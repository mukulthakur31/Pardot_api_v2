import requests
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from datetime import datetime, timedelta
from config.settings import BUSINESS_UNIT_ID
import json
import os

def fetch_all_activities(headers, created_after=None, created_before=None):
    """Fetch all landing page activities with optional date filtering"""
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
            "landing_page_only": "true"
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

def calculate_landing_page_stats(page, activities_by_page):
    """Calculate statistics for a single landing page"""
    page_id = str(page["id"])
    page_activities = activities_by_page.get(page_id, [])
    
    # Activity types: 2=View, 4=Success (Form Submission), 1,6=Clicks
    views = [a for a in page_activities if int(a.get("type", 0)) == 2]
    submissions = [a for a in page_activities if int(a.get("type", 0)) == 4]
    clicks = [a for a in page_activities if int(a.get("type", 0)) in [1, 6]]
    
    # Check if landing page is active (has activity in last 3 months)
    three_months_ago = datetime.now() - timedelta(days=90)
    recent_activities = [a for a in page_activities if a.get("created_at") and 
                        datetime.fromisoformat(a["created_at"].replace('Z', '+00:00')) > three_months_ago]
    is_active = len(recent_activities) > 0
    
    return {
        "id": page_id,
        "name": page["name"],
        "created_at": page.get("createdAt"),
        "url": page.get("url") or page.get("vanityUrl") or "No URL",
        "form_id": page.get("formId"),
        "views": len(views),
        "submissions": len(submissions),
        "clicks": len(clicks),
        "total_activities": len(page_activities),
        "recent_activities": len(recent_activities),
        "is_active": is_active,
        "last_activity": max([a.get("created_at") for a in page_activities], default=None) if page_activities else None
    }

def get_landing_page_stats(access_token, created_after=None, created_before=None):
    """Get landing page statistics with optional date filtering"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID
        }
        
        print("Fetching landing pages and activities...")
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            pages_future = executor.submit(
                requests.get,
                "https://pi.pardot.com/api/v5/objects/landing-pages",
                headers=headers,
                params={"fields": "id,name,url,vanityUrl,formId,isDeleted,createdAt", "limit": 200}
            )
            activities_future = executor.submit(fetch_all_activities, headers, created_after, created_before)
            
            pages_response = pages_future.result()
            activities = activities_future.result()
        
        if pages_response.status_code != 200:
            raise Exception(f"Error fetching landing pages: {pages_response.text}")
        
        pages = pages_response.json().get("values", [])
        # Filter out deleted pages
        pages = [p for p in pages if not p.get('isDeleted')]
        
        print(f"Found {len(pages)} active landing pages")
        print(f"Found {len(activities)} visitor activities")
        
        # Group activities by landing page ID
        activities_by_page = defaultdict(list)
        for activity in activities:
            page_id = str(activity.get("landing_page_id", "")) or str(activity.get("landing_page", {}).get("id", ""))
            if page_id:
                activities_by_page[page_id].append(activity)
        
        # Calculate stats for each landing page
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(calculate_landing_page_stats, page, activities_by_page) for page in pages]
            page_stats = [future.result() for future in futures]
        
        # Filter out pages with no activities if date filters are applied
        if created_after or created_before:
            page_stats = [page for page in page_stats if page["views"] > 0 or page["submissions"] > 0 or page["clicks"] > 0]
        
        # Categorize pages as active/inactive
        active_pages = [page for page in page_stats if page["is_active"]]
        inactive_pages = [page for page in page_stats if not page["is_active"]]
        
        return {
            "criteria": "Landing pages with visitor activity (views, clicks, submissions) in last 3 months are considered active",
            "active_pages": {
                "count": len(active_pages),
                "description": "Pages with visitor activity in the last 3 months",
                "pages": active_pages
            },
            "inactive_pages": {
                "count": len(inactive_pages),
                "description": "Pages with no visitor activity in the last 3 months",
                "pages": inactive_pages
            },
            "summary": {
                "total_pages": len(page_stats),
                "active_percentage": round((len(active_pages) / len(page_stats) * 100), 2) if page_stats else 0,
                "inactive_percentage": round((len(inactive_pages) / len(page_stats) * 100), 2) if page_stats else 0,
                "total_activities": sum(p["total_activities"] for p in page_stats),
                "total_recent_activities": sum(p["recent_activities"] for p in active_pages)
            }
        }
        
    except Exception as e:
        print(f"Error in get_landing_page_stats: {str(e)}")
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


