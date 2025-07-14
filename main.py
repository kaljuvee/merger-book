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
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager(Config.DATABASE_PATH)

def main():
    """Main application entry point"""
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🤝 Merger Book")
        st.markdown("---")
        
        # User authentication status
        if st.session_state.user_id:
            st.success(f"Welcome, {st.session_state.username}!")
            if st.button("Logout"):
                st.session_state.user_id = None
                st.session_state.username = None
                st.rerun()
        else:
            st.info("Please login to continue")
        
        st.markdown("---")
        
        # Configuration status
        config_status = Config.validate_config()
        if config_status['valid']:
            st.success("✅ Configuration Valid")
        else:
            st.error("❌ Configuration Issues")
            for issue in config_status['issues']:
                st.error(f"• {issue}")
    
    # Main content area
    if not st.session_state.user_id:
        show_login_page()
    else:
        show_dashboard()

def show_login_page():
    """Display login/registration page"""
    st.title("Welcome to Merger Book")
    st.markdown("""
    ### AI-Powered M&A Analysis Platform
    
    Discover potential merger partners and analyze synergy opportunities using advanced AI and financial data analysis.
    """)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user = st.session_state.db.authenticate_user(username, password)
                if user:
                    st.session_state.user_id = user['user_id']
                    st.session_state.username = user['username']
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register")
            
            if submit:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    try:
                        user_id = st.session_state.db.create_user(new_username, new_email, new_password)
                        st.success("Registration successful! Please login.")
                    except Exception as e:
                        st.error(f"Registration failed: {str(e)}")

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

