from flask import Blueprint, request, jsonify, g
from services.prospect_service import (
    get_prospect_health, find_duplicate_prospects, find_inactive_prospects, 
    find_missing_critical_fields, find_scoring_issues
)
from datetime import datetime, timedelta
from cache import get_cached_data, set_cached_data
from middleware.auth_middleware import require_auth

prospect_bp = Blueprint('prospect', __name__)

# In-memory fallback cache
_memory_cache = {}

# Tab data cache for instant loading
_tab_cache = {}

def get_or_create_tab_cache(cache_key):
    """Get or create cached tab data for instant loading"""
    if cache_key in _tab_cache:
        return _tab_cache[cache_key]
    
    # Get main health data
    cached_health = get_cached_data(cache_key)
    if not cached_health:
        cached_health = _memory_cache.get(cache_key)
    
    if not cached_health:
        return None
    
    # Pre-calculate all tab data
    all_prospects = cached_health.get('all_prospects', [])
    active_prospects = [p for p in all_prospects if p.get('lastActivityAt')]
    
    tab_data = {
        'all_prospects': all_prospects,
        'active_prospects': active_prospects,
        'duplicates': cached_health.get('duplicates', {}).get('details', []),
        'inactive': cached_health.get('inactive_prospects', {}).get('details', []),
        'missing_fields': cached_health.get('missing_fields', {}).get('details', []),
        'scoring_issues': cached_health.get('scoring_issues', {}).get('details', [])
    }
    
    # Cache for instant access
    _tab_cache[cache_key] = tab_data
    return tab_data

@prospect_bp.route("/get-prospect-health", methods=["GET"])
@require_auth
def get_prospect_health_route():
    try:
        cache_key = f"prospects:{g.access_token[:20]}"
        
        # Check cache first
        cached_data = get_cached_data(cache_key)
        if cached_data:
            print(f"📦 PROSPECT DATA: Retrieved from CACHE - Key: {cache_key}")
            
            # Calculate active prospects count from cached data
            all_prospects = cached_data.get("all_prospects", [])
            active_prospects = len([p for p in all_prospects if p.get('lastActivityAt')])
            
            response_data = {
                "total_prospects": cached_data.get("total_prospects", 0),
                "active_prospects": active_prospects,
                "duplicate_count": cached_data.get("duplicates", {}).get("count", 0),
                "inactive_count": cached_data.get("inactive_prospects", {}).get("count", 0),
                "missing_fields_count": cached_data.get("missing_fields", {}).get("count", 0),
                "scoring_issues_count": cached_data.get("scoring_issues", {}).get("count", 0),
                "health_score": "Good" if cached_data.get("duplicates", {}).get("count", 0) == 0 else "Needs Attention"
            }
            return jsonify(response_data)
        
        # Fetch fresh data from API
        print(f"🌐 PROSPECT DATA: Fetching from API - Key: {cache_key}")
        health_data = get_prospect_health(g.access_token)
        
        # Calculate active prospects count
        all_prospects = health_data.get("all_prospects", [])
        active_prospects = len([p for p in all_prospects if p.get('lastActivityAt')])
        
        response_data = {
            "total_prospects": health_data.get("total_prospects", 0),
            "active_prospects": active_prospects,
            "duplicate_count": health_data.get("duplicates", {}).get("count", 0),
            "inactive_count": health_data.get("inactive_prospects", {}).get("count", 0),
            "missing_fields_count": health_data.get("missing_fields", {}).get("count", 0),
            "scoring_issues_count": health_data.get("scoring_issues", {}).get("count", 0),
            "health_score": "Good" if health_data.get("duplicates", {}).get("count", 0) == 0 else "Needs Attention"
        }
        
        # Clear tab cache for fresh data
        if cache_key in _tab_cache:
            del _tab_cache[cache_key]
        
        # Try Redis first, fallback to memory
        cache_success = set_cached_data(cache_key, health_data, ttl=1800)
        if not cache_success:
            _memory_cache[cache_key] = health_data
            print(f"💾 PROSPECT DATA: Stored in memory cache - Key: {cache_key}")
        else:
            print(f"💾 PROSPECT DATA: Cached for 30 minutes - Key: {cache_key}")
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prospect_bp.route("/get-duplicate-prospects", methods=["GET"])
@require_auth
def get_duplicate_prospects():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        cache_key = f"prospects:{g.access_token[:20]}"
        
        tab_data = get_or_create_tab_cache(cache_key)
        if not tab_data:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
        
        duplicates = tab_data['duplicates']
        total = len(duplicates)
        start = (page - 1) * per_page
        
        return jsonify({
            "total_duplicate_groups": total,
            "duplicate_prospects": duplicates[start:start + per_page],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prospect_bp.route("/get-inactive-prospects", methods=["GET"])
@require_auth
def get_inactive_prospects():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        cache_key = f"prospects:{g.access_token[:20]}"
        
        tab_data = get_or_create_tab_cache(cache_key)
        if not tab_data:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
        
        prospects = tab_data['inactive']
        total = len(prospects)
        start = (page - 1) * per_page
        
        return jsonify({
            "total_inactive": total,
            "inactive_prospects": prospects[start:start + per_page],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prospect_bp.route("/get-missing-fields-prospects", methods=["GET"])
@require_auth
def get_missing_fields_prospects():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        cache_key = f"prospects:{g.access_token[:20]}"
        
        tab_data = get_or_create_tab_cache(cache_key)
        if not tab_data:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
        
        prospects = tab_data['missing_fields']
        total = len(prospects)
        start = (page - 1) * per_page
        
        return jsonify({
            "total_with_missing_fields": total,
            "prospects_missing_fields": prospects[start:start + per_page],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prospect_bp.route("/get-scoring-issues-prospects", methods=["GET"])
@require_auth
def get_scoring_issues_prospects():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        cache_key = f"prospects:{g.access_token[:20]}"
        
        tab_data = get_or_create_tab_cache(cache_key)
        if not tab_data:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
        
        prospects = tab_data['scoring_issues']
        total = len(prospects)
        start = (page - 1) * per_page
        
        return jsonify({
            "total_scoring_issues": total,
            "prospects_scoring_issues": prospects[start:start + per_page],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prospect_bp.route("/get-all-prospects", methods=["GET"])
@require_auth
def get_all_prospects():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        cache_key = f"prospects:{g.access_token[:20]}"
        
        tab_data = get_or_create_tab_cache(cache_key)
        if not tab_data:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
        
        prospects = tab_data['all_prospects']
        total = len(prospects)
        start = (page - 1) * per_page
        
        return jsonify({
            "total_prospects": total,
            "all_prospects": prospects[start:start + per_page],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prospect_bp.route("/get-active-prospects", methods=["GET"])
@require_auth
def get_active_prospects():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        cache_key = f"prospects:{g.access_token[:20]}"
        
        tab_data = get_or_create_tab_cache(cache_key)
        if not tab_data:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
        
        prospects = tab_data['active_prospects']
        total = len(prospects)
        start = (page - 1) * per_page
        
        return jsonify({
            "total_active": total,
            "active_prospects": prospects[start:start + per_page],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prospect_bp.route("/filter-prospects", methods=["POST"])
@require_auth
def filter_prospects_route():
    try:
        data = request.json or {}
        filters = data.get('filters', {})
        page = int(data.get('page', 1))
        per_page = int(data.get('per_page', 10))
        
        cache_key = f"prospects:{g.access_token[:20]}"
        tab_data = get_or_create_tab_cache(cache_key)
        if not tab_data:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
        
        prospects = tab_data['all_prospects']
        if not prospects:
            return jsonify({"error": "No prospect data available"}), 400
        
        filtered_prospects = apply_filters(prospects, filters)
        
        # Apply pagination
        total = len(filtered_prospects)
        start = (page - 1) * per_page
        
        return jsonify({
            "total_prospects": len(prospects),
            "filtered_count": total,
            "prospects": filtered_prospects[start:start + per_page],
            "filters_applied": filters,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def apply_filters(prospects, filters):
    filtered = prospects
    
    # Apply view filter
    view = filters.get('view', 'all_prospects')
    if view == 'active_prospects':
        filtered = [p for p in filtered if p.get('lastActivityAt')]
    elif view == 'never_active_prospects':
        filtered = [p for p in filtered if not p.get('lastActivityAt')]
    elif view == 'assigned_prospects':
        filtered = [p for p in filtered if p.get('assignedToId')]
    elif view == 'mailable_prospects':
        filtered = [p for p in filtered if not p.get('isDoNotEmail') and not p.get('optedOut') and p.get('email')]
    elif view == 'prospects_not_in_salesforce':
        filtered = [p for p in filtered if not p.get('salesforceId')]
    elif view == 'unassigned_prospects':
        filtered = [p for p in filtered if not p.get('assignedToId')]
    
    # Apply date range filter
    date_range = filters.get('date_range', 'all_time')
    if date_range != 'all_time':
        date_field = filters.get('date_field', 'last_activity')
        filtered = apply_date_filter(filtered, date_field, date_range, filters)
    
    return filtered

def apply_date_filter(prospects, date_field_key, date_range, filters):
    date_field_mapping = {
        'last_activity': 'lastActivityAt',
        'created': 'createdAt',
        'updated': 'updatedAt',
        'first_assigned': 'firstAssignedAt'
    }
    
    date_field = date_field_mapping.get(date_field_key, 'lastActivityAt')
    now = datetime.now()
    
    # Calculate date ranges
    if date_range == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'yesterday':
        start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = (now - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
    elif date_range == 'last_7_days':
        start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'last_week':
        days_since_sunday = (now.weekday() + 1) % 7
        last_sunday = (now - timedelta(days=days_since_sunday + 7)).replace(hour=0, minute=0, second=0, microsecond=0)
        last_saturday = (last_sunday + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999)
        start_date = last_sunday
        end_date = last_saturday
    elif date_range == 'this_month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'last_month':
        first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        start_date = last_day_last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = last_day_last_month.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif date_range == 'this_quarter':
        quarter = (now.month - 1) // 3 + 1
        start_date = now.replace(month=(quarter - 1) * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'last_quarter':
        quarter = (now.month - 1) // 3 + 1
        if quarter == 1:
            start_date = now.replace(year=now.year - 1, month=10, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(year=now.year - 1, month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            start_month = (quarter - 2) * 3 + 1
            start_date = now.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_month = start_month + 2
            if end_month == 12:
                end_date = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
            else:
                next_month = now.replace(month=end_month + 1, day=1)
                end_date = (next_month - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
    elif date_range == 'this_year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'last_year':
        start_date = now.replace(year=now.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(year=now.year - 1, month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    elif date_range == 'custom':
        start_date_str = filters.get('start_date')
        end_date_str = filters.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.fromisoformat(start_date_str).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = datetime.fromisoformat(end_date_str).replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            return prospects
    else:
        return prospects
    
    # Filter prospects by date
    filtered = []
    for prospect in prospects:
        field_value = prospect.get(date_field)
        if not field_value:
            continue
        
        try:
            if 'T' in str(field_value):
                field_date = datetime.fromisoformat(str(field_value).replace('Z', '+00:00'))
            else:
                field_date = datetime.fromisoformat(str(field_value)[:10])
            
            field_date = field_date.replace(tzinfo=None)
            if start_date <= field_date <= end_date:
                filtered.append(prospect)
        except:
            continue
    
    return filtered

@prospect_bp.route("/export-prospects", methods=["POST"])
@require_auth
def export_prospects():
    try:
        data = request.json or {}
        export_type = data.get('type', 'all')
        
        cache_key = f"prospects:{g.access_token[:20]}"
        cached_health = get_cached_data(cache_key)
        if not cached_health:
            cached_health = _memory_cache.get(cache_key)
        
        if not cached_health:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
        
        # Get comprehensive data for all tabs
        prospects = cached_health.get('all_prospects', [])
        
        # Get all analysis data from cache
        duplicates_data = cached_health.get('duplicates', {}).get('details', [])
        inactive_data = cached_health.get('inactive_prospects', {}).get('details', [])
        missing_fields_data = cached_health.get('missing_fields', {}).get('details', [])
        scoring_issues_data = cached_health.get('scoring_issues', {}).get('details', [])
        
        # Prepare export data based on type
        if export_type == 'duplicates':
            export_data = duplicates_data
        elif export_type == 'inactive':
            export_data = inactive_data
        elif export_type == 'missing_fields':
            export_data = missing_fields_data
        elif export_type == 'scoring_issues':
            export_data = scoring_issues_data
        else:
            # For 'all' type, include comprehensive data
            export_data = {
                'summary': {
                    'total_prospects': len(prospects),
                    'active_prospects': len([p for p in prospects if p.get('lastActivityAt')]),
                    'duplicate_groups': len(duplicates_data),
                    'inactive_prospects': len(inactive_data),
                    'missing_fields_prospects': len(missing_fields_data),
                    'scoring_issues_prospects': len(scoring_issues_data)
                },
                'all_prospects': prospects,
                'duplicates': duplicates_data,
                'inactive': inactive_data,
                'missing_fields': missing_fields_data,
                'scoring_issues': scoring_issues_data
            }
        
        return jsonify({
            "success": True,
            "data": export_data,
            "count": len(export_data) if isinstance(export_data, list) else len(export_data.get('all_prospects', [])),
            "type": export_type
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500