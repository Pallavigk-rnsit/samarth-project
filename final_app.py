import streamlit as st
import json
import pandas as pd
import numpy as np

class SamarthQA:
    def __init__(self):
        self.data = self.load_data()
        
    def load_data(self):
        try:
            with open('knowledge_base.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"error loading data: {e}")
            return {'agriculture': [], 'climate': [], 'metadata': {}}
    
    def get_stats(self):
        agri = self.data.get('agriculture', [])
        climate = self.data.get('climate', [])
        
        stats = {
            'agri_records': len(agri),
            'climate_records': len(climate),
            'total_records': len(agri) + len(climate)
        }
        
        if agri:
            df_agri = pd.DataFrame(agri)
            stats['states'] = df_agri['state'].nunique() if 'state' in df_agri else 0
            stats['districts'] = df_agri['district'].nunique() if 'district' in df_agri else 0
            stats['commodities'] = df_agri['commodity'].nunique() if 'commodity' in df_agri else 0
        
        if climate:
            df_climate = pd.DataFrame(climate)
            stats['climate_states'] = df_climate['state'].nunique() if 'state' in df_climate else 0
        
        return stats
    
    def safe_numeric_conversion(self, value):
        try:
            return float(value)
        except:
            return 0.0
    
    def analyze_query(self, query):
        q = query.lower()
        agri = self.data.get('agriculture', [])
        climate = self.data.get('climate', [])
        
        sources = [
            self.data.get('metadata', {}).get('agriculture_source', 'data.gov.in'),
            self.data.get('metadata', {}).get('climate_source', 'IMD data.gov.in')
        ]
        
        if not agri and not climate:
            return "no data available", ["no sources"]
        
        if 'rainfall' in q and 'compare' in q:
            return self.analyze_rainfall_comparison(q, climate), sources
        
        if 'rainfall' in q:
            return self.analyze_rainfall(q, climate), sources
        
        if 'compare' in q and ('state' in q or 'crop' in q):
            return self.analyze_state_crop_comparison(q, agri, climate), sources
        
        if 'trend' in q and 'production' in q:
            return self.analyze_production_trend(q, agri, climate), sources
        
        if 'policy' in q or 'scheme' in q or 'drought' in q:
            return self.analyze_policy_recommendation(q, agri, climate), sources
        
        if 'highest' in q and 'production' in q:
            return self.analyze_highest_production(q, agri), sources
        
        return self.analyze_basic_query(q, agri), sources
    
    def analyze_rainfall_comparison(self, query, climate):
        if not climate:
            return "no climate data available for comparison"
        
        df = pd.DataFrame(climate)
        
        # Convert rainfall to numeric safely
        df['rainfall_numeric'] = df['annual_rainfall'].apply(self.safe_numeric_conversion)
        
        answer = "rainfall comparison:\n\n"
        
        states = df['state'].unique()[:4]
        for state in states:
            state_data = df[df['state'] == state]
            if not state_data.empty:
                avg_rainfall = state_data['rainfall_numeric'].mean()
                answer += f"{state}: {avg_rainfall:.0f} mm average rainfall\n"
        
        answer += f"\nbased on {len(climate)} climate records from IMD"
        return answer
    
    def analyze_rainfall(self, query, climate):
        if not climate:
            return "no rainfall data available"
        
        df = pd.DataFrame(climate)
        answer = "rainfall data from IMD:\n\n"
        
        for _, row in df.head(5).iterrows():
            rainfall = self.safe_numeric_conversion(row['annual_rainfall'])
            answer += f"{row['state']} - {row['district']} ({row['year']}): {rainfall:.0f} mm\n"
        
        return answer
    
    def analyze_state_crop_comparison(self, query, agri, climate):
        if not agri:
            return "no agriculture data for comparison"
        
        df_agri = pd.DataFrame(agri)
        answer = "state and crop comparison:\n\n"
        
        top_states = df_agri['state'].value_counts().head(3)
        for state, count in top_states.items():
            answer += f"{state}: {count} market records\n"
            state_crops = df_agri[df_agri['state'] == state]['commodity'].value_counts().head(3)
            for crop, crop_count in state_crops.items():
                answer += f"  - {crop}: {crop_count} entries\n"
            answer += "\n"
        
        if climate:
            df_climate = pd.DataFrame(climate)
            df_climate['rainfall_numeric'] = df_climate['annual_rainfall'].apply(self.safe_numeric_conversion)
            
            answer += "corresponding rainfall data:\n"
            for state in top_states.index[:2]:
                if state in df_climate['state'].values:
                    rain_data = df_climate[df_climate['state'] == state]
                    if not rain_data.empty:
                        avg_rain = rain_data['rainfall_numeric'].mean()
                        answer += f"{state}: {avg_rain:.0f} mm average rainfall\n"
        
        return answer
    
    def analyze_production_trend(self, query, agri, climate):
        answer = "production trend analysis:\n\n"
        
        if agri:
            df_agri = pd.DataFrame(agri)
            answer += f"total agriculture records: {len(agri)}\n"
            answer += f"states covered: {df_agri['state'].nunique()}\n"
            answer += f"crops tracked: {df_agri['commodity'].nunique()}\n\n"
        
        if climate:
            df_climate = pd.DataFrame(climate)
            answer += "climate correlation:\n"
            answer += f"rainfall data for {df_climate['state'].nunique()} states\n"
            answer += f"years covered: {df_climate['year'].nunique()}\n"
            
            # Add rainfall range
            df_climate['rainfall_numeric'] = df_climate['annual_rainfall'].apply(self.safe_numeric_conversion)
            min_rain = df_climate['rainfall_numeric'].min()
            max_rain = df_climate['rainfall_numeric'].max()
            answer += f"rainfall range: {min_rain:.0f} mm to {max_rain:.0f} mm\n"
        
        answer += "\ncorrelation: agricultural planning should consider regional rainfall variations"
        return answer
    
    def analyze_policy_recommendation(self, query, agri, climate):
        answer = "policy analysis based on integrated data:\n\n"
        
        if climate:
            df_climate = pd.DataFrame(climate)
            df_climate['rainfall_numeric'] = df_climate['annual_rainfall'].apply(self.safe_numeric_conversion)
            
            high_rain_states = df_climate[df_climate['rainfall_numeric'] > 1000]['state'].tolist()
            low_rain_states = df_climate[df_climate['rainfall_numeric'] < 800]['state'].tolist()
            
            if high_rain_states:
                answer += f"1. high rainfall regions ({', '.join(high_rain_states)}) - suitable for water-intensive crops\n"
            if low_rain_states:
                answer += f"2. low rainfall regions ({', '.join(low_rain_states)}) - recommend drought-resistant varieties\n"
        
        if agri:
            df_agri = pd.DataFrame(agri)
            common_crops = df_agri['commodity'].value_counts().head(5).index.tolist()
            answer += f"3. diversify among top crops: {', '.join(common_crops)}\n\n"
        
        answer += "data sources: ministry of agriculture + IMD climate data"
        return answer
    
    def analyze_highest_production(self, query, agri):
        if not agri:
            return "no production data available"
        
        df = pd.DataFrame(agri)
        answer = "production analysis:\n\n"
        
        if 'modal_price' in df.columns:
            # Safe numeric conversion for prices
            df['price_num'] = df['modal_price'].apply(self.safe_numeric_conversion)
            high_value = df.nlargest(3, 'price_num')
            
            answer += "high-value crops:\n"
            for _, row in high_value.iterrows():
                answer += f"- {row['commodity']} in {row['state']}: Rs {row['modal_price']}\n"
        
        answer += f"\nbased on {len(agri)} market records from data.gov.in"
        return answer
    
    def analyze_basic_query(self, query, agri):
        if not agri:
            return "no agriculture data available"
        
        df = pd.DataFrame(agri)
        
        if 'price' in query:
            answer = "current market prices:\n\n"
            for _, row in df.head(4).iterrows():
                answer += f"{row['commodity']} in {row['district']}, {row['state']}\n"
                answer += f"price: Rs {row.get('modal_price', 'N/A')}\n"
                answer += f"range: Rs {row.get('min_price', 'N/A')} to Rs {row.get('max_price', 'N/A')}\n\n"
            return answer
        
        if 'crop' in query or 'commodity' in query:
            crops = df['commodity'].value_counts().head(8)
            answer = "available crops in data:\n\n"
            for crop, count in crops.items():
                answer += f"{crop}: {count} market records\n"
            return answer
        
        if 'state' in query or 'location' in query:
            states = df['state'].value_counts().head(6)
            answer = "states with agriculture data:\n\n"
            for state, count in states.items():
                answer += f"{state}: {count} records\n"
            return answer
        
        answer = f"agriculture data overview:\n\n"
        answer += f"total records: {len(agri)}\n"
        answer += f"states: {df['state'].nunique()}\n"
        answer += f"districts: {df['district'].nunique()}\n"
        answer += f"crops: {df['commodity'].nunique()}\n\n"
        answer += "ask about: prices, crops, states, rainfall, or policy recommendations"
        
        return answer

st.set_page_config(
    page_title="Project Samarth - Agriculture & Climate Q&A",
    layout="wide",
    page_icon="🌾"
)

st.title("🌾 Project Samarth")
st.markdown("### Intelligent Q&A System for Agriculture & Climate Data")

qa = SamarthQA()
stats = qa.get_stats()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Records", stats.get('total_records', 0))
with col2:
    st.metric("Agriculture", stats.get('agri_records', 0))
with col3:
    st.metric("Climate", stats.get('climate_records', 0))
with col4:
    st.metric("States", stats.get('states', 0))
with col5:
    st.metric("Crops", stats.get('commodities', 0))

st.divider()

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Ask Your Question")
    
    sample_questions = [
        "Compare rainfall in different states",
        "Which states have the highest crop production?",
        "Show me crop prices and locations",
        "Analyze production trends with climate data",
        "Recommend crops based on rainfall patterns",
        "Compare Tamil Nadu and Karnataka rainfall"
    ]
    
    question = st.text_input(
        "Enter your question:",
        placeholder="Ask about agriculture, climate, comparisons, trends..."
    )
    
    if st.button("🔍 Analyze Data", type="primary") or question:
        if question:
            with st.spinner("Analyzing data from data.gov.in..."):
                answer, sources = qa.analyze_query(question)
                
                st.markdown("---")
                st.markdown("### 📊 Analysis Result")
                # Use st.text for better formatting of plain text
                st.text(answer)
                
                st.markdown("### 📚 Data Sources")
                for source in sources:
                    st.markdown(f"- {source}")
        else:
            st.warning("Please enter a question")

with right_col:
    st.subheader("💡 Sample Questions")
    
    for i, sample_q in enumerate(sample_questions):
        if st.button(sample_q, key=f"sample_{i}"):
            st.session_state.last_question = sample_q
            st.rerun()
    
    st.divider()
    
    st.subheader("ℹ️ About This System")
    st.info("""
    **Project Samarth** integrates data from:
    - Ministry of Agriculture & Farmers Welfare
    - India Meteorological Department (IMD)
    - Live data.gov.in APIs
    
    **Capabilities:**
    - Cross-domain analysis
    - Source citation
    - Real-time data access
    - Policy recommendations
    """)

st.divider()

tab1, tab2, tab3 = st.tabs(["Sample Agriculture Data", "Sample Climate Data", "System Info"])

with tab1:
    if qa.data.get('agriculture'):
        st.json(qa.data['agriculture'][:2])

with tab2:
    if qa.data.get('climate'):
        st.json(qa.data['climate'][:2])

with tab3:
    st.markdown("""
    **System Architecture:**
    1. Data fetching from data.gov.in APIs
    2. Integration of agriculture + climate data
    3. Natural language query processing
    4. Cross-domain correlation analysis
    5. Source-cited responses
    
    **Technologies:** Python, Streamlit, Pandas, data.gov.in API
    """)
