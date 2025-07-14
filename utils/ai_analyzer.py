"""
AI-powered analysis utilities for Merger Book MVP
Uses OpenAI and LangChain for business feature extraction and synergy analysis
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
import openai
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import streamlit as st
from utils.config import Config

class AIAnalyzer:
    """AI-powered business analysis and matching"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_API_BASE
        )
        self.model = Config.OPENAI_MODEL
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200,
            length_function=len
        )
    
    def extract_business_features(self, document_content: str, document_metadata: Dict = None) -> Dict[str, Any]:
        """
        Extract comprehensive business features from document content using AI
        
        Args:
            document_content: Text content of the document
            document_metadata: Additional metadata about the document
        
        Returns:
            Dictionary containing extracted business features
        """
        try:
            # Split document into manageable chunks
            chunks = self.text_splitter.split_text(document_content)
            
            # Extract features from each chunk and combine
            all_features = []
            for chunk in chunks[:5]:  # Limit to first 5 chunks for MVP
                features = self._extract_features_from_chunk(chunk)
                if features:
                    all_features.append(features)
            
            # Combine and consolidate features
            consolidated_features = self._consolidate_features(all_features)
            
            return consolidated_features
            
        except Exception as e:
            st.error(f"Error in AI feature extraction: {str(e)}")
            return self._get_empty_features()
    
    def _extract_features_from_chunk(self, text_chunk: str) -> Dict[str, Any]:
        """Extract business features from a single text chunk"""
        
        prompt = """
        Analyze the following business document text and extract key business information. 
        Return the information in JSON format with the following structure:
        
        {
            "company_name": "extracted company name or null",
            "industry_classification": "primary industry/sector",
            "business_model": "description of how the company makes money",
            "revenue_info": {
                "amount": "revenue amount if mentioned",
                "currency": "currency if specified",
                "period": "time period (annual, quarterly, etc.)",
                "growth_rate": "growth rate if mentioned"
            },
            "employee_count": "number of employees if mentioned",
            "geographic_markets": ["list of geographic markets/regions"],
            "key_products_services": ["list of main products or services"],
            "technology_stack": ["list of technologies mentioned"],
            "competitive_advantages": ["list of competitive advantages"],
            "strategic_objectives": ["list of strategic goals or objectives"],
            "financial_metrics": {
                "profitability": "profitability information",
                "margins": "margin information",
                "other_metrics": "other financial metrics"
            },
            "partnerships": ["list of partnerships or key relationships"],
            "target_customers": ["list of target customer segments"],
            "market_position": "description of market position",
            "growth_strategy": "description of growth strategy",
            "risks_challenges": ["list of risks or challenges mentioned"]
        }
        
        Only include information that is explicitly mentioned in the text. Use null for missing information.
        
        Text to analyze:
        {text}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a business analyst expert at extracting structured information from business documents."},
                    {"role": "user", "content": prompt.format(text=text_chunk)}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            
            # Clean up the response to extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            features = json.loads(content.strip())
            return features
            
        except Exception as e:
            st.warning(f"Error extracting features from chunk: {str(e)}")
            return {}
    
    def _consolidate_features(self, features_list: List[Dict]) -> Dict[str, Any]:
        """Consolidate features from multiple chunks"""
        if not features_list:
            return self._get_empty_features()
        
        # Start with the first feature set
        consolidated = features_list[0].copy()
        
        # Merge information from other chunks
        for features in features_list[1:]:
            # Merge lists
            for key in ['geographic_markets', 'key_products_services', 'technology_stack', 
                       'competitive_advantages', 'strategic_objectives', 'partnerships', 
                       'target_customers', 'risks_challenges']:
                if key in features and features[key]:
                    if key not in consolidated:
                        consolidated[key] = []
                    consolidated[key].extend(features[key])
                    # Remove duplicates
                    consolidated[key] = list(set(consolidated[key]))
            
            # Update single values if not already set
            for key in ['company_name', 'industry_classification', 'business_model', 
                       'employee_count', 'market_position', 'growth_strategy']:
                if key in features and features[key] and not consolidated.get(key):
                    consolidated[key] = features[key]
            
            # Merge revenue info
            if 'revenue_info' in features and features['revenue_info']:
                if 'revenue_info' not in consolidated:
                    consolidated['revenue_info'] = {}
                for rev_key, rev_value in features['revenue_info'].items():
                    if rev_value and not consolidated['revenue_info'].get(rev_key):
                        consolidated['revenue_info'][rev_key] = rev_value
        
        return consolidated
    
    def _get_empty_features(self) -> Dict[str, Any]:
        """Return empty features structure"""
        return {
            "company_name": None,
            "industry_classification": None,
            "business_model": None,
            "revenue_info": {},
            "employee_count": None,
            "geographic_markets": [],
            "key_products_services": [],
            "technology_stack": [],
            "competitive_advantages": [],
            "strategic_objectives": [],
            "financial_metrics": {},
            "partnerships": [],
            "target_customers": [],
            "market_position": None,
            "growth_strategy": None,
            "risks_challenges": []
        }
    
    def analyze_synergies(self, user_company: Dict, candidate_company: Dict) -> Dict[str, Any]:
        """
        Analyze potential synergies between user company and candidate company
        
        Args:
            user_company: User's company information
            candidate_company: Potential merger candidate information
        
        Returns:
            Dictionary containing synergy analysis
        """
        try:
            prompt = """
            Analyze the potential merger synergies between these two companies and provide a detailed assessment.
            
            User Company:
            {user_company}
            
            Candidate Company:
            {candidate_company}
            
            Provide analysis in the following JSON format:
            {{
                "overall_match_score": 0.85,
                "match_type": "horizontal" or "vertical",
                "synergy_predictions": {{
                    "revenue_synergies": {{
                        "cross_selling_opportunities": "description and estimated value",
                        "market_expansion": "description and estimated value",
                        "pricing_power": "description and estimated value",
                        "total_revenue_uplift": "estimated percentage or amount"
                    }},
                    "cost_synergies": {{
                        "operational_efficiencies": "description and estimated savings",
                        "technology_integration": "description and estimated savings",
                        "administrative_savings": "description and estimated savings",
                        "procurement_savings": "description and estimated savings",
                        "total_cost_savings": "estimated percentage or amount"
                    }},
                    "strategic_synergies": {{
                        "market_position": "how combined entity improves market position",
                        "competitive_advantages": "new competitive advantages created",
                        "innovation_capabilities": "enhanced innovation potential",
                        "geographic_expansion": "geographic expansion opportunities"
                    }}
                }},
                "risk_assessment": {{
                    "integration_complexity": "high/medium/low with explanation",
                    "cultural_fit": "assessment of cultural compatibility",
                    "regulatory_concerns": "potential regulatory issues",
                    "market_risks": "market-related risks",
                    "execution_risks": "risks in executing the merger"
                }},
                "confidence_score": 0.75,
                "key_value_drivers": ["list of top 3-5 value creation drivers"],
                "implementation_timeline": "estimated timeline for realizing synergies",
                "recommended_structure": "recommended transaction structure"
            }}
            
            Provide specific, quantitative estimates where possible. Be realistic about challenges and risks.
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert M&A analyst with deep experience in synergy analysis and valuation."},
                    {"role": "user", "content": prompt.format(
                        user_company=json.dumps(user_company, indent=2),
                        candidate_company=json.dumps(candidate_company, indent=2)
                    )}
                ],
                temperature=0.2,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            
            # Clean up the response to extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            analysis = json.loads(content.strip())
            return analysis
            
        except Exception as e:
            st.error(f"Error in synergy analysis: {str(e)}")
            return self._get_empty_synergy_analysis()
    
    def _get_empty_synergy_analysis(self) -> Dict[str, Any]:
        """Return empty synergy analysis structure"""
        return {
            "overall_match_score": 0.0,
            "match_type": "unknown",
            "synergy_predictions": {
                "revenue_synergies": {},
                "cost_synergies": {},
                "strategic_synergies": {}
            },
            "risk_assessment": {},
            "confidence_score": 0.0,
            "key_value_drivers": [],
            "implementation_timeline": "unknown",
            "recommended_structure": "unknown"
        }
    
    def generate_company_summary(self, business_features: Dict) -> str:
        """Generate a concise company summary from business features"""
        try:
            prompt = """
            Based on the following business information, create a concise 2-3 sentence company summary 
            that captures the essence of the business, its market position, and key value proposition.
            
            Business Information:
            {features}
            
            Summary:
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a business analyst who creates clear, concise company summaries."},
                    {"role": "user", "content": prompt.format(features=json.dumps(business_features, indent=2))}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.warning(f"Error generating company summary: {str(e)}")
            return "Company summary not available."
    
    def classify_industry(self, business_features: Dict) -> str:
        """Classify company industry based on business features"""
        try:
            # Simple classification based on keywords
            industry_keywords = {
                'Technology': ['software', 'saas', 'platform', 'api', 'cloud', 'ai', 'machine learning'],
                'Financial Services': ['fintech', 'payment', 'banking', 'insurance', 'investment'],
                'Healthcare': ['healthcare', 'medical', 'biotech', 'pharmaceutical', 'health'],
                'Manufacturing': ['manufacturing', 'production', 'factory', 'industrial'],
                'Retail': ['retail', 'e-commerce', 'consumer', 'marketplace'],
                'Energy': ['energy', 'oil', 'gas', 'renewable', 'solar', 'wind'],
                'Real Estate': ['real estate', 'property', 'construction', 'development'],
                'Transportation': ['transportation', 'logistics', 'shipping', 'delivery'],
                'Media': ['media', 'entertainment', 'content', 'publishing', 'advertising']
            }
            
            # Check business features for industry keywords
            text_to_check = ' '.join([
                str(business_features.get('industry_classification', '')),
                str(business_features.get('business_model', '')),
                ' '.join(business_features.get('key_products_services', [])),
                ' '.join(business_features.get('technology_stack', []))
            ]).lower()
            
            for industry, keywords in industry_keywords.items():
                for keyword in keywords:
                    if keyword in text_to_check:
                        return industry
            
            # Fallback to AI classification
            if business_features.get('industry_classification'):
                return business_features['industry_classification']
            
            return 'Other'
            
        except Exception as e:
            return 'Unknown'

