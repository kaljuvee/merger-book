"""
Database models and schema for Merger Book MVP
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Any
import os

class DatabaseManager:
    """Manages SQLite database operations for Merger Book"""
    
    def __init__(self, db_path: str = "data/merger_book.db"):
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()
    
    def ensure_db_directory(self):
        """Ensure the database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    subscription_level TEXT DEFAULT 'free',
                    preferences TEXT DEFAULT '{}',
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Companies table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    ticker_symbol TEXT,
                    industry_classification TEXT,
                    revenue REAL,
                    employee_count INTEGER,
                    geographic_markets TEXT,
                    business_description TEXT,
                    financial_metrics TEXT DEFAULT '{}',
                    strategic_objectives TEXT DEFAULT '{}',
                    data_source TEXT NOT NULL CHECK (data_source IN ('user_upload', 'market_data')),
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Documents table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_path TEXT,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processing_status TEXT DEFAULT 'uploaded' CHECK (processing_status IN ('uploaded', 'processing', 'completed', 'error')),
                    extracted_content TEXT DEFAULT '{}',
                    business_features TEXT DEFAULT '{}',
                    error_messages TEXT,
                    file_size INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Matches table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_company_id INTEGER NOT NULL,
                    candidate_company_id INTEGER NOT NULL,
                    match_score REAL NOT NULL,
                    match_type TEXT NOT NULL CHECK (match_type IN ('horizontal', 'vertical')),
                    synergy_predictions TEXT DEFAULT '{}',
                    risk_assessment TEXT DEFAULT '{}',
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    analysis_version TEXT DEFAULT '1.0',
                    confidence_score REAL,
                    FOREIGN KEY (user_company_id) REFERENCES companies (company_id),
                    FOREIGN KEY (candidate_company_id) REFERENCES companies (company_id)
                )
            """)
            
            # Analysis Results table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    analysis_type TEXT NOT NULL,
                    financial_projections TEXT DEFAULT '{}',
                    synergy_breakdown TEXT DEFAULT '{}',
                    risk_factors TEXT DEFAULT '{}',
                    confidence_score REAL,
                    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_version TEXT DEFAULT '1.0',
                    FOREIGN KEY (match_id) REFERENCES matches (match_id)
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry_classification)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_companies_data_source ON companies(data_source)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_user_company ON matches(user_company_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_score ON matches(match_score)")
            
            conn.commit()
    
    # User management methods
    def create_user(self, username: str, email: str, password: str) -> int:
        """Create a new user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            """, (username, email, password_hash))
            return cursor.lastrowid
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user info"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM users 
                WHERE username = ? AND password_hash = ? AND is_active = 1
            """, (username, password_hash))
            
            user = cursor.fetchone()
            if user:
                # Update last login
                conn.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                """, (user['user_id'],))
                return dict(user)
            return None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
    
    # Company management methods
    def create_company(self, company_data: Dict) -> int:
        """Create a new company record"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO companies (
                    company_name, ticker_symbol, industry_classification, revenue,
                    employee_count, geographic_markets, business_description,
                    financial_metrics, strategic_objectives, data_source, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_data.get('company_name'),
                company_data.get('ticker_symbol'),
                company_data.get('industry_classification'),
                company_data.get('revenue'),
                company_data.get('employee_count'),
                company_data.get('geographic_markets'),
                company_data.get('business_description'),
                json.dumps(company_data.get('financial_metrics', {})),
                json.dumps(company_data.get('strategic_objectives', {})),
                company_data.get('data_source', 'user_upload'),
                company_data.get('user_id')
            ))
            return cursor.lastrowid
    
    def get_companies_by_user(self, user_id: int) -> List[Dict]:
        """Get all companies for a user"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM companies WHERE user_id = ? OR data_source = 'market_data'
                ORDER BY company_name
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_company(self, company_id: int) -> Optional[Dict]:
        """Get company by ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM companies WHERE company_id = ?", (company_id,))
            company = cursor.fetchone()
            if company:
                result = dict(company)
                # Parse JSON fields
                result['financial_metrics'] = json.loads(result['financial_metrics'])
                result['strategic_objectives'] = json.loads(result['strategic_objectives'])
                return result
            return None
    
    # Document management methods
    def create_document(self, document_data: Dict) -> int:
        """Create a new document record"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO documents (
                    user_id, filename, file_type, file_path, file_size
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                document_data['user_id'],
                document_data['filename'],
                document_data['file_type'],
                document_data.get('file_path'),
                document_data.get('file_size')
            ))
            return cursor.lastrowid
    
    def update_document_processing(self, document_id: int, status: str, 
                                 extracted_content: Dict = None, 
                                 business_features: Dict = None,
                                 error_message: str = None):
        """Update document processing status and results"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE documents SET 
                    processing_status = ?,
                    extracted_content = ?,
                    business_features = ?,
                    error_messages = ?
                WHERE document_id = ?
            """, (
                status,
                json.dumps(extracted_content) if extracted_content else None,
                json.dumps(business_features) if business_features else None,
                error_message,
                document_id
            ))
    
    def get_documents_by_user(self, user_id: int) -> List[Dict]:
        """Get all documents for a user"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM documents WHERE user_id = ?
                ORDER BY upload_date DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_document(self, document_id: int) -> Optional[Dict]:
        """Get document by ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM documents WHERE document_id = ?", (document_id,))
            document = cursor.fetchone()
            if document:
                result = dict(document)
                # Parse JSON fields
                if result['extracted_content']:
                    result['extracted_content'] = json.loads(result['extracted_content'])
                if result['business_features']:
                    result['business_features'] = json.loads(result['business_features'])
                return result
            return None
    
    # Match management methods
    def create_match(self, match_data: Dict) -> int:
        """Create a new match record"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO matches (
                    user_company_id, candidate_company_id, match_score, match_type,
                    synergy_predictions, risk_assessment, confidence_score, analysis_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_data['user_company_id'],
                match_data['candidate_company_id'],
                match_data['match_score'],
                match_data['match_type'],
                json.dumps(match_data.get('synergy_predictions', {})),
                json.dumps(match_data.get('risk_assessment', {})),
                match_data.get('confidence_score'),
                match_data.get('analysis_version', '1.0')
            ))
            return cursor.lastrowid
    
    def get_matches_by_company(self, user_company_id: int, limit: int = 50) -> List[Dict]:
        """Get matches for a user company"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT m.*, c.company_name, c.ticker_symbol, c.industry_classification
                FROM matches m
                JOIN companies c ON m.candidate_company_id = c.company_id
                WHERE m.user_company_id = ?
                ORDER BY m.match_score DESC
                LIMIT ?
            """, (user_company_id, limit))
            
            matches = []
            for row in cursor.fetchall():
                match = dict(row)
                match['synergy_predictions'] = json.loads(match['synergy_predictions'])
                match['risk_assessment'] = json.loads(match['risk_assessment'])
                matches.append(match)
            return matches
    
    # Analysis results methods
    def create_analysis_result(self, analysis_data: Dict) -> int:
        """Create a new analysis result"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO analysis_results (
                    match_id, analysis_type, financial_projections,
                    synergy_breakdown, risk_factors, confidence_score, model_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_data['match_id'],
                analysis_data['analysis_type'],
                json.dumps(analysis_data.get('financial_projections', {})),
                json.dumps(analysis_data.get('synergy_breakdown', {})),
                json.dumps(analysis_data.get('risk_factors', {})),
                analysis_data.get('confidence_score'),
                analysis_data.get('model_version', '1.0')
            ))
            return cursor.lastrowid
    
    def get_analysis_results(self, match_id: int) -> List[Dict]:
        """Get analysis results for a match"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM analysis_results WHERE match_id = ?
                ORDER BY generated_date DESC
            """, (match_id,))
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['financial_projections'] = json.loads(result['financial_projections'])
                result['synergy_breakdown'] = json.loads(result['synergy_breakdown'])
                result['risk_factors'] = json.loads(result['risk_factors'])
                results.append(result)
            return results

