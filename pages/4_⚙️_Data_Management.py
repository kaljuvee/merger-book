"""
Data Management Page for Merger Book MVP
Manages financial data integration and database population
"""

import streamlit as st
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.config import Config
from utils.database import DatabaseManager
from utils.financial_data import FinancialDataManager

# Page configuration
st.set_page_config(
    page_title="Data Management - Merger Book",
    page_icon="⚙️",
    layout="wide"
)

# Initialize components
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager(Config.DATABASE_PATH)

if 'financial_manager' not in st.session_state:
    st.session_state.financial_manager = FinancialDataManager()

def main():
    """Main data management page function"""
    
    # Check authentication
    if not st.session_state.get('user_id'):
        st.error("Please login to access this page")
        if st.button("Go to Login"):
            st.switch_page("main.py")
        return
    
    st.title("⚙️ Data Management")
    st.markdown("Manage financial data integration and database population for merger analysis.")
    
    # Configuration status
    config_status = Config.validate_config()
    display_configuration_status(config_status)
    
    # Database statistics
    st.markdown("---")
    display_database_statistics()
    
    # Data management actions
    st.markdown("---")
    display_data_management_actions()
    
    # Market statistics
    st.markdown("---")
    display_market_statistics()

def display_configuration_status(config_status: Dict):
    """Display API configuration status"""
    
    st.subheader("🔧 API Configuration Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if config_status['config']['openai_configured']:
            st.success("✅ OpenAI API Configured")
        else:
            st.error("❌ OpenAI API Not Configured")
    
    with col2:
        if config_status['config']['polygon_configured']:
            st.success("✅ Polygon API Configured")
        else:
            st.error("❌ Polygon API Not Configured")
    
    with col3:
        st.info(f"🗃️ Database: {config_status['config']['database_path']}")
    
    if not config_status['valid']:
        st.warning("⚠️ Some APIs are not configured. This may limit functionality.")
        with st.expander("Configuration Issues"):
            for issue in config_status['issues']:
                st.error(f"• {issue}")

def display_database_statistics():
    """Display current database statistics"""
    
    st.subheader("📊 Database Statistics")
    
    # Get all companies
    companies = st.session_state.db.get_companies_by_user(st.session_state.user_id)
    user_companies = [c for c in companies if c['data_source'] == 'user_upload']
    market_companies = [c for c in companies if c['data_source'] == 'market_data']
    
    # Get documents
    documents = st.session_state.db.get_documents_by_user(st.session_state.user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Your Companies", len(user_companies))
    
    with col2:
        st.metric("Market Companies", len(market_companies))
    
    with col3:
        st.metric("Documents Processed", len(documents))
    
    with col4:
        completed_docs = len([d for d in documents if d['processing_status'] == 'completed'])
        st.metric("Successfully Processed", completed_docs)
    
    # Industry distribution
    if companies:
        display_industry_distribution_chart(companies)

def display_industry_distribution_chart(companies: List[Dict]):
    """Display industry distribution chart"""
    
    # Count companies by industry and data source
    industry_data = {}
    for company in companies:
        industry = company.get('industry_classification', 'Unknown')
        source = company.get('data_source', 'unknown')
        
        if industry not in industry_data:
            industry_data[industry] = {'user_upload': 0, 'market_data': 0}
        
        industry_data[industry][source] += 1
    
    if industry_data:
        # Prepare data for stacked bar chart
        industries = list(industry_data.keys())
        user_counts = [industry_data[ind]['user_upload'] for ind in industries]
        market_counts = [industry_data[ind]['market_data'] for ind in industries]
        
        fig = go.Figure(data=[
            go.Bar(name='Your Companies', x=industries, y=user_counts),
            go.Bar(name='Market Companies', x=industries, y=market_counts)
        ])
        
        fig.update_layout(
            title="Companies by Industry",
            barmode='stack',
            height=400,
            xaxis_title="Industry",
            yaxis_title="Number of Companies"
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_data_management_actions():
    """Display data management action buttons"""
    
    st.subheader("🔄 Data Management Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Market Data Population")
        st.write("Populate the database with public company information from financial APIs.")
        
        max_companies = st.number_input("Max Companies to Add", 1, 100, 25, 
                                       help="Number of companies to fetch (limited for MVP)")
        
        if st.button("🚀 Populate Market Data", type="primary", use_container_width=True):
            populate_market_data(max_companies)
    
    with col2:
        st.markdown("#### Database Maintenance")
        st.write("Perform database maintenance and cleanup operations.")
        
        if st.button("🧹 Clean Up Database", use_container_width=True):
            cleanup_database()
        
        if st.button("📊 Refresh Statistics", use_container_width=True):
            st.rerun()
        
        if st.button("🔄 Update Financial Data", use_container_width=True):
            update_financial_data()

def populate_market_data(max_companies: int):
    """Populate database with market data"""
    
    st.subheader("🚀 Populating Market Data")
    
    try:
        # Check if market companies already exist
        companies = st.session_state.db.get_companies_by_user(st.session_state.user_id)
        market_companies = [c for c in companies if c['data_source'] == 'market_data']
        
        if market_companies:
            st.warning(f"Found {len(market_companies)} existing market companies.")
            if not st.checkbox("Continue anyway (may create duplicates)"):
                return
        
        # Start population process
        with st.spinner("Fetching and processing company data..."):
            companies_added = st.session_state.financial_manager.populate_market_companies(max_companies)
        
        if companies_added > 0:
            st.success(f"✅ Successfully added {companies_added} companies to the database!")
            st.balloons()
            
            # Show next steps
            st.info("💡 You can now find merger matches using the Analysis Results page.")
            
            if st.button("🔍 Go to Analysis"):
                st.switch_page("pages/2_🔍_Analysis_Results.py")
        else:
            st.warning("No new companies were added. This might be due to API limits or existing data.")
    
    except Exception as e:
        st.error(f"Error populating market data: {str(e)}")

def cleanup_database():
    """Perform database cleanup operations"""
    
    st.subheader("🧹 Database Cleanup")
    
    try:
        # Get statistics before cleanup
        companies = st.session_state.db.get_companies_by_user(st.session_state.user_id)
        documents = st.session_state.db.get_documents_by_user(st.session_state.user_id)
        
        st.write("**Current Database Status:**")
        st.write(f"• Total Companies: {len(companies)}")
        st.write(f"• Total Documents: {len(documents)}")
        
        # Cleanup options
        cleanup_options = st.multiselect(
            "Select cleanup operations:",
            [
                "Remove duplicate companies",
                "Clean up failed document processing records",
                "Remove companies with no data",
                "Reset match results"
            ]
        )
        
        if cleanup_options and st.button("🗑️ Perform Cleanup"):
            with st.spinner("Performing cleanup operations..."):
                
                if "Remove duplicate companies" in cleanup_options:
                    # This would implement duplicate removal logic
                    st.info("Duplicate removal not implemented in MVP")
                
                if "Clean up failed document processing records" in cleanup_options:
                    # Remove documents with error status
                    with st.session_state.db.get_connection() as conn:
                        cursor = conn.execute("""
                            DELETE FROM documents 
                            WHERE processing_status = 'error' AND user_id = ?
                        """, (st.session_state.user_id,))
                        deleted_docs = cursor.rowcount
                    st.success(f"Removed {deleted_docs} failed document records")
                
                if "Remove companies with no data" in cleanup_options:
                    # Remove companies with minimal information
                    with st.session_state.db.get_connection() as conn:
                        cursor = conn.execute("""
                            DELETE FROM companies 
                            WHERE (revenue IS NULL OR revenue = 0) 
                            AND (employee_count IS NULL OR employee_count = 0)
                            AND data_source = 'market_data'
                        """, )
                        deleted_companies = cursor.rowcount
                    st.success(f"Removed {deleted_companies} companies with no data")
                
                if "Reset match results" in cleanup_options:
                    # Clear match results
                    with st.session_state.db.get_connection() as conn:
                        cursor = conn.execute("DELETE FROM matches")
                        deleted_matches = cursor.rowcount
                        cursor = conn.execute("DELETE FROM analysis_results")
                        deleted_analyses = cursor.rowcount
                    st.success(f"Removed {deleted_matches} matches and {deleted_analyses} analyses")
            
            st.success("✅ Cleanup completed!")
    
    except Exception as e:
        st.error(f"Error during cleanup: {str(e)}")

def update_financial_data():
    """Update financial data for existing companies"""
    
    st.subheader("🔄 Update Financial Data")
    
    try:
        # Get market companies with ticker symbols
        companies = st.session_state.db.get_companies_by_user(st.session_state.user_id)
        market_companies = [c for c in companies if c['data_source'] == 'market_data' and c.get('ticker_symbol')]
        
        if not market_companies:
            st.info("No market companies with ticker symbols found to update.")
            return
        
        st.write(f"Found {len(market_companies)} companies to update.")
        
        if st.button("🔄 Start Update Process"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            updated_count = 0
            for i, company in enumerate(market_companies[:10]):  # Limit to 10 for MVP
                symbol = company['ticker_symbol']
                status_text.text(f"Updating {symbol}...")
                
                success = st.session_state.financial_manager.update_company_financials(
                    company['company_id'], symbol
                )
                
                if success:
                    updated_count += 1
                    st.success(f"Updated {company['company_name']}")
                else:
                    st.warning(f"Failed to update {company['company_name']}")
                
                progress_bar.progress((i + 1) / min(len(market_companies), 10))
            
            status_text.text("✅ Update process complete!")
            st.success(f"Successfully updated {updated_count} companies.")
    
    except Exception as e:
        st.error(f"Error updating financial data: {str(e)}")

def display_market_statistics():
    """Display market statistics and insights"""
    
    st.subheader("📈 Market Statistics")
    
    try:
        stats = st.session_state.financial_manager.get_market_statistics()
        
        if not stats:
            st.info("No market statistics available. Populate market data first.")
            return
        
        # Revenue statistics
        revenue_stats = stats.get('revenue_statistics', {})
        if revenue_stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_revenue = revenue_stats.get('avg_revenue', 0)
                if avg_revenue:
                    st.metric("Average Revenue", f"${avg_revenue:,.0f}")
            
            with col2:
                max_revenue = revenue_stats.get('max_revenue', 0)
                if max_revenue:
                    st.metric("Highest Revenue", f"${max_revenue:,.0f}")
            
            with col3:
                total_companies = revenue_stats.get('total_companies', 0)
                st.metric("Companies with Revenue Data", total_companies)
        
        # Industry distribution
        industry_dist = stats.get('industry_distribution', {})
        if industry_dist:
            st.write("**Industry Distribution:**")
            
            # Create pie chart
            fig = px.pie(
                values=list(industry_dist.values()),
                names=list(industry_dist.keys()),
                title="Market Companies by Industry"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error displaying market statistics: {str(e)}")

if __name__ == "__main__":
    main()

