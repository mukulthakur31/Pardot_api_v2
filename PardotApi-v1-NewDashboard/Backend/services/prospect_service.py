import requests
from datetime import datetime, timedelta
from config.settings import BUSINESS_UNIT_ID
from .prospect_filter_service import filter_prospects

def fetch_all_prospects(headers):
    """Fetch all prospects with pagination"""
    all_prospects = []
    url = "https://pi.pardot.com/api/v5/objects/prospects"
    params = {
        "fields": "id,email,firstName,lastName,country,jobTitle,score,grade,lastActivityAt,createdAt",
        "limit": 1000
    }
    
    while url:
        print(f"Fetching prospects from: {url}")
        response = requests.get(url, headers=headers, params=params if url.endswith("prospects") else None)
        
        if response.status_code != 200:
            print(f"Error fetching prospects: {response.status_code} - {response.text}")
            break
            
        data = response.json()
        prospects = data.get("values", [])
        all_prospects.extend(prospects)
        
        url = data.get("nextPageUrl")
        params = None  # Clear params for subsequent requests
        
        # Limit to prevent timeout (remove this in production)
        if len(all_prospects) >= 10000:
            break
    
    return all_prospects

def find_duplicate_prospects(prospects):
    """Find prospects with duplicate email addresses"""
    email_groups = {}
    
    for prospect in prospects:
        email = prospect.get('email', '').lower().strip()
        if email:
            if email not in email_groups:
                email_groups[email] = []
            email_groups[email].append(prospect)
    
    duplicates = []
    for email, group in email_groups.items():
        if len(group) > 1:
            duplicates.append({
                "email": email,
                "count": len(group),
                "prospects": [{
                    "id": p.get('id'),
                    "firstName": p.get('firstName', ''),
                    "lastName": p.get('lastName', ''),
                    "createdAt": p.get('createdAt', '')
                } for p in group]
            })
    
    return duplicates

def find_inactive_prospects(prospects):
    """Find prospects with no activity in 90+ days"""
    cutoff_date = datetime.now() - timedelta(days=90)
    inactive = []
    
    for prospect in prospects:
        last_activity = prospect.get('lastActivityAt')
        if not last_activity:
            # No activity recorded
            inactive.append({
                "id": prospect.get('id'),
                "email": prospect.get('email', ''),
                "firstName": prospect.get('firstName', ''),
                "lastName": prospect.get('lastName', ''),
                "lastActivityAt": None,
                "daysSinceActivity": "Never"
            })
        else:
            try:
                # Parse the date string
                activity_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                if activity_date < cutoff_date:
                    days_inactive = (datetime.now() - activity_date.replace(tzinfo=None)).days
                    inactive.append({
                        "id": prospect.get('id'),
                        "email": prospect.get('email', ''),
                        "firstName": prospect.get('firstName', ''),
                        "lastName": prospect.get('lastName', ''),
                        "lastActivityAt": last_activity,
                        "daysSinceActivity": days_inactive
                    })
            except:
                # If date parsing fails, consider as inactive
                inactive.append({
                    "id": prospect.get('id'),
                    "email": prospect.get('email', ''),
                    "firstName": prospect.get('firstName', ''),
                    "lastName": prospect.get('lastName', ''),
                    "lastActivityAt": last_activity,
                    "daysSinceActivity": "Unknown"
                })
    
    return inactive

def find_missing_critical_fields(prospects):
    """Find prospects missing critical fields"""
    missing = []
    
    for prospect in prospects:
        missing_fields = []
        
        if not prospect.get('country'):
            missing_fields.append('country')
        if not prospect.get('jobTitle'):
            missing_fields.append('jobTitle')
        if not prospect.get('firstName'):
            missing_fields.append('firstName')
        if not prospect.get('lastName'):
            missing_fields.append('lastName')
        
        if missing_fields:
            missing.append({
                "id": prospect.get('id'),
                "email": prospect.get('email', ''),
                "firstName": prospect.get('firstName', ''),
                "lastName": prospect.get('lastName', ''),
                "missingFields": missing_fields
            })
    
    return missing

def find_scoring_inconsistencies(prospects):
    """Find prospects with scoring inconsistencies"""
    inconsistencies = []
    
    for prospect in prospects:
        score = prospect.get('score', 0)
        last_activity = prospect.get('lastActivityAt')
        
        # High score but no recent activity (potential issue)
        if score > 50 and not last_activity:
            inconsistencies.append({
                "id": prospect.get('id'),
                "email": prospect.get('email', ''),
                "firstName": prospect.get('firstName', ''),
                "lastName": prospect.get('lastName', ''),
                "score": score,
                "issue": "High score but no activity recorded",
                "lastActivityAt": last_activity
            })
        elif score > 75:
            # Check if high score aligns with recent activity
            try:
                if last_activity:
                    activity_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                    days_since = (datetime.now() - activity_date.replace(tzinfo=None)).days
                    
                    if days_since > 30:
                        inconsistencies.append({
                            "id": prospect.get('id'),
                            "email": prospect.get('email', ''),
                            "firstName": prospect.get('firstName', ''),
                            "lastName": prospect.get('lastName', ''),
                            "score": score,
                            "issue": f"High score but no activity in {days_since} days",
                            "lastActivityAt": last_activity
                        })
            except:
                pass
    
    return inconsistencies

def analyze_grading_setup(prospects):
    """Analyze grading distribution and setup"""
    grade_distribution = {}
    total_graded = 0
    
    for prospect in prospects:
        grade = prospect.get('grade')
        if grade:
            total_graded += 1
            if grade not in grade_distribution:
                grade_distribution[grade] = 0
            grade_distribution[grade] += 1
    
    # Calculate percentages
    grade_percentages = {}
    if total_graded > 0:
        for grade, count in grade_distribution.items():
            grade_percentages[grade] = round((count / total_graded) * 100, 2)
    
    return {
        "total_prospects": len(prospects),
        "graded_prospects": total_graded,
        "ungraded_prospects": len(prospects) - total_graded,
        "grading_coverage": round((total_graded / len(prospects)) * 100, 2) if prospects else 0,
        "grade_distribution": grade_distribution,
        "grade_percentages": grade_percentages
    }

def analyze_prospect_health(prospects, headers):
    """Analyze prospect database health"""
    # Initialize counters
    duplicates = find_duplicate_prospects(prospects)
    inactive_prospects = find_inactive_prospects(prospects)
    missing_fields = find_missing_critical_fields(prospects)
    
    return {
        "total_prospects": len(prospects),
        "duplicates": {
            "count": len(duplicates),
            "details": duplicates
        },
        "inactive_prospects": {
            "count": len(inactive_prospects),
            "details": inactive_prospects
        },
        "missing_fields": {
            "count": len(missing_fields),
            "details": missing_fields
        },
        "all_prospects": prospects  # Cache all prospects for filtering
    }

def get_prospect_health(access_token):
    """Main function to get prospect health analysis"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID
        }
        
        prospects = fetch_all_prospects(headers)
        health_data = analyze_prospect_health(prospects, headers)
        
        return health_data
    except Exception as e:
        print(f"Error in get_prospect_health: {str(e)}")
        raise e

def get_filtered_prospects(access_token, filters):
    """Get filtered prospects based on provided filters"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID
        }
        
        # Get all prospects (this could be cached for better performance)
        prospects = fetch_all_prospects(headers)
        
        # Apply filters
        filtered_prospects = filter_prospects(prospects, filters)
        
        return {
            "total_prospects": len(prospects),
            "filtered_count": len(filtered_prospects),
            "prospects": filtered_prospects,
            "filters_applied": filters
        }
    except Exception as e:
        print(f"Error in get_filtered_prospects: {str(e)}")
        raise e