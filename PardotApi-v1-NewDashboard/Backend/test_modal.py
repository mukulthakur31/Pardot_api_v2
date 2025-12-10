#!/usr/bin/env python3

import json
import requests

def test_modal_structure():
    """Test PDF modal structure"""
    
    # Mock modal options structure
    modal_options = {
        "title": "Customize Your Prospect Health PDF Report",
        "description": "Select which sections and metrics to include in your comprehensive report:",
        "sections": [
            {
                "id": "active_contacts",
                "label": "Active Contacts Analysis",
                "description": "Engagement metrics and activity data",
                "enabled": True,
                "default": True,
                "subsections": [
                    {"id": "total_database", "label": "Total Database Count", "default": True},
                    {"id": "active_leads_6m", "label": "Active Leads (6 months)", "default": True},
                    {"id": "marketable_leads", "label": "Marketable Leads", "default": True},
                    {"id": "form_submissions", "label": "Form Submissions", "default": True},
                    {"id": "email_opens", "label": "Email Opens", "default": True}
                ]
            },
            {
                "id": "inactive_contacts",
                "label": "Inactive Contacts Analysis", 
                "description": "Unsubscribed leads and inactive periods",
                "enabled": True,
                "default": True,
                "subsections": [
                    {"id": "inactive_leads", "label": "Inactive Leads", "default": True},
                    {"id": "unsubscribed_leads", "label": "Unsubscribed Leads", "default": True},
                    {"id": "inactive_6m", "label": "Inactive 6 Months", "default": True}
                ]
            },
            {
                "id": "data_quality",
                "label": "Data Quality & Issues",
                "description": "Empty fields, duplicates, and data quality issues", 
                "enabled": True,
                "default": True,
                "subsections": [
                    {"id": "junk_leads", "label": "Junk/Test Leads", "default": True},
                    {"id": "duplicate_leads", "label": "Duplicate Leads", "default": True},
                    {"id": "email_empty", "label": "Empty Email Addresses", "default": True}
                ]
            },
            {
                "id": "charts",
                "label": "Charts & Visualizations",
                "description": "Trend charts and visual analytics",
                "enabled": True,
                "default": True,
                "subsections": [
                    {"id": "lead_creation_trend", "label": "Lead Creation Trend Chart", "default": True},
                    {"id": "engagement_breakdown", "label": "Engagement Breakdown Chart", "default": True},
                    {"id": "inactive_breakdown", "label": "Inactive Breakdown Chart", "default": True}
                ]
            }
        ],
        "data_available": True,
        "export_options": {
            "include_summary": {"label": "Executive Summary", "default": True},
            "include_methodology": {"label": "Methodology Notes", "default": False},
            "page_breaks": {"label": "Page Breaks Between Sections", "default": True}
        }
    }
    
    print("Modal Structure Test:")
    print(f"Title: {modal_options['title']}")
    print(f"Sections Count: {len(modal_options['sections'])}")
    print(f"Data Available: {modal_options['data_available']}")
    
    total_subsections = 0
    for section in modal_options['sections']:
        subsection_count = len(section.get('subsections', []))
        total_subsections += subsection_count
        print(f"\nSection: {section['label']}")
        print(f"  ID: {section['id']}")
        print(f"  Enabled: {section['enabled']}")
        print(f"  Subsections: {subsection_count}")
        
        for subsection in section.get('subsections', []):
            print(f"    - {subsection['label']} (default: {subsection['default']})")
    
    print(f"\nTotal Subsections: {total_subsections}")
    print(f"Export Options: {len(modal_options['export_options'])}")
    
    # Test JSON serialization
    try:
        json_str = json.dumps(modal_options, indent=2)
        print(f"\nJSON Serialization: SUCCESS ({len(json_str)} characters)")
        return True
    except Exception as e:
        print(f"\nJSON Serialization: FAILED - {str(e)}")
        return False

if __name__ == "__main__":
    test_modal_structure()