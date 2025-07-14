#!/usr/bin/env python3
"""
Test script for processing EstateGuru presentation
Saves results to test-data/ directory as JSON files
"""

import os
import sys
import json
from datetime import datetime

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.config import Config
from utils.database import DatabaseManager
from utils.document_processor import DocumentProcessor
from utils.ai_analyzer import AIAnalyzer
from utils.matching_engine import MatchingEngine
from utils.financial_data import FinancialDataManager

def main():
    """Main test function"""
    
    print("🚀 Starting EstateGuru document processing test...")
    
    # Initialize components
    db = DatabaseManager(Config.DATABASE_PATH)
    doc_processor = DocumentProcessor()
    ai_analyzer = AIAnalyzer()
    matching_engine = MatchingEngine(db)
    financial_manager = FinancialDataManager()
    
    # Ensure test-data directory exists
    os.makedirs('test-data', exist_ok=True)
    
    # File path
    pdf_path = 'test-data/EstateGuru-2024-10-01.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found at {pdf_path}")
        return
    
    print(f"📄 Processing document: {pdf_path}")
    
    try:
        # Step 1: Extract document content
        print("📄 Extracting document content...")
        extraction_result = doc_processor.process_document(pdf_path, 'pdf')
        
        if extraction_result['processing_status'] == 'error':
            print(f"❌ Document extraction failed: {extraction_result['error_message']}")
            return
        
        # Save extraction results
        save_json_result('estateguru_extraction.json', extraction_result)
        print(f"✅ Document extraction complete. Pages: {extraction_result.get('page_count', 0)}")
        
        # Step 2: AI business feature extraction
        print("🤖 Analyzing business features with AI...")
        business_features = ai_analyzer.extract_business_features(
            extraction_result['text_content'],
            extraction_result.get('metadata', {})
        )
        
        # Save business features
        save_json_result('estateguru_business_features.json', business_features)
        print(f"✅ Business features extracted. Company: {business_features.get('company_name', 'Unknown')}")
        
        # Step 3: Industry classification
        print("🏭 Classifying industry...")
        industry = ai_analyzer.classify_industry(business_features)
        business_features['industry_classification'] = industry
        
        # Step 4: Generate company summary
        print("📝 Generating company summary...")
        company_summary = ai_analyzer.generate_company_summary(business_features)
        
        # Step 5: Create company profile
        company_data = {
            'company_name': business_features.get('company_name', 'EstateGuru'),
            'industry_classification': industry,
            'business_description': company_summary,
            'revenue': doc_processor._extract_revenue(business_features.get('revenue_info', {})),
            'employee_count': business_features.get('employee_count'),
            'geographic_markets': ', '.join(business_features.get('geographic_markets', [])),
            'financial_metrics': business_features.get('financial_metrics', {}),
            'strategic_objectives': business_features.get('strategic_objectives', []),
            'data_source': 'user_upload',
            'user_id': 1,
            'processed_date': datetime.now().isoformat()
        }
        
        # Save company profile
        save_json_result('estateguru_company_profile.json', company_data)
        print(f"✅ Company profile created for {company_data['company_name']}")
        
        # Step 6: Find potential matches (if we have market data)
        print("🔍 Finding potential merger matches...")
        try:
            # First, let's populate some sample market data
            print("📊 Populating sample market data...")
            sample_companies = financial_manager.get_sample_companies()
            
            if sample_companies:
                # Save sample companies
                save_json_result('sample_market_companies.json', sample_companies)
                
                # Find matches
                matches = matching_engine.find_matches(company_data, sample_companies)
                
                # Save matches
                save_json_result('estateguru_matches.json', matches)
                print(f"✅ Found {len(matches)} potential matches")
                
                # Step 7: Analyze synergies for top matches
                print("🔗 Analyzing synergies...")
                synergy_analyses = []
                
                for match in matches[:5]:  # Top 5 matches
                    synergy = ai_analyzer.analyze_synergies(company_data, match)
                    synergy_analyses.append({
                        'target_company': match['company_name'],
                        'match_score': match['similarity_score'],
                        'synergy_analysis': synergy
                    })
                
                # Save synergy analyses
                save_json_result('estateguru_synergy_analysis.json', synergy_analyses)
                print(f"✅ Synergy analysis complete for top {len(synergy_analyses)} matches")
            
            else:
                print("⚠️ No market data available for matching")
        
        except Exception as e:
            print(f"⚠️ Matching/synergy analysis failed: {str(e)}")
        
        # Step 8: Generate final summary report
        print("📋 Generating final summary report...")
        summary_report = {
            'company_name': company_data['company_name'],
            'processing_date': datetime.now().isoformat(),
            'document_info': {
                'filename': 'EstateGuru-2024-10-01.pdf',
                'pages': extraction_result.get('page_count', 0),
                'words_extracted': len(extraction_result.get('text_content', '').split())
            },
            'business_features_summary': {
                'industry': industry,
                'revenue_info': business_features.get('revenue_info', {}),
                'geographic_markets': business_features.get('geographic_markets', []),
                'key_products': business_features.get('key_products_services', [])[:3],  # Top 3
                'strategic_objectives': business_features.get('strategic_objectives', [])[:3]  # Top 3
            },
            'analysis_results': {
                'total_matches_found': len(matches) if 'matches' in locals() else 0,
                'top_match': matches[0]['company_name'] if 'matches' in locals() and matches else None,
                'synergy_analyses_completed': len(synergy_analyses) if 'synergy_analyses' in locals() else 0
            }
        }
        
        # Save summary report
        save_json_result('estateguru_summary_report.json', summary_report)
        
        print("\n🎉 Processing complete! Results saved to test-data/")
        print("\nFiles created:")
        for filename in os.listdir('test-data'):
            if filename.endswith('.json'):
                print(f"  📄 {filename}")
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()

def save_json_result(filename: str, data: dict):
    """Save result data as JSON file"""
    filepath = os.path.join('test-data', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"💾 Saved: {filename}")

if __name__ == "__main__":
    main()

