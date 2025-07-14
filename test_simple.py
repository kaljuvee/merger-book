#!/usr/bin/env python3
"""
Simplified test script for processing EstateGuru presentation
Saves results to test-data/ directory as JSON files
"""

import os
import sys
import json
from datetime import datetime

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

def main():
    """Main test function"""
    
    print("🚀 Starting EstateGuru document processing test...")
    
    # Ensure test-data directory exists
    os.makedirs('test-data', exist_ok=True)
    
    # File path
    pdf_path = 'test-data/EstateGuru-2024-10-01.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found at {pdf_path}")
        return
    
    print(f"📄 Processing document: {pdf_path}")
    
    try:
        # Step 1: Simple document extraction using PyPDF2
        print("📄 Extracting document content...")
        
        from PyPDF2 import PdfReader
        
        reader = PdfReader(pdf_path)
        text_content = ""
        
        for page_num, page in enumerate(reader.pages):
            text_content += f"\n--- Page {page_num + 1} ---\n"
            text_content += page.extract_text()
        
        extraction_result = {
            'processing_status': 'completed',
            'text_content': text_content,
            'page_count': len(reader.pages),
            'metadata': {
                'filename': 'EstateGuru-2024-10-01.pdf',
                'file_type': 'pdf',
                'processing_date': datetime.now().isoformat()
            }
        }
        
        # Save extraction results
        save_json_result('estateguru_extraction.json', extraction_result)
        print(f"✅ Document extraction complete. Pages: {extraction_result['page_count']}")
        
        # Step 2: Simple business feature extraction (rule-based)
        print("🤖 Extracting business features...")
        
        text_lower = text_content.lower()
        
        # Extract company name
        company_name = "EstateGuru"
        if "estateguru" in text_lower:
            company_name = "EstateGuru"
        
        # Extract industry information
        industry_keywords = {
            'fintech': ['fintech', 'financial technology', 'lending platform'],
            'real estate': ['real estate', 'property', 'estate'],
            'lending': ['lending', 'loans', 'credit', 'financing'],
            'platform': ['platform', 'marketplace', 'digital platform']
        }
        
        detected_industries = []
        for industry, keywords in industry_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_industries.append(industry)
        
        # Extract geographic markets
        geographic_keywords = ['europe', 'estonia', 'latvia', 'lithuania', 'finland', 'germany', 'spain']
        geographic_markets = [geo for geo in geographic_keywords if geo in text_lower]
        
        # Extract revenue information
        revenue_info = {}
        if 'million' in text_lower or 'eur' in text_lower or '€' in text_content:
            revenue_info['currency'] = 'EUR'
            revenue_info['scale'] = 'millions'
        
        # Extract key products/services
        key_products = []
        if 'loan' in text_lower:
            key_products.append('Property-backed loans')
        if 'platform' in text_lower:
            key_products.append('Digital lending platform')
        if 'investment' in text_lower:
            key_products.append('Investment opportunities')
        
        # Extract strategic objectives
        strategic_objectives = []
        if 'growth' in text_lower:
            strategic_objectives.append('Business growth and expansion')
        if 'market' in text_lower:
            strategic_objectives.append('Market expansion')
        if 'technology' in text_lower:
            strategic_objectives.append('Technology development')
        
        business_features = {
            'company_name': company_name,
            'industry_classification': ', '.join(detected_industries) if detected_industries else 'Financial Services',
            'business_model': 'Digital lending platform for property-backed SME loans',
            'revenue_info': revenue_info,
            'geographic_markets': geographic_markets,
            'key_products_services': key_products,
            'strategic_objectives': strategic_objectives,
            'technology_stack': ['Digital platform', 'Web application'],
            'target_customers': ['SME borrowers', 'Individual investors'],
            'competitive_advantages': ['Cross-border operations', 'Property-backed security']
        }
        
        # Save business features
        save_json_result('estateguru_business_features.json', business_features)
        print(f"✅ Business features extracted. Company: {business_features['company_name']}")
        
        # Step 3: Create company profile
        company_data = {
            'company_name': business_features['company_name'],
            'industry_classification': business_features['industry_classification'],
            'business_description': f"{business_features['company_name']} is a {business_features['business_model']} operating in {', '.join(business_features['geographic_markets'])}.",
            'revenue': None,  # Would need more detailed extraction
            'employee_count': None,  # Not available in simple extraction
            'geographic_markets': ', '.join(business_features['geographic_markets']),
            'financial_metrics': business_features['revenue_info'],
            'strategic_objectives': business_features['strategic_objectives'],
            'data_source': 'user_upload',
            'user_id': 1,
            'processed_date': datetime.now().isoformat()
        }
        
        # Save company profile
        save_json_result('estateguru_company_profile.json', company_data)
        print(f"✅ Company profile created for {company_data['company_name']}")
        
        # Step 4: Create sample market companies for matching
        print("📊 Creating sample market companies...")
        
        sample_companies = [
            {
                'company_name': 'LendingClub',
                'industry_classification': 'fintech, lending',
                'business_model': 'Peer-to-peer lending platform',
                'geographic_markets': 'United States',
                'similarity_score': 0.85
            },
            {
                'company_name': 'Funding Circle',
                'industry_classification': 'fintech, lending',
                'business_model': 'SME lending platform',
                'geographic_markets': 'UK, Europe',
                'similarity_score': 0.92
            },
            {
                'company_name': 'Prosper',
                'industry_classification': 'fintech, lending',
                'business_model': 'Personal lending platform',
                'geographic_markets': 'United States',
                'similarity_score': 0.78
            },
            {
                'company_name': 'Zopa',
                'industry_classification': 'fintech, lending',
                'business_model': 'Digital bank and lending',
                'geographic_markets': 'United Kingdom',
                'similarity_score': 0.81
            },
            {
                'company_name': 'Auxmoney',
                'industry_classification': 'fintech, lending',
                'business_model': 'P2P lending platform',
                'geographic_markets': 'Germany',
                'similarity_score': 0.87
            }
        ]
        
        # Save sample companies
        save_json_result('sample_market_companies.json', sample_companies)
        print(f"✅ Created {len(sample_companies)} sample market companies")
        
        # Step 5: Create matches
        matches = []
        for company in sample_companies:
            match = {
                'target_company': company['company_name'],
                'industry_match': True,
                'geographic_overlap': 'Europe' in company['geographic_markets'],
                'business_model_similarity': 'lending' in company['business_model'].lower(),
                'similarity_score': company['similarity_score'],
                'match_type': 'horizontal' if 'lending' in company['business_model'].lower() else 'vertical'
            }
            matches.append(match)
        
        # Sort by similarity score
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Save matches
        save_json_result('estateguru_matches.json', matches)
        print(f"✅ Found {len(matches)} potential matches")
        
        # Step 6: Create synergy analysis
        print("🔗 Analyzing synergies...")
        
        synergy_analyses = []
        for match in matches[:3]:  # Top 3 matches
            synergy = {
                'target_company': match['target_company'],
                'match_score': match['similarity_score'],
                'revenue_synergies': {
                    'cross_selling_potential': 'High' if match['geographic_overlap'] else 'Medium',
                    'market_expansion': 'Significant' if not match['geographic_overlap'] else 'Limited',
                    'estimated_revenue_increase': f"{int(match['similarity_score'] * 15)}%"
                },
                'cost_synergies': {
                    'technology_consolidation': 'High',
                    'operational_efficiency': 'Medium',
                    'estimated_cost_savings': f"{int(match['similarity_score'] * 20)}%"
                },
                'strategic_synergies': {
                    'market_position': 'Strengthened',
                    'competitive_advantage': 'Enhanced',
                    'risk_diversification': 'Improved'
                },
                'risk_factors': [
                    'Regulatory compliance differences',
                    'Cultural integration challenges',
                    'Technology integration complexity'
                ]
            }
            synergy_analyses.append(synergy)
        
        # Save synergy analyses
        save_json_result('estateguru_synergy_analysis.json', synergy_analyses)
        print(f"✅ Synergy analysis complete for top {len(synergy_analyses)} matches")
        
        # Step 7: Generate final summary report
        print("📋 Generating final summary report...")
        
        summary_report = {
            'company_name': company_data['company_name'],
            'processing_date': datetime.now().isoformat(),
            'document_info': {
                'filename': 'EstateGuru-2024-10-01.pdf',
                'pages': extraction_result['page_count'],
                'words_extracted': len(extraction_result['text_content'].split())
            },
            'business_features_summary': {
                'industry': business_features['industry_classification'],
                'business_model': business_features['business_model'],
                'geographic_markets': business_features['geographic_markets'],
                'key_products': business_features['key_products_services'],
                'strategic_objectives': business_features['strategic_objectives']
            },
            'analysis_results': {
                'total_matches_found': len(matches),
                'top_match': matches[0]['target_company'] if matches else None,
                'top_match_score': matches[0]['similarity_score'] if matches else None,
                'synergy_analyses_completed': len(synergy_analyses)
            },
            'key_insights': [
                f"EstateGuru operates in the {business_features['industry_classification']} sector",
                f"Primary markets: {', '.join(business_features['geographic_markets'])}",
                f"Best match: {matches[0]['target_company']} with {matches[0]['similarity_score']:.0%} similarity",
                f"Potential revenue synergies: {synergy_analyses[0]['revenue_synergies']['estimated_revenue_increase']} increase",
                f"Potential cost synergies: {synergy_analyses[0]['cost_synergies']['estimated_cost_savings']} savings"
            ]
        }
        
        # Save summary report
        save_json_result('estateguru_summary_report.json', summary_report)
        
        print("\n🎉 Processing complete! Results saved to test-data/")
        print("\nFiles created:")
        for filename in sorted(os.listdir('test-data')):
            if filename.endswith('.json'):
                print(f"  📄 {filename}")
        
        print(f"\n📊 Summary:")
        print(f"  • Company: {summary_report['company_name']}")
        print(f"  • Industry: {summary_report['business_features_summary']['industry']}")
        print(f"  • Pages processed: {summary_report['document_info']['pages']}")
        print(f"  • Words extracted: {summary_report['document_info']['words_extracted']:,}")
        print(f"  • Matches found: {summary_report['analysis_results']['total_matches_found']}")
        print(f"  • Top match: {summary_report['analysis_results']['top_match']} ({summary_report['analysis_results']['top_match_score']:.0%})")
        
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

