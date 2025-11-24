import requests
from datetime import datetime, timezone, timedelta
from config.settings import BUSINESS_UNIT_ID


def fetch_all_mails(access_token, fields="id,name,subject,createdAt"):
    """Fetch all emails without date filtering"""
    try:
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID
        }
        
        all_mails = []
        url = "https://pi.pardot.com/api/v5/objects/list-emails"
        params = {"fields": fields, "limit": 200}
        
        while url:
            response = requests.get(url, headers=headers, params=params if url.endswith("list-emails") else None)
            
            if response.status_code != 200:
                print(f"API Error: {response.text}")
                break

            data = response.json()
            emails = data.get("values", [])
            all_mails.extend(emails)
            url = data.get("nextPageUrl")

        return all_mails
        
    except Exception as e:
        print(f"Error in fetch_all_mails: {str(e)}")
        return []

def fetch_visitor_activities(access_token, filter_start=None, filter_end=None):
    """Fetch email visitor activities using v4 API with email_only parameter"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID
        }
        
        all_activities = []
        offset = 0
        limit = 200
        
        while True:
            params = {
                "format": "json",
                "limit": limit,
                "offset": offset,
                "sort_by": "created_at",
                "sort_order": "descending",
                "email_only": "true"
            }
            
            if filter_start:
                params["created_after"] = filter_start
            if filter_end:
                params["created_before"] = filter_end
            
            response = requests.get(
                "https://pi.pardot.com/api/visitorActivity/version/4/do/query", 
                 headers=headers, params=params
                 )
            
            if response.status_code != 200:
                print(f"API Error: {response.text}")
                break
            data = response.json()
            page_activities = data.get("result", {}).get("visitor_activity", [])

            if not page_activities:
                break

            all_activities.extend(page_activities)
            offset += limit
            
        return all_activities
        
    except Exception as e:
        print(f"Error fetching visitor activities: {str(e)}")
        return []


def _get_email_stats_internal(access_token, filter_start=None, filter_end=None):
    try:
        list_emails = fetch_all_mails(access_token)
        visitor_activities = fetch_visitor_activities(access_token, filter_start, filter_end)

        # Create email lookup dictionary
        email_lookup = {email['id']: email for email in list_emails}

        # Count stats for each email
        email_stats = {}
        unique_trackers = {}  

        for activity in visitor_activities:
            list_email_id = activity.get('list_email_id')
            activity_type = activity.get('type')
            visitor_id = activity.get('visitor_id') or activity.get('prospect_id')
            
            if list_email_id:
                if list_email_id not in email_stats:
                    email_stats[list_email_id] = {
                        'sent': 0, 'delivered': 0, 'opens': 0, 'clicks': 0,
                        'uniqueOpens': 0, 'uniqueClicks': 0,
                        'bounces': 0, 'hardBounces': 0, 'softBounces': 0, 'unsubscribes': 0
                    }
                    unique_trackers[list_email_id] = {
                        'unique_opens': set(),
                        'unique_clicks': set()
                    }
                
                if activity_type == 6:  # Email Send
                    email_stats[list_email_id]['sent'] += 1
                elif activity_type == 11:  # Email Open
                    email_stats[list_email_id]['opens'] += 1
                    if visitor_id:
                        unique_trackers[list_email_id]['unique_opens'].add(visitor_id)
                elif activity_type == 1:  # Email Click
                    email_stats[list_email_id]['clicks'] += 1
                    if visitor_id:
                        unique_trackers[list_email_id]['unique_clicks'].add(visitor_id)
                elif activity_type == 12:  # Email Click (alternative)
                    email_stats[list_email_id]['clicks'] += 1
                    if visitor_id:
                        unique_trackers[list_email_id]['unique_clicks'].add(visitor_id)
                elif activity_type == 13:  # Email Hard Bounce
                    email_stats[list_email_id]['hardBounces'] += 1
                    email_stats[list_email_id]['bounces'] += 1
                elif activity_type == 36:  # Email Soft Bounce
                    email_stats[list_email_id]['softBounces'] += 1
                    email_stats[list_email_id]['bounces'] += 1
                elif activity_type == 13:  
                    email_stats[list_email_id]['unsubscribes'] += 1

 
        for email_id in email_stats:
            if email_id in unique_trackers:
                email_stats[email_id]['uniqueOpens'] = len(unique_trackers[email_id]['unique_opens'])
                email_stats[email_id]['uniqueClicks'] = len(unique_trackers[email_id]['unique_clicks'])
          
            email_stats[email_id]['delivered'] = email_stats[email_id]['sent'] - email_stats[email_id]['bounces']

       
        results = []
        for email_id, stats in email_stats.items():
            email_info = email_lookup.get(email_id)
            
            
            if email_info:
                results.append({
                    "id": str(email_id),
                    "name": email_info.get('name', 'Unknown'),
                    "subject": email_info.get('subject', ''),
                    "createdat": email_info.get('createdAt', ''),
                    "stats": stats
                })
        
        return results
        
    except Exception as e:
        print(f"Error in get_email_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return []
def get_email_stats(access_token, filter_type=None, start_date=None, end_date=None):
    """Main function to get email statistics with date filtering"""
    try:
        
        now = datetime.now(timezone.utc)
        
        if filter_type == "custom" and start_date and end_date:
            filter_start = datetime.fromisoformat(start_date.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            filter_end = datetime.fromisoformat(end_date.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
        elif filter_type == "last_7_days":
            filter_start = (now - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
            filter_end = now.strftime('%Y-%m-%d %H:%M:%S')
        elif filter_type == "last_30_days":
            filter_start = (now - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
            filter_end = now.strftime('%Y-%m-%d %H:%M:%S')
        elif filter_type == "last_3_months":
            filter_start = (now - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
            filter_end = now.strftime('%Y-%m-%d %H:%M:%S')
        elif filter_type == "last_6_months":
            filter_start = (now - timedelta(days=180)).strftime('%Y-%m-%d %H:%M:%S')
            filter_end = now.strftime('%Y-%m-%d %H:%M:%S')
        else:
           
            filter_start = None
            filter_end = None
        
        return _get_email_stats_internal(access_token, filter_start, filter_end)
        
    except Exception as e:
        print(f"Error in get_email_stats: {str(e)}")
        return []