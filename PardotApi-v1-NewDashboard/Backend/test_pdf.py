#!/usr/bin/env python3

"""
Test script to verify PDF generation works correctly
"""

from services.pdf_service import create_prospect_pdf_report

def test_prospect_pdf():
    """Test prospect PDF generation with sample data"""
    
    # Test with new format (summary structure)
    sample_data_new = {
        'summary': {
            'total_prospects': 1000,
            'duplicate_groups': 25,
            'inactive_prospects': 150,
            'missing_fields_prospects': 75,
            'scoring_issues_prospects': 30
        }
    }
    
    # Test with legacy format
    sample_data_legacy = {
        'total_prospects': 1000,
        'duplicates': {'count': 25},
        'inactive_prospects': {'count': 150},
        'missing_fields': {'count': 75},
        'scoring_issues': {'count': 30}
    }
    
    print("Testing new format...")
    try:
        buffer1 = create_prospect_pdf_report(sample_data_new)
        print(f"SUCCESS: New format PDF generated successfully. Size: {len(buffer1.getvalue())} bytes")
    except Exception as e:
        print(f"ERROR: New format failed: {str(e)}")
    
    print("Testing legacy format...")
    try:
        buffer2 = create_prospect_pdf_report(sample_data_legacy)
        print(f"SUCCESS: Legacy format PDF generated successfully. Size: {len(buffer2.getvalue())} bytes")
    except Exception as e:
        print(f"ERROR: Legacy format failed: {str(e)}")
    
    print("PDF generation test completed!")

if __name__ == "__main__":
    test_prospect_pdf()