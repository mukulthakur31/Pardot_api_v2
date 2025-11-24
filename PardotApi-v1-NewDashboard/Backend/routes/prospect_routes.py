from flask import Blueprint, request, jsonify, g
from services.prospect_service import (
    get_prospect_health, find_duplicate_prospects, find_inactive_prospects, 
    find_missing_critical_fields
)
from datetime import datetime, timedelta
from cache import get_cached_data, set_cached_data
from middleware.auth_middleware import require_auth

prospect_bp = Blueprint('prospect', __name__)

@prospect_bp.route("/get-prospect-health", methods=["GET"])
@require_auth
def get_prospect_health_route():
    try:
        health_data = get_prospect_health(g.access_token)
        set_cached_data(f"prospects:{g.access_token[:20]}", health_data, ttl=1800)
        return jsonify(health_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prospect_bp.route("/get-inactive-prospects", methods=["GET"])
@require_auth
def get_inactive_prospects():
    try:
        cached_health = get_cached_data(f"prospects:{g.access_token[:20]}")
        if cached_health and 'all_prospects' in cached_health:
            prospects = cached_health['all_prospects']
            inactive_prospects = find_inactive_prospects(prospects)
            
            return jsonify({
                "total_inactive": len(inactive_prospects),
                "inactive_prospects": inactive_prospects
            })
        else:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prospect_bp.route("/get-duplicate-prospects", methods=["GET"])
@require_auth
def get_duplicate_prospects():
    try:
        cached_health = get_cached_data(f"prospects:{g.access_token[:20]}")
        if cached_health and 'all_prospects' in cached_health:
            prospects = cached_health['all_prospects']
            duplicates = find_duplicate_prospects(prospects)
            
            return jsonify({
                "total_duplicate_groups": len(duplicates),
                "duplicate_prospects": duplicates
            })
        else:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prospect_bp.route("/get-missing-fields-prospects", methods=["GET"])
@require_auth
def get_missing_fields_prospects():
    try:
        cached_health = get_cached_data(f"prospects:{g.access_token[:20]}")
        if cached_health and 'all_prospects' in cached_health:
            prospects = cached_health['all_prospects']
            missing_fields = find_missing_critical_fields(prospects)
            
            return jsonify({
                "total_with_missing_fields": len(missing_fields),
                "prospects_missing_fields": missing_fields
            })
        else:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prospect_bp.route("/filter-prospects", methods=["POST"])
@require_auth
def filter_prospects_route():
    try:
        filters = request.json or {}
        
        cached_health = get_cached_data(f"prospects:{g.access_token[:20]}")
        if not cached_health:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
        
        if 'all_prospects' not in cached_health:
            return jsonify({"error": "Cached data missing all_prospects"}), 400
        
        prospects = cached_health['all_prospects']
        filtered_prospects = apply_simple_filters(prospects, filters)
        
        return jsonify({
            "total_prospects": len(prospects),
            "filtered_count": len(filtered_prospects),
            "prospects": filtered_prospects,
            "filters_applied": filters
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def apply_simple_filters(prospects, filters):
    """Apply basic filters to prospect data"""
    filtered = prospects.copy()
    
    # View filters
    view = filters.get('view', 'All Prospects')
    if view == 'Active Prospects':
        filtered = [p for p in filtered if p.get('lastActivityAt')]
    elif view == 'Never Active Prospects':
        filtered = [p for p in filtered if not p.get('lastActivityAt')]
    elif view == 'Active Prospects For Review':
        filtered = [p for p in filtered if p.get('lastActivityAt') and not p.get('isReviewed')]
    elif view == 'Assigned Prospects':
        filtered = [p for p in filtered if p.get('assignedTo')]
    elif view == 'Mailable Prospects':
        filtered = [p for p in filtered if not p.get('isDoNotEmail', False) and p.get('email')]
    elif view == 'My Prospects':
        filtered = [p for p in filtered if p.get('assignedTo') == 'current_user']
    elif view == 'My Starred Prospects':
        filtered = [p for p in filtered if p.get('isStarred')]
    elif view == 'Prospects Not In Salesforce':
        filtered = [p for p in filtered if not p.get('salesforceId')]
    elif view == 'Reviewed Prospects':
        filtered = [p for p in filtered if p.get('isReviewed')]
    elif view == 'Unassigned Prospects':
        filtered = [p for p in filtered if not p.get('assignedTo')]
    elif view == 'Unmailable Prospects':
        filtered = [p for p in filtered if p.get('isDoNotEmail', False)]
    elif view == 'Unsubscribed Prospects':
        filtered = [p for p in filtered if p.get('optedOut', False)]
    elif view == 'Paused Prospects':
        filtered = [p for p in filtered if p.get('isPaused', False)]
    elif view == 'Undelivered Prospects':
        filtered = [p for p in filtered if p.get('isEmailHardBounced', False)]
    
    # Time filters
    time_filter = filters.get('time', 'All Time')
    if time_filter != 'All Time':
        now = datetime.now()
        activity_field = 'lastActivityAt' if filters.get('activity') == 'Last Activity' else 'createdAt'
        
        start_date = None
        end_date = None
        
        if time_filter == 'Today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif time_filter == 'Yesterday':
            yesterday = now - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif time_filter == 'Last 7 Days':
            start_date = now - timedelta(days=7)
            end_date = now
        elif time_filter == 'Last Month':
            if now.month == 1:
                start_date = now.replace(year=now.year-1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
            else:
                start_date = now.replace(month=now.month-1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
        
        if start_date:
            time_filtered = []
            for p in filtered:
                date_val = p.get(activity_field)
                if date_val:
                    try:
                        if 'T' in str(date_val):
                            prospect_date = datetime.fromisoformat(str(date_val).replace('Z', '+00:00'))
                        else:
                            prospect_date = datetime.strptime(str(date_val)[:10], '%Y-%m-%d')
                        
                        prospect_date = prospect_date.replace(tzinfo=None)
                        if end_date:
                            if start_date <= prospect_date <= end_date:
                                time_filtered.append(p)
                        else:
                            if prospect_date >= start_date:
                                time_filtered.append(p)
                    except:
                        continue
            filtered = time_filtered
    
    return filtered