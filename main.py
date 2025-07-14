"""
Merger Book MVP - Main Streamlit Application
"""

import streamlit as st
import sys
import os

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.config import Config
from utils.database import DatabaseManager

# Configure Streamlit page
st.set_page_config(
    page_title="Merger Book",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager(Config.DATABASE_PATH)

# Set default user for testing (no authentication)
if 'user_id' not in st.session_state:
    st.session_state.user_id = 1  # Default test user
if 'username' not in st.session_state:
    st.session_state.username = "test_user"

def main():
    """Main application entry point"""
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🤝 Merger Book")
        st.markdown("---")
        
        # User status (authentication disabled for testing)
        st.success(f"Welcome, {st.session_state.username}!")
        st.info("🔓 Authentication disabled for testing")
        
        st.markdown("---")
        
        # Configuration status
        config_status = Config.validate_config()
        if config_status['valid']:
            st.success("✅ Configuration Valid")
        else:
            st.error("❌ Configuration Issues")
            for issue in config_status['issues']:
                st.error(f"• {issue}")
    
    # Main content area - always show dashboard
    show_dashboard()

def show_dashboard():
    """Display main dashboard"""
    st.title("Merger Book Dashboard")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        documents = st.session_state.db.get_documents_by_user(st.session_state.user_id)
        st.metric("Documents Uploaded", len(documents))
    
    with col2:
        companies = st.session_state.db.get_companies_by_user(st.session_state.user_id)
        user_companies = [c for c in companies if c['data_source'] == 'user_upload']
        st.metric("Your Companies", len(user_companies))
    
    with col3:
        # Count total matches for user companies
        total_matches = 0
        for company in user_companies:
            matches = st.session_state.db.get_matches_by_company(company['company_id'])
            total_matches += len(matches)
        st.metric("Total Matches", total_matches)
    
    with col4:
        st.metric("Analysis Complete", "0")  # Placeholder
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    if documents:
        st.write("**Recent Documents:**")
        for doc in documents[:5]:  # Show last 5 documents
            status_icon = {
                'uploaded': '📄',
                'processing': '⏳',
                'completed': '✅',
                'error': '❌'
            }.get(doc['processing_status'], '📄')
            
            st.write(f"{status_icon} {doc['filename']} - {doc['processing_status']}")
    else:
        st.info("No documents uploaded yet. Visit the Upload page to get started!")
    
    # Quick actions
    st.markdown("---")
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload Document", use_container_width=True):
            st.switch_page("pages/1_📤_Upload_Documents.py")
    
    with col2:
        if st.button("🔍 View Analysis", use_container_width=True):
            st.switch_page("pages/2_🔍_Analysis_Results.py")
    
    with col3:
        if st.button("🏢 Company Database", use_container_width=True):
            st.switch_page("pages/3_🏢_Company_Database.py")

if __name__ == "__main__":
    main()

