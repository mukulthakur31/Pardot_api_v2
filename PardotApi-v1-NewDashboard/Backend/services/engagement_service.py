import requests
from config.settings import BUSINESS_UNIT_ID

def get_engagement_programs_analysis(access_token):
    """Analyze engagement programs for completion rates and entries"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID
        }
        
        # Fetch engagement programs
        programs_response = requests.get(
            "https://pi.pardot.com/api/v5/objects/engagement-studio-programs",
            headers=headers,
            params={"fields": "id,name,status,isDeleted,createdAt,updatedAt,description,folderId", "limit": 200}
        )
        
        if programs_response.status_code != 200:
            raise Exception(f"Error fetching engagement programs: {programs_response.text}")
        
        programs = programs_response.json().get("values", [])
        
        # Analyze program performance
        low_completion_programs = []
        no_entry_programs = []
        active_programs = [p for p in programs if p.get("status") == "Running" and not p.get("isDeleted")]
        inactive_programs = [p for p in programs if p.get("status") != "Running" or p.get("isDeleted")]
        
        # Categorize programs
        for program in programs:
            if program.get("status") == "Paused":
                no_entry_programs.append(program)
            elif program.get("isDeleted"):
                low_completion_programs.append(program)
        
        return {
            "summary": {
                "total_programs": len(programs),
                "active_count": len(active_programs),
                "inactive_count": len(inactive_programs),
                "low_completion_count": len(low_completion_programs),
                "no_entry_count": len(no_entry_programs)
            },
            "active_programs": active_programs,
            "inactive_programs": inactive_programs,
            "low_completion_programs": low_completion_programs,
            "no_entry_programs": no_entry_programs
        }
    except Exception as e:
        print(f"Error in get_engagement_programs_analysis: {str(e)}")
        raise e

def get_engagement_programs_performance(access_token):
    """Get detailed performance metrics for engagement programs"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID
        }
        
        # Fetch engagement program statistics
        stats_response = requests.get(
            "https://pi.pardot.com/api/v5/objects/engagement-studio-programs",
            headers=headers,
            params={"fields": "id,name,status,isDeleted,createdAt,updatedAt,description,folderId", "limit": 200}
        )
        
        if stats_response.status_code != 200:
            raise Exception(f"Error fetching program statistics: {stats_response.text}")
        
        programs = stats_response.json().get("values", [])
        
        # Build performance data with available fields
        performance_data = []
        for program in programs:
            performance_data.append({
                "id": program["id"],
                "name": program["name"],
                "status": program.get("status"),
                "is_deleted": program.get("isDeleted", False),
                "created_at": program.get("createdAt"),
                "updated_at": program.get("updatedAt"),
                "description": program.get("description"),
                "folder_id": program.get("folderId")
            })
        
        top_performers = performance_data[:10]
        
        return {
            "performance_summary": {
                "total_programs": len(programs),
                "note": "Detailed metrics require additional API calls"
            },
            "all_programs": performance_data,
            "top_performers": top_performers
        }
    except Exception as e:
        print(f"Error in get_engagement_programs_performance: {str(e)}")
        raise e