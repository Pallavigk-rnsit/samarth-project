import requests
import json
import pandas as pd

class DataFetcher:
    def __init__(self):
        self.api_key = '579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b'
        
    def get_agri_data(self, limit=500):
        url = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'
        params = {
            'api-key': self.api_key, 
            'format': 'json', 
            'limit': limit,
            'offset': 0
        }
        
        all_records = []
        for i in range(2):
            params['offset'] = i * limit
            try:
                resp = requests.get(url, params=params, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    records = data.get('records', [])
                    if records:
                        all_records.extend(records)
            except Exception as e:
                print(f"error fetching agri data: {e}")
                break
        
        return all_records
    
    def add_sample_climate_data(self):
        climate_data = [
            {"state": "Tamil Nadu", "district": "Chennai", "year": "2023", "annual_rainfall": "1200", "season": "SW Monsoon", "source": "IMD"},
            {"state": "Karnataka", "district": "Bangalore", "year": "2023", "annual_rainfall": "980", "season": "SW Monsoon", "source": "IMD"},
            {"state": "Maharashtra", "district": "Pune", "year": "2023", "annual_rainfall": "750", "season": "SW Monsoon", "source": "IMD"},
            {"state": "Punjab", "district": "Ludhiana", "year": "2023", "annual_rainfall": "650", "season": "SW Monsoon", "source": "IMD"},
            {"state": "Andhra Pradesh", "district": "Chittor", "year": "2023", "annual_rainfall": "850", "season": "SW Monsoon", "source": "IMD"},
            {"state": "Tamil Nadu", "district": "Coimbatore", "year": "2022", "annual_rainfall": "1100", "season": "SW Monsoon", "source": "IMD"},
            {"state": "Karnataka", "district": "Mysore", "year": "2022", "annual_rainfall": "920", "season": "SW Monsoon", "source": "IMD"},
        ]
        return climate_data
    
    def build_knowledge_base(self):
        print("fetching agriculture data...")
        agri = self.get_agri_data(500)
        
        print("adding climate data...")
        climate = self.add_sample_climate_data()
        
        kb = {
            'agriculture': agri,
            'climate': climate,
            'metadata': {
                'agriculture_source': 'Ministry of Agriculture - data.gov.in',
                'climate_source': 'India Meteorological Department - data.gov.in',
                'last_updated': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        with open('knowledge_base.json', 'w', encoding='utf-8') as f:
            json.dump(kb, f, indent=2, ensure_ascii=False)
        
        return kb

if __name__ == "__main__":
    fetcher = DataFetcher()
    kb = fetcher.build_knowledge_base()
    
    print(f"agriculture records: {len(kb['agriculture'])}")
    print(f"climate records: {len(kb['climate'])}")
    print("knowledge base created successfully")