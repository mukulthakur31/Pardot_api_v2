import requests
from config.settings import BUSINESS_UNIT_ID
<<<<<<< HEAD
from datetime import datetime, timedelta
from cache import get_cached_data, set_cached_data

class EngagementHealthAuditor:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID
        }
    
    def analyze_engagement_health(self):
        """Comprehensive engagement program health analysis"""
        try:
            programs = self._fetch_all_programs()
            
            # Categorize programs
            all_programs = programs
            active_programs = [p for p in programs if p.get('status') == 'Running' and not p.get('isDeleted')]
            inactive_programs = [p for p in programs if p.get('status') != 'Running' or p.get('isDeleted')]
            low_performance = [p for p in programs if p.get('isDeleted')]
            no_entries = [p for p in programs if p.get('status') == 'Paused']
            
            return {
                "summary": {
                    "total_programs": len(all_programs),
                    "active_count": len(active_programs),
                    "inactive_count": len(inactive_programs),
                    "low_performance_count": len(low_performance),
                    "no_entries_count": len(no_entries)
                },
                "all_programs": all_programs,
                "active_programs": active_programs,
                "inactive_programs": inactive_programs,
                "low_performance": low_performance,
                "no_entries": no_entries
            }
        except Exception as e:
            raise Exception(f"Error in engagement health analysis: {str(e)}")
    
    def _fetch_all_programs(self):
        """Fetch all engagement programs with pagination"""
        all_programs = []
        offset = 0
        limit = 200
        
        while True:
            response = requests.get(
                "https://pi.pardot.com/api/v5/objects/engagement-studio-programs",
                headers=self.headers,
                params={
                    "fields": "id,name,status,isDeleted,createdAt,updatedAt,description,folderId",
                    "limit": limit,
                    "offset": offset
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Error fetching programs: {response.text}")
            
            data = response.json()
            programs = data.get("values", [])
            
            if not programs:
                break
            
            all_programs.extend(programs)
            
            if len(programs) < limit:
                break
            
            offset += limit
        
        return all_programs

logger = logging.getLogger(__name__)
=======
>>>>>>> f378ea016ddbaa9c4f5971c5d82480a01750cb70

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
        cache_key = f"engagement_raw_data:{access_token[:20]}"
        
        # Check cache first for raw programs data
        cached_programs = get_cached_data(cache_key)
        if cached_programs:
            print(f"📦 ENGAGEMENT RAW DATA: Retrieved from CACHE - Key: {cache_key}")
            programs = cached_programs
        else:
            print(f"🌐 ENGAGEMENT RAW DATA: Fetching from API - Key: {cache_key}")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID
            }
            
            programs = _fetch_all_programs(headers)
            
            # Cache raw programs data for 30 minutes
            set_cached_data(cache_key, programs, ttl=1800)
            print(f"💾 ENGAGEMENT RAW DATA: Cached for 30 minutes - Key: {cache_key}")
        
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