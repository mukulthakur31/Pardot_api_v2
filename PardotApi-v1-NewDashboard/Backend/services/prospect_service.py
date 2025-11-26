import requests
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from config.settings import BUSINESS_UNIT_ID

def get_prospect_health(access_token):
    """Main function to get prospect health analysis"""
    try:
        auditor = ProspectHealthAuditor(access_token, BUSINESS_UNIT_ID, "https://pi.pardot.com")
        results = auditor.run_prospect_health_audit()
        return results
    except Exception as e:
        print(f"Error in get_prospect_health: {str(e)}")
        raise e

def find_duplicate_prospects(prospects):
    """Find prospects with duplicate email addresses"""
    auditor = ProspectHealthAuditor("", "", "")
    return auditor.find_duplicate_prospects(prospects)

def find_inactive_prospects(prospects):
    """Find prospects with no activity in 90+ days"""
    auditor = ProspectHealthAuditor("", "", "")
    return auditor.find_inactive_prospects(prospects)

def find_missing_critical_fields(prospects):
    """Find prospects missing critical fields"""
    auditor = ProspectHealthAuditor("", "", "")
    return auditor.find_missing_critical_fields(prospects)

def find_scoring_issues(prospects):
    """Find prospects with scoring inconsistencies"""
    auditor = ProspectHealthAuditor("", "", "")
    return auditor.find_scoring_issues(prospects)

class ProspectHealthAuditor:
    def __init__(self, access_token, business_unit_id, instance_url):
        self.access_token = access_token
        self.business_unit_id = business_unit_id
        self.instance_url = instance_url.rstrip('/')
        self.base_url = "https://pi.pardot.com/api/v5/objects"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Pardot-Business-Unit-Id': business_unit_id,
            'Content-Type': 'application/json'
        }
        print(f"[DEBUG] Using base URL: {self.base_url}")
        print(f"[DEBUG] Business Unit ID: {business_unit_id}")
        print(f"[DEBUG] Instance URL: {instance_url}")
    
    def get_prospects(self, limit=1000, next_page_token=None, filters=None):
        """Fetch prospects from Pardot v5 API with filters"""
        url = f"{self.base_url}/prospects"
        
        # Only standard fields - custom fields are fetched separately
        fields = "id,addressOne,addressTwo,annualRevenue,campaignId,campaignParameter,salesforceCampaignId,city,comments,company,contentParameter,convertedAt,convertedFromObjectName,convertedFromObjectType,country,createdAt,createdById,salesforceAccountId,salesforceContactId,salesforceLastSync,salesforceLeadId,salesforceOwnerId,department,email,emailBouncedAt,emailBouncedReason,employees,fax,firstActivityAt,firstAssignedAt,firstName,firstReferrerQuery,firstReferrerType,firstReferrerUrl,grade,industry,isDeleted,isDoNotCall,isDoNotEmail,isEmailHardBounced,isReviewed,isStarred,jobTitle,lastActivityAt,lastName,mediumParameter,notes,optedOut,password,phone,prospectAccountId,salesforceId,salutation,score,source,sourceParameter,state,termParameter,territory,updatedAt,updatedById,userId,website,yearsInBusiness,zip,assignedToId,profileId,salesforceUrl,lifecycleStageId,recentInteraction,doNotSell"
        
        if next_page_token:
            # When using nextPageToken, only include fields and nextPageToken
            params = {
                'fields': fields,
                'nextPageToken': next_page_token
            }
        else:
            # Initial request without nextPageToken
            params = {
                'fields': fields,
                'limit': limit
            }
            
            # Apply filters if provided
            if filters:
                params.update(self.build_filter_params(filters))
        
        print(f"[DEBUG] Endpoint: {url}")
        print(f"[DEBUG] Params: {params}")
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            print(f"[DEBUG] Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"[DEBUG] Found {len(data.get('values', []))} records")
                return data
            else:
                print(f"[ERROR] Fetching prospects: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"[ERROR] Exception fetching prospects: {e}")
            return None
    
    def safe_get_value(self, prospect, key, default=''):
        """Safely get value from prospect data"""
        value = prospect.get(key, default)
        if value is None:
            return default
        return str(value).strip() if str(value).strip() else default
    
    def build_filter_params(self, filters):
        """Build minimal API parameters - filters now applied client-side"""
        params = {'limit': '1000'}  # Use max limit for efficiency
        
        # No API filters applied - all filtering done client-side
        
        return params
    
    def get_all_prospects(self, max_records=10000, filters=None):
        """Fetch all prospects once, then apply filters client-side"""
        # If we already have cached data and no filters, return cached data
        if hasattr(self, '_cached_prospects') and not filters:
            return self._cached_prospects[:max_records]
        
        all_prospects = []
        next_page_token = None
        limit = 1000
        
        # Fetch all data without problematic individual API calls
        while len(all_prospects) < max_records:
            data = self.get_prospects(limit=limit, next_page_token=next_page_token, filters=None)
            if not data or 'values' not in data:
                break
            
            prospects = data['values']
            if not prospects:
                break
            
            all_prospects.extend(prospects)
            
            # Check for next page
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
                
            if len(all_prospects) % 2000 == 0:
                print(f"[DEBUG] Fetched {len(all_prospects)} prospects so far...")
        
        # Convert prospects
        converted_prospects = []
        
        print(f"\n=== PROCESSING {len(all_prospects)} PROSPECTS ===\n")
        
        for prospect in all_prospects:
            try:
                # Safe conversion with null handling
                score_val = prospect.get('score')
                if score_val is None or str(score_val).lower() in ['none', '', 'null']:
                    score_val = 0
                else:
                    try:
                        score_val = int(float(score_val))
                    except:
                        score_val = 0
                
                prospect_id = self.safe_get_value(prospect, 'id')
                
                converted_prospects.append({
                    'id': prospect_id,
                    'email': self.safe_get_value(prospect, 'email'),
                    'firstName': self.safe_get_value(prospect, 'firstName'),
                    'lastName': self.safe_get_value(prospect, 'lastName'),
                    'company': self.safe_get_value(prospect, 'company'),
                    'country': self.safe_get_value(prospect, 'country'),
                    'jobTitle': self.safe_get_value(prospect, 'jobTitle'),
                    'lastActivityAt': self.safe_get_value(prospect, 'lastActivityAt'),
                    'score': score_val,
                    'grade': self.safe_get_value(prospect, 'grade', 'D'),
                    'createdAt': self.safe_get_value(prospect, 'createdAt'),
                    'updatedAt': self.safe_get_value(prospect, 'updatedAt'),
                    'firstAssignedAt': self.safe_get_value(prospect, 'firstAssignedAt'),
                    'firstActivityAt': self.safe_get_value(prospect, 'firstActivityAt'),
                    'isDeleted': prospect.get('isDeleted', False),
                    'isDoNotEmail': prospect.get('isDoNotEmail', False),
                    'optedOut': prospect.get('optedOut', False),
                    'isStarred': prospect.get('isStarred', False),
                    'isReviewed': prospect.get('isReviewed', False),
                    'assignedToId': prospect.get('assignedToId'),
                    'userId': prospect.get('userId'),
                    'salesforceId': prospect.get('salesforceId'),
                    'isEmailHardBounced': prospect.get('isEmailHardBounced', False),
                    'campaignId': prospect.get('campaignId')
                })
                    
            except Exception as e:
                print(f"[DEBUG] Error processing prospect: {e}")
                continue
        
        print(f"\n=== FINAL SUMMARY ===")
        print(f"Total prospects processed: {len(converted_prospects)}")
        print(f"=== END SUMMARY ===\n")
        
        # Cache the full dataset
        self._cached_prospects = converted_prospects
        
        return converted_prospects[:max_records]
    
    def find_duplicate_prospects(self, prospects):
        """Find prospects with duplicate email addresses"""
        email_counts = defaultdict(list)
        
        # Group prospects by email
        for prospect in prospects:
            email = prospect.get('email', '').lower().strip()
            if email and email != 'n/a':
                email_counts[email].append(prospect)
        
        # Find duplicates
        duplicates = []
        for email, prospect_list in email_counts.items():
            if len(prospect_list) > 1:
                duplicates.append({
                    'email': email,
                    'count': len(prospect_list),
                    'prospects': [{
                        'id': p.get('id'),
                        'firstName': p.get('firstName', ''),
                        'lastName': p.get('lastName', ''),
                        'createdAt': p.get('createdAt', '')
                    } for p in prospect_list]
                })
        
        return duplicates
    
    def find_inactive_prospects(self, prospects, days=90):
        """Find prospects with no activity in specified days"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        inactive_prospects = []
        
        for prospect in prospects:
            last_activity = prospect.get('lastActivityAt')
            if last_activity and str(last_activity).strip():
                try:
                    # Handle different date formats
                    if 'T' in str(last_activity):
                        activity_date = datetime.fromisoformat(str(last_activity).replace('Z', '+00:00'))
                    else:
                        # Make naive datetime timezone-aware
                        activity_date = datetime.strptime(str(last_activity), '%Y-%m-%d')
                        activity_date = activity_date.replace(tzinfo=timezone.utc)
                    
                    # Ensure both dates are timezone-aware
                    if activity_date.tzinfo is None:
                        activity_date = activity_date.replace(tzinfo=timezone.utc)
                    
                    if activity_date < cutoff_date:
                        days_diff = (datetime.now(timezone.utc) - activity_date).days
                        inactive_prospects.append({
                            'id': prospect.get('id'),
                            'email': prospect.get('email'),
                            'firstName': prospect.get('firstName', ''),
                            'lastName': prospect.get('lastName', ''),
                            'company': prospect.get('company', ''),
                            'lastActivityAt': str(last_activity),
                            'daysInactive': days_diff
                        })
                except Exception as e:
                    print(f"[DEBUG] Date parsing error for {prospect.get('email')}: {e}")
                    # If date parsing fails, consider as inactive
                    inactive_prospects.append({
                        'id': prospect.get('id'),
                        'email': prospect.get('email'),
                        'firstName': prospect.get('firstName', ''),
                        'lastName': prospect.get('lastName', ''),
                        'company': prospect.get('company', ''),
                        'lastActivityAt': 'Invalid date',
                        'daysInactive': 'Unknown'
                    })
            else:
                # No activity recorded
                inactive_prospects.append({
                    'id': prospect.get('id'),
                    'email': prospect.get('email'),
                    'firstName': prospect.get('firstName', ''),
                    'lastName': prospect.get('lastName', ''),
                    'company': prospect.get('company', ''),
                    'lastActivityAt': None,
                    'daysInactive': 'Never'
                })
        
        return inactive_prospects
    
    def find_missing_critical_fields(self, prospects):
        """Find prospects missing critical fields"""
        critical_fields = ['firstName', 'lastName', 'company', 'jobTitle', 'country']
        missing_fields = []
        
        for prospect in prospects:
            try:
                missing = []
                for field in critical_fields:
                    field_value = prospect.get(field, '')
                    # Check if field is empty, None, or contains placeholder values
                    if (not field_value or 
                        str(field_value).strip() == '' or 
                        str(field_value).lower().strip() in ['none', 'null', 'n/a', 'undefined']):
                        missing.append(field)
                
                if missing:
                    missing_fields.append({
                        'id': prospect.get('id', ''),
                        'email': prospect.get('email', 'N/A'),
                        'firstName': prospect.get('firstName', ''),
                        'lastName': prospect.get('lastName', ''),
                        'company': prospect.get('company', ''),
                        'missingFields': missing
                    })
            except Exception as e:
                print(f"[DEBUG] Error processing missing fields for prospect: {e}")
                continue
        
        print(f"[DEBUG] Found {len(missing_fields)} prospects with missing fields")
        return missing_fields
    
    def find_scoring_issues(self, prospects):
        """Find prospects with scoring inconsistencies"""
        scoring_issues = []
        
        for prospect in prospects:
            try:
                score = prospect.get('score', 0)
                grade = prospect.get('grade', 'D')
                last_activity = prospect.get('lastActivityAt')
                
                issues = []
                
                # Check for score/grade mismatch
                if score >= 100 and grade in ['D', 'F']:
                    issues.append('High score with low grade')
                elif score <= 10 and grade in ['A', 'B']:
                    issues.append('Low score with high grade')
                
                # Check for active prospects with very low scores
                if last_activity and score == 0:
                    issues.append('Active prospect with zero score')
                
                # Check for prospects with negative scores
                if score < 0:
                    issues.append('Negative score')
                
                # Check for prospects with extremely high scores
                if score > 1000:
                    issues.append('Unusually high score')
                
                # Check for grade without corresponding score range
                if grade == 'A' and score < 75:
                    issues.append('Grade A with score below 75')
                elif grade == 'B' and (score < 50 or score >= 75):
                    issues.append('Grade B with score outside 50-74 range')
                elif grade == 'C' and (score < 25 or score >= 50):
                    issues.append('Grade C with score outside 25-49 range')
                elif grade == 'D' and score >= 25:
                    issues.append('Grade D with score above 24')
                
                if issues:
                    scoring_issues.append({
                        'id': prospect.get('id', ''),
                        'email': prospect.get('email', 'N/A'),
                        'firstName': prospect.get('firstName', ''),
                        'lastName': prospect.get('lastName', ''),
                        'company': prospect.get('company', ''),
                        'score': score,
                        'grade': grade,
                        'lastActivityAt': last_activity,
                        'issues': issues
                    })
            except Exception as e:
                print(f"[DEBUG] Error processing scoring for prospect: {e}")
                continue
        
        print(f"[DEBUG] Found {len(scoring_issues)} prospects with scoring issues")
        return scoring_issues
    
    def run_prospect_health_audit(self, filters=None):
        """Run complete prospect health audit with client-side filters"""
        print("Starting Prospect Database Health Audit...")
        if filters:
            print(f"[DEBUG] Applying client-side filters: {filters}")
        
        # Fetch all prospects (cached after first call)
        print("Fetching prospects...")
        prospects = self.get_all_prospects(filters=filters)
        
        if not prospects:
            return {
                "error": "Failed to fetch prospects",
                "total_prospects": 0,
                "duplicates": {"count": 0, "details": []},
                "inactive_prospects": {"count": 0, "details": []},
                "missing_fields": {"count": 0, "details": []},
                "all_prospects": []
            }
        
        total_fetched = len(prospects)
        print(f"Analyzing {total_fetched:,} prospects...")
        
        # Run all audits
        duplicates = self.find_duplicate_prospects(prospects)
        inactive = self.find_inactive_prospects(prospects)
        missing = self.find_missing_critical_fields(prospects)
        scoring_issues = self.find_scoring_issues(prospects)
        
        print(f"[DEBUG] Duplicates found: {len(duplicates)}")
        print(f"[DEBUG] Inactive prospects: {len(inactive)}")
        print(f"[DEBUG] Missing fields: {len(missing)}")
        print(f"[DEBUG] Scoring issues: {len(scoring_issues)}")
        
        audit_results = {
            'total_prospects': len(prospects),
            'duplicates': {
                'count': len(duplicates),
                'details': duplicates
            },
            'inactive_prospects': {
                'count': len(inactive),
                'details': inactive
            },
            'missing_fields': {
                'count': len(missing),
                'details': missing
            },
            'scoring_issues': {
                'count': len(scoring_issues),
                'details': scoring_issues
            },
            'all_prospects': prospects  # Cache all prospects for filtering
        }
        
        print(f"Audit completed successfully - {total_fetched:,} prospects analyzed")
        return audit_results