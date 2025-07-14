"""
Document Upload Page for Merger Book MVP
Handles file upload, processing, and business feature extraction
"""

import streamlit as st
import sys
import os
import time
from typing import Dict, Any

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.config import Config
from utils.database import DatabaseManager
from utils.document_processor import DocumentProcessor
from utils.ai_analyzer import AIAnalyzer

# Page configuration
st.set_page_config(
    page_title="Upload Documents - Merger Book",
    page_icon="📤",
    layout="wide"
)

# Initialize components
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager(Config.DATABASE_PATH)

if 'doc_processor' not in st.session_state:
    st.session_state.doc_processor = DocumentProcessor()

if 'ai_analyzer' not in st.session_state:
    st.session_state.ai_analyzer = AIAnalyzer()

def main():
    """Main upload page function"""
    
    # Set default user for testing (no authentication)
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 1  # Default test user
    if 'username' not in st.session_state:
        st.session_state.username = "test_user"
    
    st.title("📤 Upload Business Documents")
    st.markdown("Upload your business plan, annual report, or pitch deck to extract key business information and find potential merger partners.")
    st.info("🔓 Authentication disabled for testing")
    
    # Configuration check
    config_status = Config.validate_config()
    if not config_status['valid']:
        st.error("⚠️ Configuration issues detected:")
        for issue in config_status['issues']:
            st.error(f"• {issue}")
        st.stop()
    
    # File upload section
    st.subheader("Upload Document")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'doc', 'pptx', 'ppt'],
        help="Supported formats: PDF, Word (DOCX/DOC), PowerPoint (PPTX/PPT)"
    )
    
    if uploaded_file is not None:
        # Display file information
        file_info = st.session_state.doc_processor.get_file_info(uploaded_file)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", file_info['filename'])
        with col2:
            st.metric("File Type", file_info['file_type'].upper())
        with col3:
            st.metric("File Size", f"{file_info['file_size'] / 1024:.1f} KB")
        
        # Process document button
        if st.button("🚀 Process Document", type="primary", use_container_width=True):
            process_document(uploaded_file, file_info)
    
    # Display recent uploads
    st.markdown("---")
    display_recent_uploads()

def process_document(uploaded_file, file_info: Dict[str, Any]):
    """Process uploaded document"""
    
    try:
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Save file
        status_text.text("💾 Saving file...")
        progress_bar.progress(10)
        
        file_path = st.session_state.doc_processor.save_uploaded_file(
            uploaded_file, Config.UPLOAD_FOLDER
        )
        
        # Step 2: Create database record
        status_text.text("📝 Creating database record...")
        progress_bar.progress(20)
        
        document_data = {
            'user_id': st.session_state.user_id,
            'filename': file_info['filename'],
            'file_type': file_info['file_type'],
            'file_path': file_path,
            'file_size': file_info['file_size']
        }
        
        document_id = st.session_state.db.create_document(document_data)
        
        # Step 3: Process document content
        status_text.text("📄 Extracting document content...")
        progress_bar.progress(40)
        
        # Update status to processing
        st.session_state.db.update_document_processing(document_id, 'processing')
        
        # Extract content
        extraction_result = st.session_state.doc_processor.process_document(
            file_path, file_info['file_type']
        )
        
        if extraction_result['processing_status'] == 'error':
            st.session_state.db.update_document_processing(
                document_id, 'error', error_message=extraction_result['error_message']
            )
            st.error(f"Document processing failed: {extraction_result['error_message']}")
            return
        
        # Step 4: AI analysis
        status_text.text("🤖 Analyzing business features with AI...")
        progress_bar.progress(60)
        
        business_features = st.session_state.ai_analyzer.extract_business_features(
            extraction_result['text_content'],
            extraction_result.get('metadata', {})
        )
        
        # Step 5: Update database with results
        status_text.text("💾 Saving analysis results...")
        progress_bar.progress(80)
        
        st.session_state.db.update_document_processing(
            document_id, 'completed',
            extracted_content=extraction_result,
            business_features=business_features
        )
        
        # Step 6: Create company record if business features extracted
        if business_features.get('company_name'):
            status_text.text("🏢 Creating company profile...")
            progress_bar.progress(90)
            
            # Generate company summary
            company_summary = st.session_state.ai_analyzer.generate_company_summary(business_features)
            
            company_data = {
                'company_name': business_features.get('company_name', file_info['filename']),
                'industry_classification': st.session_state.ai_analyzer.classify_industry(business_features),
                'business_description': company_summary,
                'revenue': st.session_state.doc_processor._extract_revenue(business_features.get('revenue_info', {})),
                'employee_count': business_features.get('employee_count'),
                'geographic_markets': ', '.join(business_features.get('geographic_markets', [])),
                'financial_metrics': business_features.get('financial_metrics', {}),
                'strategic_objectives': business_features.get('strategic_objectives', []),
                'data_source': 'user_upload',
                'user_id': st.session_state.user_id
            }
            
            company_id = st.session_state.db.create_company(company_data)
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        # Display results
        display_processing_results(extraction_result, business_features)
        
        # Success message with next steps
        st.success("🎉 Document processed successfully!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Find Merger Matches", use_container_width=True):
                st.switch_page("pages/2_🔍_Analysis_Results.py")
        with col2:
            if st.button("📤 Upload Another Document", use_container_width=True):
                st.rerun()
        
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        if 'document_id' in locals():
            st.session_state.db.update_document_processing(
                document_id, 'error', error_message=str(e)
            )

def display_processing_results(extraction_result: Dict, business_features: Dict):
    """Display document processing results"""
    
    st.subheader("📊 Processing Results")
    
    # Document statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pages/Slides", extraction_result.get('page_count', 0))
    with col2:
        st.metric("Words Extracted", len(extraction_result.get('text_content', '').split()))
    with col3:
        st.metric("Processing Status", "✅ Complete")
    
    # Business features tabs
    tab1, tab2, tab3 = st.tabs(["🏢 Company Info", "📈 Business Details", "🎯 Strategic Info"])
    
    with tab1:
        if business_features.get('company_name'):
            st.write(f"**Company Name:** {business_features['company_name']}")
        if business_features.get('industry_classification'):
            st.write(f"**Industry:** {business_features['industry_classification']}")
        if business_features.get('business_model'):
            st.write(f"**Business Model:** {business_features['business_model']}")
        
        # Revenue information
        revenue_info = business_features.get('revenue_info', {})
        if revenue_info:
            st.write("**Revenue Information:**")
            for key, value in revenue_info.items():
                if value:
                    st.write(f"  • {key.replace('_', ' ').title()}: {value}")
    
    with tab2:
        # Products and services
        products = business_features.get('key_products_services', [])
        if products:
            st.write("**Key Products/Services:**")
            for product in products:
                st.write(f"• {product}")
        
        # Geographic markets
        markets = business_features.get('geographic_markets', [])
        if markets:
            st.write("**Geographic Markets:**")
            for market in markets:
                st.write(f"• {market}")
        
        # Technology stack
        tech = business_features.get('technology_stack', [])
        if tech:
            st.write("**Technology Stack:**")
            for technology in tech:
                st.write(f"• {technology}")
    
    with tab3:
        # Strategic objectives
        objectives = business_features.get('strategic_objectives', [])
        if objectives:
            st.write("**Strategic Objectives:**")
            for objective in objectives:
                st.write(f"• {objective}")
        
        # Competitive advantages
        advantages = business_features.get('competitive_advantages', [])
        if advantages:
            st.write("**Competitive Advantages:**")
            for advantage in advantages:
                st.write(f"• {advantage}")
        
        # Target customers
        customers = business_features.get('target_customers', [])
        if customers:
            st.write("**Target Customers:**")
            for customer in customers:
                st.write(f"• {customer}")

def display_recent_uploads():
    """Display recent document uploads"""
    
    st.subheader("📋 Recent Uploads")
    
    documents = st.session_state.db.get_documents_by_user(st.session_state.user_id)
    
    if not documents:
        st.info("No documents uploaded yet. Upload your first document above!")
        return
    
    # Display documents in a table
    for doc in documents[:10]:  # Show last 10 documents
        with st.expander(f"📄 {doc['filename']} - {doc['processing_status'].title()}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Upload Date:** {doc['upload_date']}")
                st.write(f"**File Type:** {doc['file_type'].upper()}")
            
            with col2:
                st.write(f"**Status:** {doc['processing_status'].title()}")
                if doc['file_size']:
                    st.write(f"**Size:** {doc['file_size'] / 1024:.1f} KB")
            
            with col3:
                if doc['processing_status'] == 'completed':
                    if st.button(f"🔍 View Analysis", key=f"view_{doc['document_id']}"):
                        st.session_state.selected_document_id = doc['document_id']
                        st.switch_page("pages/2_🔍_Analysis_Results.py")
                elif doc['processing_status'] == 'error':
                    st.error(f"Error: {doc.get('error_messages', 'Unknown error')}")

if __name__ == "__main__":
    main()

