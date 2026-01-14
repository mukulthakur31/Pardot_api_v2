import requests
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from datetime import datetime, timedelta
from config.settings import BUSINESS_UNIT_ID
import json
import os



def fetch_all_activities(headers, created_after=None, created_before=None):
    """Fetch all form activities with optional date filtering"""
    all_activities = []
    limit = 200
    offset = 0
    
    while True:
        params = {
            "format": "json",
            "limit": limit,
            "offset": offset,
            "sort_by": "created_at",
            "sort_order": "descending",
            "form_only": "true"
        }
        
        # Add date filters if provided
        if created_after:
            params["created_after"] = created_after
        if created_before:
            params["created_before"] = created_before
        
        response = requests.get(
            "https://pi.pardot.com/api/visitorActivity/version/4/do/query",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            activities = data.get("result", {}).get("visitor_activity", [])
            if activities:
                all_activities.extend(activities)
                offset += limit
            else:
                break
        else:
            print(f"Error fetching activities: {response.status_code} - {response.text}")
            break
    
    return all_activities


def calculate_form_stats(form, activities_by_form, headers, prospect_cache):
    """Calculate statistics for a single form"""
    form_id = str(form["id"])
    form_activities = activities_by_form.get(form_id, [])
    
    # Activity types: 2=View, 4=Success (Form Submission), 1,6=Clicks
    views = [a for a in form_activities if int(a.get("type", 0)) == 2]
    submissions = [a for a in form_activities if int(a.get("type", 0)) == 4]
    clicks = [a for a in form_activities if int(a.get("type", 0)) in [1, 6]]
    
    def get_unique_count(activities):
        return len({a.get("visitor_id") or a.get("prospect_id") for a in activities if a.get("visitor_id") or a.get("prospect_id")})
    
    # Calculate abandonment metrics
    total_views = len(views)
    total_submissions = len(submissions)
    abandoned = total_views - total_submissions if total_views > total_submissions else 0
    abandonment_rate = (abandoned / total_views * 100) if total_views > 0 else 0
    
    # Calculate conversions: A submission is a conversion only if the prospect had no prior activities
    conversions = 0
    for submission in submissions:
        prospect_id = submission.get("prospect_id")
        if not prospect_id:
            continue
        
        submission_date = submission.get("created_at")
        if not submission_date:
            continue
        
        # Check if this prospect has any activities before this submission
        prospect_activities = prospect_cache.get(prospect_id)
        if prospect_activities is None:
            # Fetch all activities for this prospect
            params = {"format": "json", "prospect_id": prospect_id, "limit": 200}
            response = requests.get(
                "https://pi.pardot.com/api/visitorActivity/version/4/do/query",
                headers=headers, params=params
            )
            if response.status_code == 200:
                result = response.json().get("result", {})
                prospect_activities = result.get("visitor_activity", [])
                # Ensure it's a list
                if not isinstance(prospect_activities, list):
                    prospect_activities = [prospect_activities] if prospect_activities else []
                prospect_cache[prospect_id] = prospect_activities
            else:
                prospect_cache[prospect_id] = []
                prospect_activities = []
        
        # Check if any activity exists before this submission date
        has_prior_activity = any(
            isinstance(a, dict) and a.get("created_at") and a.get("created_at") < submission_date
            for a in prospect_activities
        )
        
        if not has_prior_activity:
            conversions += 1

    
    
    # Check if form is active (has activity in last 30 days)
    thirty_days_ago = datetime.now()
    recent_activities = [a for a in form_activities if a.get("created_at") and 
                        datetime.fromisoformat(a["created_at"].replace('Z', '+00:00')).replace(tzinfo=None) > (thirty_days_ago - timedelta(days=30))]
    is_active = len(recent_activities) > 0
    
    return {
        "id": form_id,
        "name": form["name"],
        "created_at": form.get("createdAt"),
        "views": total_views,
        "unique_views": get_unique_count(views),
        "submissions": total_submissions,
        "unique_submissions": get_unique_count(submissions),
        "abandoned": abandoned,
        "abandonment_rate": round(abandonment_rate, 2),
        "clicks": len(clicks),
        "unique_clicks": get_unique_count(clicks),
        "conversions": conversions,
        "is_active": is_active,
        "last_activity": max([a.get("created_at") for a in form_activities], default=None) if form_activities else None
    }


def get_form_stats(access_token, created_after=None, created_before=None):
    """Main function to get form statistics with optional date filtering"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID
        }
        
        print(f"Fetching forms and activities with headers: {headers}")
        
        def fetch_all_forms():
            all_forms = []
            limit = 200
            offset = 0
            
            while True:
                response = requests.get(
                    "https://pi.pardot.com/api/v5/objects/forms",
                    headers=headers,
                    params={"fields": "id,name,createdAt", "limit": limit, "offset": offset}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    forms = data.get("values", [])
                    if forms:
                        all_forms.extend(forms)
                        offset += limit
                    else:
                        break
                else:
                    print(f"Error fetching forms: {response.status_code} - {response.text}")
                    break
            return all_forms
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            forms_future = executor.submit(fetch_all_forms)
            activities_future = executor.submit(fetch_all_activities, headers, created_after, created_before)
            
            forms = forms_future.result()
            activities = activities_future.result()  
        
        print(f"Forms count: {len(forms) if forms else 0}")
        print(f"Activities count: {len(activities) if activities else 0}")
        print(f"Found {len(forms)} forms")
        
        # Group activities by form_id
        activities_by_form = defaultdict(list)
        for activity in activities:
            form_id = str(activity.get("form_id", "")) or str(activity.get("form", {}).get("id", ""))
            if form_id:
                activities_by_form[form_id].append(activity)
        
        print(f"Activities grouped by {len(activities_by_form)} forms")
        
        # Create prospect cache to avoid duplicate API calls
        prospect_cache = {}
        
        # Calculate stats sequentially to manage API rate limits
        form_stats = []
        for form in forms:
            try:
                stats = calculate_form_stats(form, activities_by_form, headers, prospect_cache)
                form_stats.append(stats)
            except Exception as e:
                print(f"Error calculating stats for form {form.get('id')}: {e}")
        
        # Filter out forms with no activities if date filters are applied
        if created_after or created_before:
            form_stats = [form for form in form_stats if form["views"] > 0 or form["submissions"] > 0 or form["clicks"] > 0]
        
        print(f"Calculated stats for {len(form_stats)} forms")
        
        return form_stats
    except Exception as e:
        print(f"Error in get_form_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e




def get_date_range_from_filter(filter_type):
    """Convert filter type to date range"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    if filter_type == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif filter_type == "yesterday":
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif filter_type == "last_7_days":
        start = now - timedelta(days=7)
        end = now
    elif filter_type == "last_30_days":
        start = now - timedelta(days=30)
        end = now
    elif filter_type == "this_month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif filter_type == "last_month":
        if now.month == 1:
            start = now.replace(year=now.year-1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
        else:
            start = now.replace(month=now.month-1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
    elif filter_type == "this_quarter":
        quarter_start_month = ((now.month - 1) // 3) * 3 + 1
        start = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif filter_type == "this_year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:
        return None, None
    
    return start.isoformat(), end.isoformat()


def get_form_abandonment_analysis(access_token, created_after=None, created_before=None):
    """Analyze form abandonment patterns and issues"""
    try:
        form_stats = get_form_stats(access_token, created_after, created_before)
        return get_form_abandonment_analysis_from_cache(form_stats)
    except Exception as e:
        print(f"Error in get_form_abandonment_analysis: {str(e)}")
        raise e

def get_form_abandonment_analysis_from_cache(form_stats):
    """Analyze form abandonment using cached form stats"""
    # Categorize forms by abandonment rate
    high_abandonment = [f for f in form_stats if f["abandonment_rate"] > 70 and f["views"] > 10]
    medium_abandonment = [f for f in form_stats if 40 <= f["abandonment_rate"] <= 70 and f["views"] > 5]
    low_abandonment = [f for f in form_stats if f["abandonment_rate"] < 40 and f["views"] > 0]
    
    # Calculate overall metrics
    total_views = sum(f["views"] for f in form_stats)
    total_submissions = sum(f["submissions"] for f in form_stats)
    total_abandoned = sum(f["abandoned"] for f in form_stats)
    
    return {
        "summary": {
            "total_forms": len(form_stats),
            "total_views": total_views,
            "total_submissions": total_submissions,
            "total_abandoned": total_abandoned,
            "overall_abandonment_rate": round((total_abandoned / total_views * 100), 2) if total_views > 0 else 0,
            "overall_conversion_rate": round((total_submissions / total_views * 100), 2) if total_views > 0 else 0
        },
        "categories": {
            "high_abandonment": {
                "count": len(high_abandonment),
                "threshold": ">70%",
                "forms": high_abandonment
            },
            "medium_abandonment": {
                "count": len(medium_abandonment),
                "threshold": "40-70%",
                "forms": medium_abandonment
            },
            "low_abandonment": {
                "count": len(low_abandonment),
                "threshold": "<40%",
                "forms": low_abandonment
            }
        },
        "insights": {
            "forms_needing_attention": len(high_abandonment),
            "avg_abandonment_rate": round(sum(f["abandonment_rate"] for f in form_stats) / len(form_stats), 2) if form_stats else 0,
            "best_performing_form": min([f for f in form_stats if f["views"] > 0], key=lambda x: x["abandonment_rate"]) if [f for f in form_stats if f["views"] > 0] else None,
            "worst_performing_form": max([f for f in form_stats if f["views"] > 0], key=lambda x: x["abandonment_rate"]) if [f for f in form_stats if f["views"] > 0] else None
        }
    }




def get_active_inactive_forms(access_token):
    """Get categorized active and inactive forms"""
    try:
        form_stats = get_form_stats(access_token)
        return get_active_inactive_forms_from_cache(form_stats)
    except Exception as e:
        print(f"Error in get_active_inactive_forms: {str(e)}")
        raise e

def get_active_inactive_forms_from_cache(form_stats):
    """Get active/inactive forms using cached form stats"""
    active_forms = [form for form in form_stats if form["is_active"]]
    inactive_forms = [form for form in form_stats if not form["is_active"]]
    
    return {
        "active_forms": {
            "count": len(active_forms),
            "forms": active_forms
        },
        "inactive_forms": {
            "count": len(inactive_forms),
            "forms": inactive_forms
        },
        "summary": {
            "total_forms": len(form_stats),
            "active_percentage": round((len(active_forms) / len(form_stats) * 100), 2) if form_stats else 0,
            "total_conversions_active": sum(f["conversions"] for f in active_forms),
            "total_conversions_inactive": sum(f["conversions"] for f in inactive_forms)
        }
    }