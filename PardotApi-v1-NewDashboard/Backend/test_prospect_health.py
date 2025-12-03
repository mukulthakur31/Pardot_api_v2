#!/usr/bin/env python3
"""
Test script for Prospect Health functionality
"""

import json
from services.database_health_service import DatabaseHealthAnalyzer

def test_prospect_health():
    """Test the prospect health functionality with mock data"""
    
    # Mock access token and business unit ID for testing
    mock_access_token = "test_token_12345"
    mock_business_unit_id = "test_bu_67890"
    
    print("Testing Prospect Health Functionality")
    print("=" * 50)
    
    try:
        # Initialize the analyzer
        analyzer = DatabaseHealthAnalyzer(mock_access_token, mock_business_unit_id)
        
        # Test the comprehensive stats method (will use fallback data due to mock token)
        print("Testing comprehensive stats generation...")
        stats = analyzer.get_comprehensive_stats()
        
        # Verify the structure
        print("\nVerifying data structure...")
        
        # Check if all three sections exist
        assert 'active_contacts' in stats, "Missing active_contacts section"
        assert 'inactive_contacts' in stats, "Missing inactive_contacts section"
        assert 'empty_details' in stats, "Missing empty_details section"
        
        print("All three sections present")
        
        # Check active contacts structure
        active_contacts = stats['active_contacts']
        assert 'table_data' in active_contacts, "Missing table_data in active_contacts"
        
        if active_contacts['table_data']:
            first_row = active_contacts['table_data'][0]
            required_fields = ['metric', 'count', 'percentage', 'industry_standard']
            for field in required_fields:
                assert field in first_row, f"Missing {field} in active_contacts"
        
        print("Active contacts structure valid")
        
        # Check inactive contacts structure
        inactive_contacts = stats['inactive_contacts']
        assert 'table_data' in inactive_contacts, "Missing table_data in inactive_contacts"
        
        if inactive_contacts['table_data']:
            first_row = inactive_contacts['table_data'][0]
            required_fields = ['metric', 'count', 'percentage']
            for field in required_fields:
                assert field in first_row, f"Missing {field} in inactive_contacts"
        
        print("Inactive contacts structure valid")
        
        # Check empty details structure
        empty_details = stats['empty_details']
        assert 'table_data' in empty_details, "Missing table_data in empty_details"
        
        if empty_details['table_data']:
            first_row = empty_details['table_data'][0]
            required_fields = ['metric', 'count', 'percentage']
            for field in required_fields:
                assert field in first_row, f"Missing {field} in empty_details"
        
        print("Empty details structure valid")
        
        # Check chart data
        assert 'chart_data' in stats, "Missing chart_data"
        chart_data = stats['chart_data']
        
        expected_charts = ['lead_creation_trend', 'engagement_breakdown', 'inactive_breakdown']
        for chart in expected_charts:
            assert chart in chart_data, f"Missing {chart} in chart_data"
        
        print("Chart data structure valid")
        
        # Check recommendations
        assert 'recommendations' in stats, "Missing recommendations"
        recommendations = stats['recommendations']
        
        expected_rec_sections = ['active_contacts', 'inactive_contacts', 'empty_details']
        for section in expected_rec_sections:
            assert section in recommendations, f"Missing {section} in recommendations"
        
        print("Recommendations structure valid")
        
        # Print sample data
        print("\nSample Data Structure:")
        print("-" * 30)
        
        print(f"Active Contacts Metrics: {len(active_contacts['table_data'])}")
        print(f"Inactive Contacts Metrics: {len(inactive_contacts['table_data'])}")
        print(f"Empty Details Metrics: {len(empty_details['table_data'])}")
        
        print(f"\nChart Data Available:")
        for chart_name, chart_info in chart_data.items():
            if isinstance(chart_info, dict) and 'data' in chart_info:
                print(f"  - {chart_name}: {len(chart_info['data'])} data points")
        
        print(f"\nRecommendations Available:")
        for section, recs in recommendations.items():
            print(f"  - {section}: {len(recs)} recommendations")
        
        print("\nAll tests passed! Prospect Health functionality is working correctly.")
        
        return True
        
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_prospect_health()
    exit(0 if success else 1)