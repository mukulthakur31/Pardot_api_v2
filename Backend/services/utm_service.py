import requests
from config.settings import BUSINESS_UNIT_ID
from cache import get_cached_data, set_cached_data

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
    """Analyze UTM parameters for missing values only"""
    utm_fields = ["utm_campaign__c", "utm_medium__c", "utm_source__c", "utm_term__c"]
    audit_results = []
    
    for prospect in prospects_data:
        prospect_id = prospect.get("id")
        email = prospect.get("email")
        missing_fields = []
        
        for field in utm_fields:
            value = prospect.get(field)
            
            if value is None or str(value).strip() == "":
                missing_fields.append(field)
        
        if missing_fields:
            audit_results.append({
                "prospect_id": prospect_id,
                "email": email,
                "missing_fields": missing_fields
            })
    
    return audit_results

def format_utm_issues_for_export(utm_issues):
    """Format UTM issues for Google Sheets export with Yes/No flags for missing fields only"""
    formatted_data = []
    
    for issue in utm_issues:
        row = {
            "Prospect ID": issue.get("prospect_id", ""),
            "Email": issue.get("email", ""),
            "UTM Campaign Missing": "Yes" if "utm_campaign__c" in issue.get("missing_fields", []) else "No",
            "UTM Medium Missing": "Yes" if "utm_medium__c" in issue.get("missing_fields", []) else "No",
            "UTM Source Missing": "Yes" if "utm_source__c" in issue.get("missing_fields", []) else "No",
            "UTM Term Missing": "Yes" if "utm_term__c" in issue.get("missing_fields", []) else "No"
        }
        formatted_data.append(row)
    
    return formatted_data

def get_utm_analysis(access_token):
    """Main function to run UTM audit"""
    try:
        # Input validation
        if not access_token or len(access_token.strip()) == 0:
            raise ValueError("Invalid access token")
        
        cache_key = f"utm_prospects:{access_token[:20]}"
        
        # Check cache first for prospects data
        cached_prospects = get_cached_data(cache_key)
        if cached_prospects:
            print(f"📦 UTM PROSPECTS DATA: Retrieved from CACHE - Key: {cache_key}")
            prospects_data = cached_prospects
        else:
            print(f"🌐 UTM PROSPECTS DATA: Fetching from API - Key: {cache_key}")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID,
                "Content-Type": "application/json"
            }
            
            prospects_data = get_prospects_with_utm(headers)
            
            # Cache prospects data for 30 minutes
            set_cached_data(cache_key, prospects_data, ttl=1800)
            print(f"💾 UTM PROSPECTS DATA: Cached for 30 minutes - Key: {cache_key}")
        
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


               