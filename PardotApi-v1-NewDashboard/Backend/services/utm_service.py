import requests
import datetime
from dateutil import parser
from config.settings import BUSINESS_UNIT_ID

def get_prospects_with_utm(headers):
    """Get prospects with UTM fields using nextPageUrl pagination"""
    all_prospects = []
    url = "https://pi.pardot.com/api/v5/objects/prospects"
    params = {
        "fields": "id,email,utm_campaign__c,utm_medium__c,utm_source__c,utm_term__c",
        "limit": 200
    }
    
    while url:
        response = requests.get(url, headers=headers, params=params if url.endswith("prospects") else None)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get prospects: {response.status_code} - {response.text}")
        
        data = response.json()
        prospects = data.get("values", [])
        all_prospects.extend(prospects)
        
        url = data.get("nextPageUrl")
        params = None  # Clear params for subsequent requests
        
        # Limit to prevent timeout
        if len(all_prospects) >= 10000:
            break
    
    return all_prospects

def analyze_utm_parameters(prospects_data):
    """Analyze UTM parameters for missing/invalid values"""
    allowed_values = {
        "utm_source__c": ["google", "linkedin", "facebook"],
        "utm_medium__c": ["cpc", "email", "social"],
        "utm_campaign__c": ["spring_sale", "newsletter", "webinar"]
    }
    
    utm_fields = ["utm_campaign__c", "utm_medium__c", "utm_source__c", "utm_term__c"]
    audit_results = []
    
    for prospect in prospects_data:
        prospect_id = prospect.get("id")
        email = prospect.get("email")
        missing_fields = []
        invalid_fields = []
        
        for field in utm_fields:
            value = prospect.get(field)
            
            if value is None or str(value).strip() == "":
                missing_fields.append(field)
            else:
                value_str = str(value).strip().lower()
                if field in allowed_values and value_str not in allowed_values[field]:
                    invalid_fields.append(field)
        
        if missing_fields or invalid_fields:
            audit_results.append({
                "prospect_id": prospect_id,
                "email": email,
                "missing_fields": missing_fields,
                "invalid_fields": invalid_fields
            })
    
    return audit_results

def format_utm_issues_for_export(utm_issues):
    """Format UTM issues for Google Sheets export with Yes/No flags"""
    formatted_data = []
    
    for issue in utm_issues:
        row = {
            "Prospect ID": issue.get("prospect_id", ""),
            "Email": issue.get("email", ""),
            "UTM Campaign Missing": "Yes" if "utm_campaign__c" in issue.get("missing_fields", []) else "No",
            "UTM Medium Missing": "Yes" if "utm_medium__c" in issue.get("missing_fields", []) else "No",
            "UTM Source Missing": "Yes" if "utm_source__c" in issue.get("missing_fields", []) else "No",
            "UTM Term Missing": "Yes" if "utm_term__c" in issue.get("missing_fields", []) else "No",
            "UTM Campaign Invalid": "Yes" if "utm_campaign__c" in issue.get("invalid_fields", []) else "No",
            "UTM Medium Invalid": "Yes" if "utm_medium__c" in issue.get("invalid_fields", []) else "No",
            "UTM Source Invalid": "Yes" if "utm_source__c" in issue.get("invalid_fields", []) else "No"
        }
        formatted_data.append(row)
    
    return formatted_data

def get_utm_analysis(access_token):
    """Main function to run UTM audit"""
    try:
        # Input validation
        if not access_token or len(access_token.strip()) == 0:
            raise ValueError("Invalid access token")
            
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID,
            "Content-Type": "application/json"
        }
        
        prospects_data = get_prospects_with_utm(headers)
        audit_results = analyze_utm_parameters(prospects_data)
        
        return {
            "utm_analysis": {
                "total_prospects_analyzed": len(prospects_data),
                "prospects_with_utm_issues": len(audit_results),
                "utm_issues": audit_results[:20],
                "all_utm_issues": audit_results,
                "export_data": format_utm_issues_for_export(audit_results),
                "summary": f"Analyzed {len(prospects_data)} prospects, found {len(audit_results)} with UTM issues"
            }
        }
        
    except Exception:
        return {
            "utm_analysis": {
                "status": "ERROR",
                "error": "Analysis failed",
                "total_prospects_analyzed": 0,
                "prospects_with_utm_issues": 0,
                "utm_issues": [],
                "summary": "Analysis failed"
            }
        }

# ===== CAMPAIGN ENGAGEMENT CHECKER =====

def fetch_all_campaigns(headers):
    """Fetch all Pardot campaigns"""
    all_campaigns = []
    url = "https://pi.pardot.com/api/v5/objects/campaigns"
    params = {"fields": "id,name,createdAt,updatedAt,cost", "limit": 200}
    
    while url:
        response = requests.get(url, headers=headers, params=params if url.endswith("campaigns") else None)
        if response.status_code != 200:
            raise Exception(f"Failed to get campaigns: {response.status_code} - {response.text}")
        
        data = response.json()
        all_campaigns.extend(data.get("values", []))
        url = data.get("nextPageUrl")
        params = None
    
    return all_campaigns

def fetch_campaign_assets(headers, endpoint, asset_type):
    """Generic function to fetch campaign assets"""
    assets = []
    url = f"https://pi.pardot.com/api/v5/objects/{endpoint}"
    params = {"fields": "id,campaignId,createdAt", "limit": 200}
    
    while url:
        response = requests.get(url, headers=headers, params=params if url.endswith(endpoint) else None)
        if response.status_code == 200:
            data = response.json()
            assets.extend(data.get("values", []))
            url = data.get("nextPageUrl")
            params = None
        else:
            break
    return assets

def fetch_all_campaign_related_data(headers):
    """Fetch all campaign-related assets"""
    endpoints = {
        "prospects": "prospects",
        "emails": "list-emails", 
        "forms": "forms",
        "landing_pages": "landing-pages",
        "custom_redirects": "custom-redirects",
        "files": "files"
    }
    
    all_data = {}
    for asset_type, endpoint in endpoints.items():
        all_data[asset_type] = fetch_campaign_assets(headers, endpoint, asset_type)
    
    return all_data

def check_campaign_activity_with_data(campaign_id, all_data, months_back):
    """Check if campaign has activity in timeframe"""
    try:
        cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=int(months_back) * 30)
        asset_types = ["prospects", "emails", "forms", "landing_pages", "custom_redirects", "files"]
        
        for asset_type in asset_types:
            for item in all_data[asset_type]:
                if str(item.get("campaignId")) == str(campaign_id):
                    try:
                        created_date = parser.parse(item.get("createdAt"))
                        if created_date > cutoff_date:
                            return "active"
                    except:
                        continue
        return "inactive"
    except:
        return "inactive"

def get_campaign_engagement_analysis(months_back="6"):
    """Analyze campaign engagement with timeframe filter"""
    try:
        # Input validation
        try:
            months_int = int(months_back)
            if months_int < 1 or months_int > 24:
                months_back = "6"  # Default to 6 months if invalid
        except (ValueError, TypeError):
            months_back = "6"
            
        from flask import session
        access_token = session.get('access_token')
        if not access_token:
            raise Exception("No access token available")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID,
            "Content-Type": "application/json"
        }
        
        campaigns = fetch_all_campaigns(headers)
        all_data = fetch_all_campaign_related_data(headers)
        
        active_campaigns = []
        inactive_campaigns = []
        
        for campaign in campaigns:
            status = check_campaign_activity_with_data(campaign.get("id"), all_data, months_back)
            
            campaign_data = {
                "id": campaign.get("id"),
                "name": campaign.get("name", "Unknown"),
                "created_at": campaign.get("createdAt"),
                "updated_at": campaign.get("updatedAt"),
                "cost": campaign.get("cost", 0),
                "status": status
            }
            
            if status == "active":
                active_campaigns.append(campaign_data)
            else:
                inactive_campaigns.append(campaign_data)
        
        # Format export data
        export_data = [{
            "Campaign ID": c["id"],
            "Campaign Name": c["name"],
            "Status": c["status"].title(),
            "Created Date": c["created_at"],
            "Last Updated": c["updated_at"],
            "Cost": c["cost"]
        } for c in active_campaigns + inactive_campaigns]
        
        return {
            "campaign_engagement_analysis": {
                "total_campaigns_analyzed": len(campaigns),
                "active_campaigns_count": len(active_campaigns),
                "inactive_campaigns_count": len(inactive_campaigns),
                "active_campaigns": active_campaigns,
                "inactive_campaigns": inactive_campaigns,
                "export_data": export_data,
                "months_analyzed": months_back,
                "summary": f"Total: {len(campaigns)} campaigns - {len(active_campaigns)} active, {len(inactive_campaigns)} inactive (based on last {months_back} months activity)",
                "breakdown": {
                    "active_percentage": round((len(active_campaigns) / len(campaigns)) * 100, 1) if campaigns else 0,
                    "inactive_percentage": round((len(inactive_campaigns) / len(campaigns)) * 100, 1) if campaigns else 0
                }
            }
        }
        
    except Exception:
        return {
            "campaign_engagement_analysis": {
                "status": "ERROR",
                "error": "Analysis failed",
                "total_campaigns_analyzed": 0,
                "active_campaigns_count": 0,
                "inactive_campaigns_count": 0,
                "active_campaigns": [],
                "inactive_campaigns": [],
                "export_data": [],
                "summary": "Analysis failed"
            }
        }