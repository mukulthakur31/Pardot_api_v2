from datetime import datetime, timedelta
try:
    from dateutil import parser
except ImportError:
    # Fallback to basic datetime parsing if dateutil is not available
    import datetime as dt
    class parser:
        @staticmethod
        def parse(date_string):
            # Basic ISO format parsing
            return dt.datetime.fromisoformat(date_string.replace('Z', '+00:00'))

class ProspectFilterService:
    def __init__(self, prospects_data):
        self.all_prospects = prospects_data
        
    def apply_filters(self, view_filter="All Prospects", activity_filter="Last Activity", 
                     time_filter="All Time", custom_start_date=None, custom_end_date=None, 
                     tag_filter=""):
        """Apply all filters to the prospect data"""
        filtered_prospects = self.all_prospects.copy()
        
        # Apply view filter
        filtered_prospects = self._apply_view_filter(filtered_prospects, view_filter)
        
        # Apply time filter based on activity filter
        filtered_prospects = self._apply_time_filter(filtered_prospects, activity_filter, 
                                                   time_filter, custom_start_date, custom_end_date)
        
        # Apply tag filter
        if tag_filter:
            filtered_prospects = self._apply_tag_filter(filtered_prospects, tag_filter)
            
        return filtered_prospects
    
    def _apply_view_filter(self, prospects, view_filter):
        """Apply view-based filters"""
        if view_filter == "All Prospects":
            return prospects
        elif view_filter == "Active Prospects":
            return [p for p in prospects if self._is_active_prospect(p)]
        elif view_filter == "Active Prospects For Review":
            return [p for p in prospects if self._is_active_prospect(p) and self._needs_review(p)]
        elif view_filter == "Assigned Prospects":
            return [p for p in prospects if p.get('assignedTo')]
        elif view_filter == "Mailable Prospects":
            return [p for p in prospects if self._is_mailable(p)]
        elif view_filter == "My Prospects":
            return [p for p in prospects if self._is_my_prospect(p)]
        elif view_filter == "My Starred Prospects":
            return [p for p in prospects if self._is_starred(p)]
        elif view_filter == "Never Active Prospects":
            return [p for p in prospects if not p.get('lastActivityAt')]
        elif view_filter == "Prospects Not In Salesforce":
            return [p for p in prospects if not p.get('salesforceId')]
        elif view_filter == "Reviewed Prospects":
            return [p for p in prospects if p.get('isReviewed')]
        elif view_filter == "Unassigned Prospects":
            return [p for p in prospects if not p.get('assignedTo')]
        elif view_filter == "Unmailable Prospects":
            return [p for p in prospects if not self._is_mailable(p)]
        elif view_filter == "Unsubscribed Prospects":
            return [p for p in prospects if p.get('isDoNotEmail')]
        elif view_filter == "Paused Prospects":
            return [p for p in prospects if p.get('isPaused')]
        elif view_filter == "Undelivered Prospects":
            return [p for p in prospects if self._has_undelivered_emails(p)]
        else:
            return prospects
    
    def _apply_time_filter(self, prospects, activity_filter, time_filter, custom_start_date, custom_end_date):
        """Apply time-based filters"""
        if time_filter == "All Time":
            return prospects
            
        now = datetime.now()
        start_date = None
        end_date = now
        
        if time_filter == "Today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == "Yesterday":
            yesterday = now - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif time_filter == "This Month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == "This Quarter":
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == "This Year":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == "Last 7 Days":
            start_date = now - timedelta(days=7)
        elif time_filter == "Last Week":
            days_since_monday = now.weekday()
            last_monday = now - timedelta(days=days_since_monday + 7)
            start_date = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = last_monday + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif time_filter == "Last Month":
            if now.month == 1:
                start_date = now.replace(year=now.year-1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
            else:
                start_date = now.replace(month=now.month-1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
        elif time_filter == "Last Quarter":
            current_quarter_start = ((now.month - 1) // 3) * 3 + 1
            if current_quarter_start == 1:
                start_date = now.replace(year=now.year-1, month=10, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
            else:
                last_quarter_start = current_quarter_start - 3
                start_date = now.replace(month=last_quarter_start, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(month=current_quarter_start, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
        elif time_filter == "Last Year":
            start_date = now.replace(year=now.year-1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
        elif time_filter == "Custom" and custom_start_date and custom_end_date:
            start_date = parser.parse(custom_start_date)
            end_date = parser.parse(custom_end_date)
        
        if start_date:
            return self._filter_by_date_range(prospects, activity_filter, start_date, end_date)
        
        return prospects
    
    def _filter_by_date_range(self, prospects, activity_filter, start_date, end_date):
        """Filter prospects by date range based on activity filter"""
        filtered = []
        
        for prospect in prospects:
            date_field = None
            
            if activity_filter == "Last Activity":
                date_field = prospect.get('lastActivityAt')
            elif activity_filter == "Created":
                date_field = prospect.get('createdAt')
            elif activity_filter == "Updated":
                date_field = prospect.get('updatedAt')
            elif activity_filter == "First Assigned":
                date_field = prospect.get('firstAssignedAt')
            
            if date_field:
                try:
                    prospect_date = parser.parse(date_field)
                    if start_date <= prospect_date <= end_date:
                        filtered.append(prospect)
                except:
                    continue
            elif activity_filter == "Last Activity" and not date_field:
                # Include prospects with no activity if filtering by last activity
                filtered.append(prospect)
                
        return filtered
    
    def _apply_tag_filter(self, prospects, tag_filter):
        """Filter prospects by tags"""
        if not tag_filter:
            return prospects
            
        tag_terms = [term.strip().lower() for term in tag_filter.split(',')]
        filtered = []
        
        for prospect in prospects:
            prospect_tags = prospect.get('tags', [])
            if isinstance(prospect_tags, str):
                prospect_tags = [prospect_tags]
            
            prospect_tags_lower = [tag.lower() for tag in prospect_tags]
            
            # Check if any of the search terms match any prospect tags
            if any(any(term in tag for tag in prospect_tags_lower) for term in tag_terms):
                filtered.append(prospect)
                
        return filtered
    
    def _is_active_prospect(self, prospect):
        """Check if prospect is active (has recent activity)"""
        last_activity = prospect.get('lastActivityAt')
        if not last_activity:
            return False
        
        try:
            activity_date = parser.parse(last_activity)
            cutoff_date = datetime.now() - timedelta(days=30)
            return activity_date > cutoff_date
        except:
            return False
    
    def _needs_review(self, prospect):
        """Check if prospect needs review"""
        return prospect.get('score', 0) > 50 and not prospect.get('isReviewed', False)
    
    def _is_mailable(self, prospect):
        """Check if prospect is mailable"""
        return (prospect.get('email') and 
                not prospect.get('isDoNotEmail', False) and 
                not prospect.get('isUnsubscribed', False) and
                not prospect.get('isHardBounced', False))
    
    def _is_my_prospect(self, prospect):
        """Check if prospect is assigned to current user (placeholder logic)"""
        # This would need to be implemented based on current user context
        return prospect.get('assignedTo') == 'current_user_id'
    
    def _is_starred(self, prospect):
        """Check if prospect is starred"""
        return prospect.get('isStarred', False)
    
    def _has_undelivered_emails(self, prospect):
        """Check if prospect has undelivered emails"""
        return prospect.get('hasUndeliveredEmails', False)

def filter_prospects(prospects_data, filters):
    """Main function to filter prospects"""
    filter_service = ProspectFilterService(prospects_data)
    
    return filter_service.apply_filters(
        view_filter=filters.get('view', 'All Prospects'),
        activity_filter=filters.get('activity', 'Last Activity'),
        time_filter=filters.get('time', 'All Time'),
        custom_start_date=filters.get('customStartDate'),
        custom_end_date=filters.get('customEndDate'),
        tag_filter=filters.get('tags', '')
    )