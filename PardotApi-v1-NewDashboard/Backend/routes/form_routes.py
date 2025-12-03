from flask import Blueprint, request, jsonify, g
from services.form_service import (
    get_form_stats, get_active_inactive_forms, get_form_abandonment_analysis,
    get_date_range_from_filter, get_active_inactive_forms_from_cache, 
    get_form_abandonment_analysis_from_cache
)
from middleware.auth_middleware import require_auth
from cache import get_cached_data, set_cached_data

form_bp = Blueprint('form', __name__)

@form_bp.route("/get-form-stats", methods=["GET"])
@require_auth
def get_form_stats_route():
    try:
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        if filter_type and not start_date and not end_date:
            start_date, end_date = get_date_range_from_filter(filter_type)
        
        cache_key = f"forms:{g.access_token[:20]}:{filter_type or 'all'}:{start_date or ''}:{end_date or ''}"
        
        # Check cache first
        cached_data = get_cached_data(cache_key)
        if cached_data:
            print(f"📦 FORM DATA: Retrieved from CACHE - Key: {cache_key}")
            return jsonify(cached_data)
        
        # Fetch fresh data from API
        print(f"🌐 FORM DATA: Fetching from API - Key: {cache_key}")
        form_stats = get_form_stats(g.access_token, start_date, end_date)
        
        # Cache the data for 30 minutes
        set_cached_data(cache_key, form_stats, ttl=1800)
        print(f"💾 FORM DATA: Cached for 30 minutes - Key: {cache_key}")
        
        return jsonify(form_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@form_bp.route("/get-active-inactive-forms", methods=["GET"])
@require_auth
def get_active_inactive_forms_route():
    try:
        cache_key = f"forms:{g.access_token[:20]}:all:::"
        cached_forms = get_cached_data(cache_key)
        
        if cached_forms:
            print(f"📦 ACTIVE/INACTIVE FORMS: Retrieved from CACHE - Key: {cache_key}")
            forms_data = get_active_inactive_forms_from_cache(cached_forms)
        else:
            print(f"🌐 ACTIVE/INACTIVE FORMS: Fetching from API - Key: {cache_key}")
            form_stats = get_form_stats(g.access_token)
            set_cached_data(cache_key, form_stats, ttl=1800)
            print(f"💾 ACTIVE/INACTIVE FORMS: Cached for 30 minutes - Key: {cache_key}")
            forms_data = get_active_inactive_forms_from_cache(form_stats)
        
        return jsonify(forms_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@form_bp.route("/get-form-abandonment-analysis", methods=["GET"])
@require_auth
def get_form_abandonment_analysis_route():
    try:
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        if filter_type and not start_date and not end_date:
            start_date, end_date = get_date_range_from_filter(filter_type)
        
        cache_key = f"forms:{g.access_token[:20]}:{filter_type or 'all'}:{start_date or ''}:{end_date or ''}"
        cached_forms = get_cached_data(cache_key)
        
        if cached_forms:
            print(f"📦 FORM ABANDONMENT: Retrieved from CACHE - Key: {cache_key}")
            abandonment_data = get_form_abandonment_analysis_from_cache(cached_forms)
        else:
            print(f"🌐 FORM ABANDONMENT: Fetching from API - Key: {cache_key}")
            form_stats = get_form_stats(g.access_token, start_date, end_date)
            set_cached_data(cache_key, form_stats, ttl=1800)
            print(f"💾 FORM ABANDONMENT: Cached for 30 minutes - Key: {cache_key}")
            abandonment_data = get_form_abandonment_analysis_from_cache(form_stats)
        
        return jsonify(abandonment_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@form_bp.route("/get-filtered-form-stats", methods=["GET"])
@require_auth
def get_filtered_form_stats_route():
    try:
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        if filter_type and not start_date and not end_date:
            start_date, end_date = get_date_range_from_filter(filter_type)
        
        filtered_stats = get_form_stats(g.access_token, start_date, end_date)
        return jsonify(filtered_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500