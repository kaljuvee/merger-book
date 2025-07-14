"""
Company Database Page for Merger Book MVP
Browse and search through available companies for merger analysis
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.config import Config
from utils.database import DatabaseManager

# Page configuration
st.set_page_config(
    page_title="Company Database - Merger Book",
    page_icon="🏢",
    layout="wide"
)

# Initialize components
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager(Config.DATABASE_PATH)

def main():
    """Main company database page function"""
    
    # Check authentication
    if not st.session_state.get('user_id'):
        st.error("Please login to access this page")
        if st.button("Go to Login"):
            st.switch_page("main.py")
        return
    
    st.title("🏢 Company Database")
    st.markdown("Browse and explore companies available for merger analysis.")
    
    # Get all companies
    companies = st.session_state.db.get_companies_by_user(st.session_state.user_id)
    
    if not companies:
        st.info("No companies in database. Upload business documents or integrate financial data to populate the database.")
        if st.button("📤 Upload Document"):
            st.switch_page("pages/1_📤_Upload_Documents.py")
        return
    
    # Separate user companies from market data
    user_companies = [c for c in companies if c['data_source'] == 'user_upload']
    market_companies = [c for c in companies if c['data_source'] == 'market_data']
    
    # Display statistics
    display_database_statistics(user_companies, market_companies)
    
    # Company browser
    st.markdown("---")
    display_company_browser(companies)

def display_database_statistics(user_companies: List[Dict], market_companies: List[Dict]):
    """Display database statistics and overview"""
    
    st.subheader("📊 Database Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Your Companies", len(user_companies))
    
    with col2:
        st.metric("Market Companies", len(market_companies))
    
    with col3:
        st.metric("Total Companies", len(user_companies) + len(market_companies))
    
    with col4:
        # Calculate average revenue if available
        all_companies = user_companies + market_companies
        revenues = [c.get('revenue', 0) for c in all_companies if c.get('revenue', 0) > 0]
        avg_revenue = sum(revenues) / len(revenues) if revenues else 0
        if avg_revenue > 0:
            st.metric("Avg Revenue", f"${avg_revenue:,.0f}")
        else:
            st.metric("Avg Revenue", "N/A")
    
    # Industry distribution chart
    if user_companies or market_companies:
        display_industry_distribution(user_companies + market_companies)

def display_industry_distribution(companies: List[Dict]):
    """Display industry distribution chart"""
    
    # Count companies by industry
    industry_counts = {}
    for company in companies:
        industry = company.get('industry_classification', 'Unknown')
        industry_counts[industry] = industry_counts.get(industry, 0) + 1
    
    if industry_counts:
        # Create pie chart
        fig = px.pie(
            values=list(industry_counts.values()),
            names=list(industry_counts.keys()),
            title="Industry Distribution"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def display_company_browser(companies: List[Dict]):
    """Display company browser with search and filters"""
    
    st.subheader("🔍 Browse Companies")
    
    # Search and filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search companies", placeholder="Enter company name or keyword")
    
    with col2:
        # Get unique industries
        industries = list(set([c.get('industry_classification', 'Unknown') for c in companies]))
        industries.sort()
        selected_industry = st.selectbox("Industry Filter", ["All"] + industries)
    
    with col3:
        data_source_filter = st.selectbox("Data Source", ["All", "Your Companies", "Market Data"])
    
    # Apply filters
    filtered_companies = filter_companies(companies, search_term, selected_industry, data_source_filter)
    
    # Display results count
    st.write(f"**Showing {len(filtered_companies)} companies**")
    
    # Display companies
    if filtered_companies:
        display_company_grid(filtered_companies)
    else:
        st.info("No companies match your search criteria.")

def filter_companies(companies: List[Dict], search_term: str, industry: str, data_source: str) -> List[Dict]:
    """Filter companies based on search criteria"""
    
    filtered = companies
    
    # Search term filter
    if search_term:
        search_lower = search_term.lower()
        filtered = [
            c for c in filtered 
            if (search_lower in c.get('company_name', '').lower() or
                search_lower in c.get('business_description', '').lower() or
                search_lower in c.get('industry_classification', '').lower())
        ]
    
    # Industry filter
    if industry != "All":
        filtered = [c for c in filtered if c.get('industry_classification') == industry]
    
    # Data source filter
    if data_source == "Your Companies":
        filtered = [c for c in filtered if c.get('data_source') == 'user_upload']
    elif data_source == "Market Data":
        filtered = [c for c in filtered if c.get('data_source') == 'market_data']
    
    return filtered

def display_company_grid(companies: List[Dict]):
    """Display companies in a grid layout"""
    
    # Sort companies by name
    companies.sort(key=lambda x: x.get('company_name', ''))
    
    # Display in grid format
    for i in range(0, len(companies), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            if i < len(companies):
                display_company_card(companies[i])
        
        with col2:
            if i + 1 < len(companies):
                display_company_card(companies[i + 1])

def display_company_card(company: Dict):
    """Display individual company card"""
    
    # Determine card color based on data source
    if company.get('data_source') == 'user_upload':
        border_color = "#1f77b4"  # Blue for user companies
        source_icon = "👤"
    else:
        border_color = "#ff7f0e"  # Orange for market data
        source_icon = "📈"
    
    with st.container():
        # Company header
        st.markdown(f"""
        <div style="border-left: 4px solid {border_color}; padding-left: 10px; margin-bottom: 10px;">
            <h4>{source_icon} {company.get('company_name', 'Unknown Company')}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Company details
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Industry:** {company.get('industry_classification', 'N/A')}")
            
            revenue = company.get('revenue', 0)
            if revenue:
                st.write(f"**Revenue:** ${revenue:,.0f}")
            else:
                st.write("**Revenue:** N/A")
        
        with col2:
            employees = company.get('employee_count', 0)
            if employees:
                st.write(f"**Employees:** {employees:,}")
            else:
                st.write("**Employees:** N/A")
            
            if company.get('ticker_symbol'):
                st.write(f"**Ticker:** {company['ticker_symbol']}")
        
        # Business description
        description = company.get('business_description', '')
        if description:
            # Truncate long descriptions
            if len(description) > 150:
                description = description[:150] + "..."
            st.write(f"**Description:** {description}")
        
        # Geographic markets
        markets = company.get('geographic_markets', '')
        if markets:
            st.write(f"**Markets:** {markets}")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👁️ View Details", key=f"view_{company['company_id']}"):
                display_company_details(company)
        
        with col2:
            if company.get('data_source') == 'market_data':
                if st.button("🔍 Analyze Match", key=f"match_{company['company_id']}"):
                    analyze_company_match(company)
        
        with col3:
            if st.button("📊 Compare", key=f"compare_{company['company_id']}"):
                st.session_state.selected_company_for_comparison = company
                st.info("Company selected for comparison. Select another company to compare.")
        
        st.markdown("---")

def display_company_details(company: Dict):
    """Display detailed company information in a modal-like expander"""
    
    with st.expander(f"📋 Detailed Information: {company['company_name']}", expanded=True):
        
        # Basic information
        st.subheader("Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Company Name:** {company.get('company_name', 'N/A')}")
            st.write(f"**Industry:** {company.get('industry_classification', 'N/A')}")
            st.write(f"**Data Source:** {company.get('data_source', 'N/A').replace('_', ' ').title()}")
            
            if company.get('ticker_symbol'):
                st.write(f"**Stock Ticker:** {company['ticker_symbol']}")
        
        with col2:
            revenue = company.get('revenue', 0)
            if revenue:
                st.write(f"**Revenue:** ${revenue:,.0f}")
            
            employees = company.get('employee_count', 0)
            if employees:
                st.write(f"**Employees:** {employees:,}")
            
            st.write(f"**Last Updated:** {company.get('last_updated', 'N/A')}")
        
        # Business description
        if company.get('business_description'):
            st.subheader("Business Description")
            st.write(company['business_description'])
        
        # Geographic markets
        if company.get('geographic_markets'):
            st.subheader("Geographic Markets")
            st.write(company['geographic_markets'])
        
        # Financial metrics (if available)
        financial_metrics = company.get('financial_metrics')
        if financial_metrics and financial_metrics != '{}':
            st.subheader("Financial Metrics")
            if isinstance(financial_metrics, str):
                import json
                try:
                    financial_metrics = json.loads(financial_metrics)
                except:
                    financial_metrics = {}
            
            if financial_metrics:
                for key, value in financial_metrics.items():
                    if value:
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Strategic objectives (if available)
        strategic_objectives = company.get('strategic_objectives')
        if strategic_objectives and strategic_objectives != '[]':
            st.subheader("Strategic Objectives")
            if isinstance(strategic_objectives, str):
                import json
                try:
                    strategic_objectives = json.loads(strategic_objectives)
                except:
                    strategic_objectives = []
            
            if strategic_objectives:
                for objective in strategic_objectives:
                    st.write(f"• {objective}")

def analyze_company_match(company: Dict):
    """Analyze match potential with user companies"""
    
    # Get user companies
    user_companies = [c for c in st.session_state.db.get_companies_by_user(st.session_state.user_id) 
                     if c['data_source'] == 'user_upload']
    
    if not user_companies:
        st.error("No user companies found for matching analysis.")
        return
    
    st.info(f"Analyzing match potential between your companies and {company['company_name']}...")
    
    # For now, redirect to analysis page
    # In a full implementation, this would perform quick matching analysis
    st.session_state.selected_candidate_company = company
    st.switch_page("pages/2_🔍_Analysis_Results.py")

if __name__ == "__main__":
    main()

