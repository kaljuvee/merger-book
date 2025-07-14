"""
Financial data integration utilities for Merger Book MVP
Integrates with Polygon.io and Yahoo Finance APIs to fetch public company data
"""

import requests
import yfinance as yf
import pandas as pd
import time
from typing import Dict, List, Optional, Any
import streamlit as st
from utils.config import Config
from utils.database import DatabaseManager

class FinancialDataManager:
    """Manages financial data integration from external APIs"""
    
    def __init__(self):
        self.polygon_api_key = Config.POLYGON_API_KEY
        self.polygon_base_url = "https://api.polygon.io"
        self.db = DatabaseManager(Config.DATABASE_PATH)
        self.rate_limit_delay = 12  # 12 seconds between requests for free tier
    
    def fetch_sp500_companies(self) -> List[Dict[str, Any]]:
        """Fetch S&P 500 companies as potential merger candidates"""
        try:
            # Get S&P 500 list from Wikipedia (free source)
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            sp500_df = tables[0]
            
            companies = []
            for _, row in sp500_df.head(50).iterrows():  # Limit to 50 for MVP
                company_data = {
                    'symbol': row['Symbol'],
                    'company_name': row['Security'],
                    'sector': row['GICS Sector'],
                    'industry': row['GICS Sub-Industry']
                }
                companies.append(company_data)
            
            return companies
            
        except Exception as e:
            st.error(f"Error fetching S&P 500 companies: {str(e)}")
            return []
    
    def get_company_fundamentals(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company fundamentals from Polygon.io"""
        try:
            if not self.polygon_api_key:
                st.warning("Polygon API key not configured")
                return None
            
            # Get company details
            url = f"{self.polygon_base_url}/v3/reference/tickers/{symbol}"
            params = {
                'apikey': self.polygon_api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data:
                    return data['results']
            elif response.status_code == 429:
                st.warning(f"Rate limit hit for {symbol}, skipping...")
                time.sleep(self.rate_limit_delay)
            else:
                st.warning(f"Error fetching data for {symbol}: {response.status_code}")
            
            return None
            
        except Exception as e:
            st.warning(f"Error getting fundamentals for {symbol}: {str(e)}")
            return None
    
    def get_company_financials_yfinance(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company financial data using Yahoo Finance (free alternative)"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'symbol' not in info:
                return None
            
            # Extract relevant financial information
            financial_data = {
                'symbol': symbol,
                'company_name': info.get('longName', ''),
                'industry': info.get('industry', ''),
                'sector': info.get('sector', ''),
                'business_summary': info.get('longBusinessSummary', ''),
                'market_cap': info.get('marketCap', 0),
                'revenue': info.get('totalRevenue', 0),
                'employees': info.get('fullTimeEmployees', 0),
                'country': info.get('country', ''),
                'city': info.get('city', ''),
                'website': info.get('website', ''),
                'pe_ratio': info.get('trailingPE', 0),
                'price_to_book': info.get('priceToBook', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'return_on_equity': info.get('returnOnEquity', 0),
                'profit_margins': info.get('profitMargins', 0),
                'revenue_growth': info.get('revenueGrowth', 0)
            }
            
            return financial_data
            
        except Exception as e:
            st.warning(f"Error getting Yahoo Finance data for {symbol}: {str(e)}")
            return None
    
    def populate_market_companies(self, max_companies: int = 50) -> int:
        """Populate database with market companies"""
        try:
            st.info("Fetching S&P 500 company list...")
            sp500_companies = self.fetch_sp500_companies()
            
            if not sp500_companies:
                st.error("Failed to fetch S&P 500 companies")
                return 0
            
            companies_added = 0
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, company in enumerate(sp500_companies[:max_companies]):
                symbol = company['symbol']
                
                # Check if company already exists
                existing_companies = self.db.get_companies_by_user(1)  # Use dummy user_id for market data
                if any(c.get('ticker_symbol') == symbol for c in existing_companies):
                    continue
                
                status_text.text(f"Processing {symbol} ({i+1}/{min(len(sp500_companies), max_companies)})...")
                progress_bar.progress((i + 1) / min(len(sp500_companies), max_companies))
                
                # Get financial data
                financial_data = self.get_company_financials_yfinance(symbol)
                
                if financial_data:
                    # Create company record
                    company_record = {
                        'company_name': financial_data.get('company_name', company['company_name']),
                        'ticker_symbol': symbol,
                        'industry_classification': financial_data.get('industry', company.get('sector', '')),
                        'revenue': financial_data.get('revenue', 0),
                        'employee_count': financial_data.get('employees', 0),
                        'geographic_markets': financial_data.get('country', ''),
                        'business_description': financial_data.get('business_summary', ''),
                        'financial_metrics': {
                            'market_cap': financial_data.get('market_cap', 0),
                            'pe_ratio': financial_data.get('pe_ratio', 0),
                            'price_to_book': financial_data.get('price_to_book', 0),
                            'debt_to_equity': financial_data.get('debt_to_equity', 0),
                            'return_on_equity': financial_data.get('return_on_equity', 0),
                            'profit_margins': financial_data.get('profit_margins', 0),
                            'revenue_growth': financial_data.get('revenue_growth', 0)
                        },
                        'strategic_objectives': [],
                        'data_source': 'market_data',
                        'user_id': None  # Market data doesn't belong to specific user
                    }
                    
                    try:
                        company_id = self.db.create_company(company_record)
                        companies_added += 1
                        st.success(f"Added {financial_data.get('company_name', symbol)} (ID: {company_id})")
                    except Exception as e:
                        st.warning(f"Error saving {symbol}: {str(e)}")
                
                # Rate limiting
                time.sleep(1)  # 1 second delay between requests
            
            status_text.text("✅ Market data population complete!")
            progress_bar.progress(1.0)
            
            return companies_added
            
        except Exception as e:
            st.error(f"Error populating market companies: {str(e)}")
            return 0
    
    def update_company_financials(self, company_id: int, symbol: str) -> bool:
        """Update financial data for a specific company"""
        try:
            financial_data = self.get_company_financials_yfinance(symbol)
            
            if not financial_data:
                return False
            
            # Update company record
            company = self.db.get_company(company_id)
            if not company:
                return False
            
            # Update financial metrics
            updated_metrics = company.get('financial_metrics', {})
            updated_metrics.update({
                'market_cap': financial_data.get('market_cap', 0),
                'pe_ratio': financial_data.get('pe_ratio', 0),
                'price_to_book': financial_data.get('price_to_book', 0),
                'debt_to_equity': financial_data.get('debt_to_equity', 0),
                'return_on_equity': financial_data.get('return_on_equity', 0),
                'profit_margins': financial_data.get('profit_margins', 0),
                'revenue_growth': financial_data.get('revenue_growth', 0)
            })
            
            # Update database
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE companies SET 
                        revenue = ?,
                        employee_count = ?,
                        business_description = ?,
                        financial_metrics = ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE company_id = ?
                """, (
                    financial_data.get('revenue', company.get('revenue')),
                    financial_data.get('employees', company.get('employee_count')),
                    financial_data.get('business_summary', company.get('business_description')),
                    json.dumps(updated_metrics),
                    company_id
                ))
            
            return True
            
        except Exception as e:
            st.error(f"Error updating company financials: {str(e)}")
            return False
    
    def get_industry_peers(self, industry: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get companies in the same industry"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM companies 
                    WHERE industry_classification LIKE ? 
                    AND data_source = 'market_data'
                    ORDER BY revenue DESC
                    LIMIT ?
                """, (f"%{industry}%", limit))
                
                companies = []
                for row in cursor.fetchall():
                    company = dict(row)
                    # Parse JSON fields
                    if company['financial_metrics']:
                        company['financial_metrics'] = json.loads(company['financial_metrics'])
                    if company['strategic_objectives']:
                        company['strategic_objectives'] = json.loads(company['strategic_objectives'])
                    companies.append(company)
                
                return companies
                
        except Exception as e:
            st.error(f"Error getting industry peers: {str(e)}")
            return []
    
    def get_market_statistics(self) -> Dict[str, Any]:
        """Get market statistics from the database"""
        try:
            with self.db.get_connection() as conn:
                # Count companies by industry
                cursor = conn.execute("""
                    SELECT industry_classification, COUNT(*) as count
                    FROM companies 
                    WHERE data_source = 'market_data'
                    GROUP BY industry_classification
                    ORDER BY count DESC
                """)
                industry_counts = dict(cursor.fetchall())
                
                # Get revenue statistics
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_companies,
                        AVG(revenue) as avg_revenue,
                        MAX(revenue) as max_revenue,
                        MIN(revenue) as min_revenue
                    FROM companies 
                    WHERE data_source = 'market_data' AND revenue > 0
                """)
                revenue_stats = dict(cursor.fetchone())
                
                # Get employee statistics
                cursor = conn.execute("""
                    SELECT 
                        AVG(employee_count) as avg_employees,
                        MAX(employee_count) as max_employees,
                        MIN(employee_count) as min_employees
                    FROM companies 
                    WHERE data_source = 'market_data' AND employee_count > 0
                """)
                employee_stats = dict(cursor.fetchone())
                
                return {
                    'industry_distribution': industry_counts,
                    'revenue_statistics': revenue_stats,
                    'employee_statistics': employee_stats
                }
                
        except Exception as e:
            st.error(f"Error getting market statistics: {str(e)}")
            return {}

# Import json for JSON operations
import json

