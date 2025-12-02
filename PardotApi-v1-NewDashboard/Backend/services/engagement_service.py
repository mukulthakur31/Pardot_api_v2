import requests
from config.settings import BUSINESS_UNIT_ID

class EngagementServiceError(Exception):
    """Custom exception for engagement service errors"""
    pass

def _fetch_all_programs(headers):
    """Fetch all engagement programs with pagination"""
    all_programs = []
    offset = 0
    limit = 200
    
    while True:
        params = {
            "fields": "id,name,status,isDeleted,createdAt,updatedAt,description,folderId",
            "limit": limit,
            "offset": offset
        }
        
        response = requests.get(
            "https://pi.pardot.com/api/v5/objects/engagement-studio-programs",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise EngagementServiceError(f"API request failed: {response.status_code} - {response.text}")
        
        data = response.json()
        programs = data.get("values", [])
        
        if not programs:
            break
            
        all_programs.extend(programs)
        
        if len(programs) < limit:
            break
            
        offset += limit
    
    return all_programs

def get_engagement_programs_analysis(access_token):
    """Get engagement programs data with analysis"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID
        }
        
        programs = _fetch_all_programs(headers)
        
        # Categorize programs
        active_programs = [p for p in programs if p.get("status") == "Running" and not p.get("isDeleted")]
        inactive_programs = [p for p in programs if p.get("status") != "Running" or p.get("isDeleted")]
        paused_programs = [p for p in programs if p.get("status") == "Paused" and not p.get("isDeleted")]
        deleted_programs = [p for p in programs if p.get("isDeleted")]
        
        return {
            "summary": {
                "total_programs": len(programs),
                "active_count": len(active_programs),
                "inactive_count": len(inactive_programs),
                "paused_count": len(paused_programs),
                "deleted_count": len(deleted_programs)
            },
            "active_programs": active_programs,
            "inactive_programs": inactive_programs,
            "paused_programs": paused_programs,
            "deleted_programs": deleted_programs
        }
    except Exception as e:
        raise EngagementServiceError(f"Failed to fetch engagement programs: {str(e)}") from e