"""
Analysis Results Page for Merger Book MVP
Displays merger matches, synergy analysis, and detailed company comparisons
"""

import streamlit as st
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Any

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.config import Config
from utils.database import DatabaseManager
from utils.matching_engine import MatchingEngine
from utils.ai_analyzer import AIAnalyzer

# Page configuration
st.set_page_config(
    page_title="Analysis Results - Merger Book",
    page_icon="🔍",
    layout="wide"
)

# Initialize components
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager(Config.DATABASE_PATH)

if 'matching_engine' not in st.session_state:
    st.session_state.matching_engine = MatchingEngine()

if 'ai_analyzer' not in st.session_state:
    st.session_state.ai_analyzer = AIAnalyzer()

def main():
    """Main analysis results page function"""
    
    # Check authentication
    if not st.session_state.get('user_id'):
        st.error("Please login to access this page")
        if st.button("Go to Login"):
            st.switch_page("main.py")
        return
    
    st.title("🔍 Merger Analysis Results")
    st.markdown("Discover potential merger partners and analyze synergy opportunities for your business.")
    
    # Get user companies
    user_companies = get_user_companies()
    
    if not user_companies:
        st.info("No companies found. Please upload a business document first.")
        if st.button("📤 Upload Document"):
            st.switch_page("pages/1_📤_Upload_Documents.py")
        return
    
    # Company selection
    selected_company = select_company(user_companies)
    
    if selected_company:
        # Display company overview
        display_company_overview(selected_company)
        
        # Find and display matches
        st.markdown("---")
        display_merger_matches(selected_company)

def get_user_companies() -> List[Dict]:
    """Get companies for the current user"""
    companies = st.session_state.db.get_companies_by_user(st.session_state.user_id)
    return [c for c in companies if c['data_source'] == 'user_upload']

def select_company(user_companies: List[Dict]) -> Dict:
    """Company selection interface"""
    
    st.subheader("🏢 Select Company for Analysis")
    
    if len(user_companies) == 1:
        selected_company = user_companies[0]
        st.info(f"Analyzing: **{selected_company['company_name']}**")
        return selected_company
    
    # Multiple companies - show selection
    company_options = {f"{c['company_name']} ({c['industry_classification']})": c for c in user_companies}
    
    selected_name = st.selectbox(
        "Choose a company to analyze:",
        options=list(company_options.keys()),
        help="Select which of your companies you want to find merger partners for"
    )
    
    return company_options[selected_name] if selected_name else None

def display_company_overview(company: Dict):
    """Display overview of selected company"""
    
    st.subheader(f"📊 Company Overview: {company['company_name']}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Industry", company.get('industry_classification', 'N/A'))
    
    with col2:
        revenue = company.get('revenue', 0)
        if revenue:
            st.metric("Revenue", f"${revenue:,.0f}")
        else:
            st.metric("Revenue", "N/A")
    
    with col3:
        employees = company.get('employee_count', 0)
        if employees:
            st.metric("Employees", f"{employees:,}")
        else:
            st.metric("Employees", "N/A")
    
    with col4:
        st.metric("Data Source", "User Upload")
    
    # Business description
    if company.get('business_description'):
        st.write("**Business Description:**")
        st.write(company['business_description'])

def display_merger_matches(user_company: Dict):
    """Find and display potential merger matches"""
    
    st.subheader("🎯 Potential Merger Partners")
    
    # Get all companies for matching (excluding user companies)
    all_companies = st.session_state.db.get_companies_by_user(st.session_state.user_id)
    candidate_companies = [c for c in all_companies if c['data_source'] == 'market_data']
    
    if not candidate_companies:
        st.warning("No market data companies available for matching. Please ensure financial data integration is working.")
        return
    
    # Find matches
    with st.spinner("🔍 Finding potential merger partners..."):
        matches = st.session_state.matching_engine.find_matches(user_company, candidate_companies)
    
    if not matches:
        st.info("No suitable merger candidates found. Try adjusting your search criteria or upload more detailed business information.")
        return
    
    # Display match statistics
    display_match_statistics(matches)
    
    # Display individual matches
    st.markdown("### 📋 Match Results")
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_score = st.slider("Minimum Match Score", 0.0, 1.0, 0.3, 0.1)
    
    with col2:
        match_type_filter = st.selectbox("Match Type", ["All", "Horizontal", "Vertical"])
    
    with col3:
        max_results = st.number_input("Max Results", 1, 50, 10)
    
    # Filter matches
    filtered_matches = filter_matches(matches, min_score, match_type_filter, max_results)
    
    # Display matches
    for i, match in enumerate(filtered_matches):
        display_match_card(match, i)

def display_match_statistics(matches: List[Dict]):
    """Display overall match statistics"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Matches", len(matches))
    
    with col2:
        avg_score = sum(m['match_score'] for m in matches) / len(matches) if matches else 0
        st.metric("Avg Match Score", f"{avg_score:.2f}")
    
    with col3:
        horizontal_count = sum(1 for m in matches if m['match_type'] == 'horizontal')
        st.metric("Horizontal Matches", horizontal_count)
    
    with col4:
        vertical_count = sum(1 for m in matches if m['match_type'] == 'vertical')
        st.metric("Vertical Matches", vertical_count)
    
    # Match score distribution chart
    if matches:
        scores = [m['match_score'] for m in matches]
        fig = px.histogram(
            x=scores,
            nbins=10,
            title="Match Score Distribution",
            labels={'x': 'Match Score', 'y': 'Number of Matches'}
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def filter_matches(matches: List[Dict], min_score: float, match_type: str, max_results: int) -> List[Dict]:
    """Filter matches based on criteria"""
    
    filtered = matches
    
    # Filter by score
    filtered = [m for m in filtered if m['match_score'] >= min_score]
    
    # Filter by type
    if match_type != "All":
        filtered = [m for m in filtered if m['match_type'].lower() == match_type.lower()]
    
    # Limit results
    return filtered[:max_results]

def display_match_card(match: Dict, index: int):
    """Display individual match card"""
    
    candidate = match['candidate_company']
    
    with st.expander(f"🏢 {candidate['company_name']} - Score: {match['match_score']:.2f}"):
        
        # Basic info
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Industry:** {candidate.get('industry_classification', 'N/A')}")
            st.write(f"**Match Type:** {match['match_type'].title()}")
            st.write(f"**Match Score:** {match['match_score']:.2f}")
            
            if candidate.get('ticker_symbol'):
                st.write(f"**Ticker:** {candidate['ticker_symbol']}")
        
        with col2:
            revenue = candidate.get('revenue', 0)
            if revenue:
                st.write(f"**Revenue:** ${revenue:,.0f}")
            
            employees = candidate.get('employee_count', 0)
            if employees:
                st.write(f"**Employees:** {employees:,}")
            
            if candidate.get('geographic_markets'):
                st.write(f"**Markets:** {candidate['geographic_markets']}")
        
        # Business description
        if candidate.get('business_description'):
            st.write("**Business Description:**")
            st.write(candidate['business_description'])
        
        # Similarity breakdown
        if 'similarity_factors' in match:
            display_similarity_breakdown(match['similarity_factors'])
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"🔬 Detailed Analysis", key=f"analyze_{index}"):
                perform_detailed_analysis(match)
        
        with col2:
            if st.button(f"💾 Save Match", key=f"save_{index}"):
                save_match_to_database(match)

def display_similarity_breakdown(similarity_factors: Dict[str, float]):
    """Display similarity factor breakdown"""
    
    st.write("**Similarity Breakdown:**")
    
    factors = {
        'Industry': similarity_factors.get('industry_similarity', 0),
        'Business': similarity_factors.get('business_similarity', 0),
        'Geographic': similarity_factors.get('geographic_similarity', 0),
        'Size': similarity_factors.get('size_similarity', 0),
        'Strategic': similarity_factors.get('strategic_similarity', 0)
    }
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=list(factors.values()),
        theta=list(factors.keys()),
        fill='toself',
        name='Similarity'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=False,
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

def perform_detailed_analysis(match: Dict):
    """Perform detailed synergy analysis"""
    
    st.subheader("🔬 Detailed Synergy Analysis")
    
    with st.spinner("Analyzing synergies..."):
        # Get user company data
        user_companies = get_user_companies()
        user_company = user_companies[0] if user_companies else {}
        
        # Perform AI synergy analysis
        synergy_analysis = st.session_state.ai_analyzer.analyze_synergies(
            user_company, match['candidate_company']
        )
    
    if synergy_analysis:
        display_synergy_analysis(synergy_analysis)
    else:
        st.error("Failed to perform synergy analysis")

def display_synergy_analysis(analysis: Dict):
    """Display detailed synergy analysis results"""
    
    # Overall scores
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Score", f"{analysis.get('overall_match_score', 0):.2f}")
    
    with col2:
        st.metric("Confidence", f"{analysis.get('confidence_score', 0):.2f}")
    
    with col3:
        st.metric("Match Type", analysis.get('match_type', 'Unknown').title())
    
    # Synergy predictions
    synergies = analysis.get('synergy_predictions', {})
    
    if synergies:
        tab1, tab2, tab3 = st.tabs(["💰 Revenue Synergies", "💸 Cost Synergies", "🎯 Strategic Synergies"])
        
        with tab1:
            revenue_synergies = synergies.get('revenue_synergies', {})
            for key, value in revenue_synergies.items():
                if value:
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        with tab2:
            cost_synergies = synergies.get('cost_synergies', {})
            for key, value in cost_synergies.items():
                if value:
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        with tab3:
            strategic_synergies = synergies.get('strategic_synergies', {})
            for key, value in strategic_synergies.items():
                if value:
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    # Risk assessment
    risks = analysis.get('risk_assessment', {})
    if risks:
        st.subheader("⚠️ Risk Assessment")
        for key, value in risks.items():
            if value:
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    # Key value drivers
    drivers = analysis.get('key_value_drivers', [])
    if drivers:
        st.subheader("🚀 Key Value Drivers")
        for driver in drivers:
            st.write(f"• {driver}")

def save_match_to_database(match: Dict):
    """Save match to database"""
    
    try:
        # Get user company
        user_companies = get_user_companies()
        if not user_companies:
            st.error("No user company found")
            return
        
        user_company = user_companies[0]
        
        match_data = {
            'user_company_id': user_company['company_id'],
            'candidate_company_id': match['candidate_company']['company_id'],
            'match_score': match['match_score'],
            'match_type': match['match_type'],
            'synergy_predictions': {},  # Will be filled by detailed analysis
            'risk_assessment': {},
            'confidence_score': match.get('confidence_score', match['match_score'])
        }
        
        match_id = st.session_state.db.create_match(match_data)
        st.success(f"Match saved successfully! (ID: {match_id})")
        
    except Exception as e:
        st.error(f"Error saving match: {str(e)}")

if __name__ == "__main__":
    main()

