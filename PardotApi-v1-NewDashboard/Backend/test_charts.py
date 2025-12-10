#!/usr/bin/env python3

import json
from services.database_health_service import DatabaseHealthAnalyzer

def test_chart_format():
    """Test chart data format"""
    
    # Create mock analyzer
    class MockAnalyzer(DatabaseHealthAnalyzer):
        def __init__(self):
            pass
        
        def get_prospects_count(self, filters=None):
            return 1000
        
        def get_all_prospects_data(self):
            return [{'id': i, 'email': f'test{i}@example.com', 'createdAt': '2024-01-01T00:00:00Z', 'updatedAt': '2024-01-01T00:00:00Z'} for i in range(100)]
        
        def count_prospects_by_date(self, prospects, date_field, cutoff_date):
            return len(prospects) // 10
        
        def count_marketable_prospects(self, prospects):
            return int(len(prospects) * 0.8)
        
        def get_inactive_contact_metrics_local(self, prospects, six_months_ago, twelve_months_ago, two_years_ago):
            return {
                'inactive_leads': 50,
                'unsubscribed_leads': 30,
                'inactive_6m': 50,
                'inactive_12m': 80,
                'inactive_2y': 120,
                'delivered_not_opened': 150,
                'opened_not_clicked': 100
            }
        
        def analyze_data_quality(self):
            return {'quality_table': []}
        
        def analyze_scoring_issues(self, prospects):
            return {'scoring_table': []}
        
        def generate_comprehensive_recommendations(self, *args):
            return {'active_contacts': [], 'inactive_contacts': [], 'empty_details': [], 'scoring_issues': []}
    
    # Test chart generation
    analyzer = MockAnalyzer()
    stats = analyzer.get_comprehensive_stats()
    
    print("Chart Data Structure:")
    print(f"Type: {type(stats['chart_data'])}")
    print(f"Length: {len(stats['chart_data']) if isinstance(stats['chart_data'], list) else 'Not a list'}")
    
    if isinstance(stats['chart_data'], list):
        for i, chart in enumerate(stats['chart_data']):
            print(f"\nChart {i+1}:")
            print(f"  ID: {chart.get('id', 'No ID')}")
            print(f"  Type: {chart.get('type', 'No Type')}")
            print(f"  Title: {chart.get('title', 'No Title')}")
            print(f"  Has Data: {'data' in chart}")
            if 'data' in chart and 'datasets' in chart['data']:
                datasets = chart['data']['datasets']
                if datasets and len(datasets) > 0:
                    data_values = datasets[0].get('data', [])
                    print(f"  Data Values: {data_values}")
                    print(f"  Data Count: {len(data_values)}")
    
    print("\nChart data format test completed!")
    return stats

if __name__ == "__main__":
    test_chart_format()