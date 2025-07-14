"""
Matching engine for identifying potential merger candidates
Uses machine learning and similarity analysis to find compatible companies
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import pandas as pd
import streamlit as st
from utils.config import Config

class MatchingEngine:
    """Engine for finding and scoring potential merger candidates"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.scaler = StandardScaler()
        self.min_match_score = Config.MIN_MATCH_SCORE
        self.max_matches = Config.MAX_MATCHES_PER_QUERY
    
    def find_matches(self, user_company: Dict, candidate_companies: List[Dict]) -> List[Dict]:
        """
        Find potential merger matches for a user company
        
        Args:
            user_company: User's company information
            candidate_companies: List of potential candidate companies
        
        Returns:
            List of matches sorted by match score
        """
        try:
            if not candidate_companies:
                return []
            
            # Calculate similarity scores
            matches = []
            for candidate in candidate_companies:
                # Skip if same company
                if (user_company.get('company_id') == candidate.get('company_id') or
                    user_company.get('company_name') == candidate.get('company_name')):
                    continue
                
                match_score, match_type = self._calculate_match_score(user_company, candidate)
                
                if match_score >= self.min_match_score:
                    match = {
                        'candidate_company': candidate,
                        'match_score': match_score,
                        'match_type': match_type,
                        'similarity_factors': self._get_similarity_factors(user_company, candidate)
                    }
                    matches.append(match)
            
            # Sort by match score and limit results
            matches.sort(key=lambda x: x['match_score'], reverse=True)
            return matches[:self.max_matches]
            
        except Exception as e:
            st.error(f"Error in matching engine: {str(e)}")
            return []
    
    def _calculate_match_score(self, company1: Dict, company2: Dict) -> Tuple[float, str]:
        """
        Calculate overall match score between two companies
        
        Returns:
            Tuple of (match_score, match_type)
        """
        try:
            # Extract features for comparison
            features1 = self._extract_matching_features(company1)
            features2 = self._extract_matching_features(company2)
            
            # Calculate different similarity components
            industry_sim = self._calculate_industry_similarity(features1, features2)
            business_sim = self._calculate_business_similarity(features1, features2)
            geographic_sim = self._calculate_geographic_similarity(features1, features2)
            size_sim = self._calculate_size_similarity(features1, features2)
            strategic_sim = self._calculate_strategic_similarity(features1, features2)
            
            # Determine match type
            match_type = self._determine_match_type(features1, features2, industry_sim)
            
            # Weight the similarities based on match type
            if match_type == 'horizontal':
                # Horizontal mergers: same industry, focus on geographic and strategic fit
                weights = {
                    'industry': 0.3,
                    'business': 0.2,
                    'geographic': 0.2,
                    'size': 0.1,
                    'strategic': 0.2
                }
            else:  # vertical
                # Vertical mergers: different industries, focus on business and strategic complementarity
                weights = {
                    'industry': 0.1,
                    'business': 0.3,
                    'geographic': 0.2,
                    'size': 0.1,
                    'strategic': 0.3
                }
            
            # Calculate weighted score
            match_score = (
                industry_sim * weights['industry'] +
                business_sim * weights['business'] +
                geographic_sim * weights['geographic'] +
                size_sim * weights['size'] +
                strategic_sim * weights['strategic']
            )
            
            return min(match_score, 1.0), match_type
            
        except Exception as e:
            st.warning(f"Error calculating match score: {str(e)}")
            return 0.0, 'unknown'
    
    def _extract_matching_features(self, company: Dict) -> Dict[str, Any]:
        """Extract features relevant for matching"""
        # Handle both database format and business features format
        if 'financial_metrics' in company and isinstance(company['financial_metrics'], str):
            # Database format - parse JSON strings
            import json
            financial_metrics = json.loads(company.get('financial_metrics', '{}'))
            strategic_objectives = json.loads(company.get('strategic_objectives', '{}'))
            business_features = {}
        else:
            # Business features format
            financial_metrics = company.get('financial_metrics', {})
            strategic_objectives = company.get('strategic_objectives', [])
            business_features = company
        
        return {
            'company_name': company.get('company_name', ''),
            'industry': company.get('industry_classification', business_features.get('industry_classification', '')),
            'business_model': business_features.get('business_model', ''),
            'revenue': company.get('revenue', 0) or self._extract_revenue(business_features.get('revenue_info', {})),
            'employee_count': company.get('employee_count', 0) or business_features.get('employee_count', 0),
            'geographic_markets': company.get('geographic_markets', '').split(',') if company.get('geographic_markets') else business_features.get('geographic_markets', []),
            'products_services': business_features.get('key_products_services', []),
            'technology_stack': business_features.get('technology_stack', []),
            'strategic_objectives': strategic_objectives if isinstance(strategic_objectives, list) else business_features.get('strategic_objectives', []),
            'target_customers': business_features.get('target_customers', []),
            'competitive_advantages': business_features.get('competitive_advantages', [])
        }
    
    def _extract_revenue(self, revenue_info: Dict) -> float:
        """Extract numeric revenue from revenue info"""
        try:
            amount_str = revenue_info.get('amount', '0')
            if isinstance(amount_str, str):
                # Remove currency symbols and convert to float
                amount_str = amount_str.replace('$', '').replace(',', '').replace('M', '000000').replace('B', '000000000')
                return float(amount_str)
            return float(amount_str)
        except:
            return 0.0
    
    def _calculate_industry_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calculate industry similarity"""
        industry1 = features1.get('industry', '').lower()
        industry2 = features2.get('industry', '').lower()
        
        if not industry1 or not industry2:
            return 0.5  # Neutral score if industry unknown
        
        # Exact match
        if industry1 == industry2:
            return 1.0
        
        # Related industries
        related_industries = {
            'technology': ['software', 'fintech', 'artificial intelligence', 'saas'],
            'financial services': ['fintech', 'banking', 'insurance'],
            'healthcare': ['biotech', 'pharmaceutical', 'medical'],
            'retail': ['e-commerce', 'consumer goods', 'marketplace']
        }
        
        for main_industry, related in related_industries.items():
            if (industry1 in [main_industry] + related and 
                industry2 in [main_industry] + related):
                return 0.7
        
        return 0.2  # Different industries
    
    def _calculate_business_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calculate business model and offering similarity"""
        try:
            # Combine business-related text
            text1 = ' '.join([
                features1.get('business_model', ''),
                ' '.join(features1.get('products_services', [])),
                ' '.join(features1.get('competitive_advantages', []))
            ])
            
            text2 = ' '.join([
                features2.get('business_model', ''),
                ' '.join(features2.get('products_services', [])),
                ' '.join(features2.get('competitive_advantages', []))
            ])
            
            if not text1.strip() or not text2.strip():
                return 0.5
            
            # Use TF-IDF similarity
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity
            
        except Exception as e:
            return 0.5
    
    def _calculate_geographic_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calculate geographic market overlap"""
        markets1 = set([m.lower().strip() for m in features1.get('geographic_markets', [])])
        markets2 = set([m.lower().strip() for m in features2.get('geographic_markets', [])])
        
        if not markets1 or not markets2:
            return 0.5
        
        # Calculate Jaccard similarity
        intersection = len(markets1.intersection(markets2))
        union = len(markets1.union(markets2))
        
        if union == 0:
            return 0.5
        
        jaccard_sim = intersection / union
        
        # Boost score for complementary markets (good for expansion)
        if intersection == 0 and len(markets1) > 0 and len(markets2) > 0:
            return 0.7  # Complementary markets are valuable
        
        return jaccard_sim
    
    def _calculate_size_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calculate company size compatibility"""
        try:
            revenue1 = features1.get('revenue', 0)
            revenue2 = features2.get('revenue', 0)
            employees1 = features1.get('employee_count', 0)
            employees2 = features2.get('employee_count', 0)
            
            # If no size data, return neutral
            if not any([revenue1, revenue2, employees1, employees2]):
                return 0.5
            
            # Calculate revenue ratio similarity
            revenue_sim = 0.5
            if revenue1 > 0 and revenue2 > 0:
                ratio = min(revenue1, revenue2) / max(revenue1, revenue2)
                revenue_sim = ratio
            
            # Calculate employee ratio similarity
            employee_sim = 0.5
            if employees1 > 0 and employees2 > 0:
                ratio = min(employees1, employees2) / max(employees1, employees2)
                employee_sim = ratio
            
            # Average the similarities
            return (revenue_sim + employee_sim) / 2
            
        except Exception as e:
            return 0.5
    
    def _calculate_strategic_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calculate strategic alignment"""
        try:
            # Combine strategic text
            text1 = ' '.join([
                ' '.join(features1.get('strategic_objectives', [])),
                ' '.join(features1.get('target_customers', []))
            ])
            
            text2 = ' '.join([
                ' '.join(features2.get('strategic_objectives', [])),
                ' '.join(features2.get('target_customers', []))
            ])
            
            if not text1.strip() or not text2.strip():
                return 0.5
            
            # Use TF-IDF similarity
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity
            
        except Exception as e:
            return 0.5
    
    def _determine_match_type(self, features1: Dict, features2: Dict, industry_similarity: float) -> str:
        """Determine if match is horizontal or vertical"""
        if industry_similarity >= 0.7:
            return 'horizontal'
        else:
            return 'vertical'
    
    def _get_similarity_factors(self, company1: Dict, company2: Dict) -> Dict[str, float]:
        """Get detailed similarity breakdown"""
        features1 = self._extract_matching_features(company1)
        features2 = self._extract_matching_features(company2)
        
        return {
            'industry_similarity': self._calculate_industry_similarity(features1, features2),
            'business_similarity': self._calculate_business_similarity(features1, features2),
            'geographic_similarity': self._calculate_geographic_similarity(features1, features2),
            'size_similarity': self._calculate_size_similarity(features1, features2),
            'strategic_similarity': self._calculate_strategic_similarity(features1, features2)
        }
    
    def get_feature_importance(self, matches: List[Dict]) -> Dict[str, float]:
        """
        Analyze feature importance across matches
        
        Args:
            matches: List of match results
        
        Returns:
            Dictionary of feature importance scores
        """
        if not matches:
            return {}
        
        # Collect similarity factors from all matches
        factors_data = []
        scores = []
        
        for match in matches:
            factors = match.get('similarity_factors', {})
            factors_data.append([
                factors.get('industry_similarity', 0),
                factors.get('business_similarity', 0),
                factors.get('geographic_similarity', 0),
                factors.get('size_similarity', 0),
                factors.get('strategic_similarity', 0)
            ])
            scores.append(match['match_score'])
        
        if len(factors_data) < 2:
            return {
                'industry_importance': 0.2,
                'business_importance': 0.2,
                'geographic_importance': 0.2,
                'size_importance': 0.2,
                'strategic_importance': 0.2
            }
        
        # Calculate correlation between each factor and match scores
        factors_array = np.array(factors_data)
        scores_array = np.array(scores)
        
        correlations = []
        for i in range(factors_array.shape[1]):
            corr = np.corrcoef(factors_array[:, i], scores_array)[0, 1]
            correlations.append(abs(corr) if not np.isnan(corr) else 0)
        
        # Normalize to sum to 1
        total_corr = sum(correlations)
        if total_corr > 0:
            normalized_importance = [c / total_corr for c in correlations]
        else:
            normalized_importance = [0.2] * 5
        
        return {
            'industry_importance': normalized_importance[0],
            'business_importance': normalized_importance[1],
            'geographic_importance': normalized_importance[2],
            'size_importance': normalized_importance[3],
            'strategic_importance': normalized_importance[4]
        }

