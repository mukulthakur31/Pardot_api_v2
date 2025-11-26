from flask import Blueprint, jsonify, g, request
from services.engagement_service import EngagementHealthAuditor
from middleware.auth_middleware import require_auth
from cache import get_cached_data, set_cached_data
from datetime import datetime, timedelta

engagement_bp = Blueprint('engagement', __name__)

# Tab cache for engagement data
tab_cache = {}

def get_or_create_tab_cache(cache_key):
    if cache_key not in tab_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            tab_cache[cache_key] = {
                'all_programs': cached_data.get('all_programs', []),
                'active_programs': cached_data.get('active_programs', []),
                'inactive_programs': cached_data.get('inactive_programs', []),
                'low_performance': cached_data.get('low_performance', []),
                'no_entries': cached_data.get('no_entries', [])
            }
    return tab_cache.get(cache_key)

@engagement_bp.route("/engagement-health-analysis", methods=["GET"])
@require_auth
def engagement_health_analysis():
    try:
        auditor = EngagementHealthAuditor(g.access_token)
        analysis_data = auditor.analyze_engagement_health()
        
        cache_key = f"engagement:{g.access_token[:20]}"
        set_cached_data(cache_key, analysis_data, ttl=1800)
        
        # Update tab cache
        tab_cache[cache_key] = {
            'all_programs': analysis_data.get('all_programs', []),
            'active_programs': analysis_data.get('active_programs', []),
            'inactive_programs': analysis_data.get('inactive_programs', []),
            'low_performance': analysis_data.get('low_performance', []),
            'no_entries': analysis_data.get('no_entries', [])
        }
        
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@engagement_bp.route("/get-all-programs", methods=["GET"])
@require_auth
def get_all_programs():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        cache_key = f"engagement:{g.access_token[:20]}"
        
        tab_data = get_or_create_tab_cache(cache_key)
        if not tab_data:
            return jsonify({"error": "Please run engagement health analysis first"}), 400
        
        programs = tab_data['all_programs']
        total = len(programs)
        start = (page - 1) * per_page
        
        return jsonify({
            "total_programs": total,
            "all_programs": programs[start:start + per_page],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@engagement_bp.route("/get-active-programs", methods=["GET"])
@require_auth
def get_active_programs():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        cache_key = f"engagement:{g.access_token[:20]}"
        
        tab_data = get_or_create_tab_cache(cache_key)
        if not tab_data:
            return jsonify({"error": "Please run engagement health analysis first"}), 400
        
        programs = tab_data['active_programs']
        total = len(programs)
        start = (page - 1) * per_page
        
        return jsonify({
            "total_active": total,
            "active_programs": programs[start:start + per_page],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@engagement_bp.route("/get-inactive-programs", methods=["GET"])
@require_auth
def get_inactive_programs():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        cache_key = f"engagement:{g.access_token[:20]}"
        
        tab_data = get_or_create_tab_cache(cache_key)
        if not tab_data:
            return jsonify({"error": "Please run engagement health analysis first"}), 400
        
        programs = tab_data['inactive_programs']
        total = len(programs)
        start = (page - 1) * per_page
        
        return jsonify({
            "total_inactive": total,
            "inactive_programs": programs[start:start + per_page],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@engagement_bp.route("/get-low-performance-programs", methods=["GET"])
@require_auth
def get_low_performance_programs():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        cache_key = f"engagement:{g.access_token[:20]}"
        
        tab_data = get_or_create_tab_cache(cache_key)
        if not tab_data:
            return jsonify({"error": "Please run engagement health analysis first"}), 400
        
        programs = tab_data['low_performance']
        total = len(programs)
        start = (page - 1) * per_page
        
        return jsonify({
            "total_low_performance": total,
            "low_performance_programs": programs[start:start + per_page],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@engagement_bp.route("/get-no-entries-programs", methods=["GET"])
@require_auth
def get_no_entries_programs():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        cache_key = f"engagement:{g.access_token[:20]}"
        
        tab_data = get_or_create_tab_cache(cache_key)
        if not tab_data:
            return jsonify({"error": "Please run engagement health analysis first"}), 400
        
        programs = tab_data['no_entries']
        total = len(programs)
        start = (page - 1) * per_page
        
        return jsonify({
            "total_no_entries": total,
            "no_entries_programs": programs[start:start + per_page],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@engagement_bp.route("/filter-programs", methods=["POST"])
@require_auth
def filter_programs_route():
    try:
        data = request.json or {}
        filters = data.get('filters', {})
        page = int(data.get('page', 1))
        per_page = int(data.get('per_page', 10))
        
        cache_key = f"engagement:{g.access_token[:20]}"
        tab_data = get_or_create_tab_cache(cache_key)
        if not tab_data:
            return jsonify({"error": "Please run engagement health analysis first"}), 400
        
        programs = tab_data['all_programs']
        if not programs:
            return jsonify({"error": "No program data available"}), 400
        
        filtered_programs = apply_filters(programs, filters)
        
        total = len(filtered_programs)
        start = (page - 1) * per_page
        
        return jsonify({
            "total_programs": len(programs),
            "filtered_count": total,
            "programs": filtered_programs[start:start + per_page],
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

def apply_filters(programs, filters):
    filtered = programs
    
    # Apply view filter
    view = filters.get('view', 'all_programs')
    if view == 'active_programs':
        filtered = [p for p in filtered if p.get('status') == 'Running' and not p.get('isDeleted')]
    elif view == 'inactive_programs':
        filtered = [p for p in filtered if p.get('status') != 'Running' or p.get('isDeleted')]
    elif view == 'paused_programs':
        filtered = [p for p in filtered if p.get('status') == 'Paused']
    elif view == 'deleted_programs':
        filtered = [p for p in filtered if p.get('isDeleted')]
    
    # Apply date range filter
    date_range = filters.get('date_range', 'all_time')
    if date_range != 'all_time':
        date_field = filters.get('date_field', 'created')
        filtered = apply_date_filter(filtered, date_field, date_range, filters)
    
    return filtered

def apply_date_filter(programs, date_field_key, date_range, filters):
    date_field_mapping = {
        'created': 'createdAt',
        'updated': 'updatedAt'
    }
    
    date_field = date_field_mapping.get(date_field_key, 'createdAt')
    now = datetime.now()
    
    if date_range == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'yesterday':
        start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = (now - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
    elif date_range == 'last_7_days':
        start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'last_30_days':
        start_date = (now - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'custom':
        start_date_str = filters.get('start_date')
        end_date_str = filters.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        else:
            return programs
    else:
        return programs
    
    filtered_programs = []
    for program in programs:
        program_date_str = program.get(date_field)
        if program_date_str:
            try:
                program_date = datetime.fromisoformat(program_date_str.replace('Z', '+00:00'))
                if start_date <= program_date <= end_date:
                    filtered_programs.append(program)
            except (ValueError, TypeError):
                continue
    
    return filtered_programs