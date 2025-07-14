# Merger Book MVP

An AI-powered M&A analysis platform that helps startups and SMEs identify potential merger partners by analyzing uploaded business documents and matching with public companies using advanced AI and financial data analysis.

## 🚀 Features

- **Document Analysis**: Upload business plans, annual reports, or pitch decks (PDF, Word, PowerPoint)
- **AI-Powered Extraction**: Extract key business features using OpenAI and LangChain
- **Company Matching**: Find potential merger partners from public market data
- **Synergy Analysis**: Analyze potential synergies and value drivers
- **Financial Integration**: Real-time financial data from Polygon.io and Yahoo Finance
- **Interactive Dashboard**: Streamlit-based user interface with multi-page navigation

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Streamlit (Multi-page application)
- **Backend**: Python with SQLite database
- **AI/ML**: OpenAI GPT, LangChain, scikit-learn
- **Financial APIs**: Polygon.io, Yahoo Finance (yfinance)
- **Document Processing**: PyPDF2, python-docx, python-pptx

### Project Structure
```
merger-book/
├── main.py                 # Main Streamlit application
├── pages/                  # Streamlit pages
│   ├── 1_📤_Upload_Documents.py
│   ├── 2_🔍_Analysis_Results.py
│   ├── 3_🏢_Company_Database.py
│   └── 4_⚙️_Data_Management.py
├── utils/                  # Utility modules
│   ├── config.py          # Configuration management
│   ├── database.py        # Database operations
│   ├── document_processor.py  # Document parsing
│   ├── ai_analyzer.py     # AI analysis utilities
│   ├── matching_engine.py # Company matching algorithms
│   └── financial_data.py  # Financial data integration
├── data/                  # Data storage
├── docs/                  # Documentation
│   └── merger_book_prd.md # Product Requirements Document
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- OpenAI API key
- Polygon.io API key (optional, for enhanced financial data)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/kaljuvee/merger-book.git
   cd merger-book
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:8501`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# Financial Data APIs
POLYGON_API_KEY=your_polygon_api_key_here

# Database Configuration
DATABASE_PATH=data/merger_book.db

# File Upload Configuration
UPLOAD_FOLDER=data/uploads
MAX_FILE_SIZE_MB=50
```

### API Keys Setup
- **OpenAI API**: Required for document analysis and AI features
- **Polygon.io API**: Optional, enhances financial data capabilities
- **Yahoo Finance**: Used as fallback for financial data (no API key required)

## 📖 Usage

### 1. User Registration and Login
- Create an account or login with existing credentials
- Secure authentication with password hashing

### 2. Document Upload
- Navigate to "Upload Documents" page
- Upload business documents (PDF, Word, PowerPoint)
- AI automatically extracts key business information

### 3. Company Analysis
- View extracted business features and company profile
- Browse analysis results and business insights

### 4. Merger Matching
- Navigate to "Analysis Results" to find potential merger partners
- View match scores and similarity analysis
- Detailed synergy predictions with value drivers

### 5. Company Database
- Browse all companies in the database
- Filter by industry, data source, and other criteria
- View detailed company profiles

### 6. Data Management
- Populate database with market data from financial APIs
- Monitor API configuration status
- Manage database statistics and cleanup

## 🔍 Key Features Explained

### Document Processing
- Supports PDF, Word (DOCX/DOC), and PowerPoint (PPTX/PPT) files
- Extracts text content and metadata
- AI-powered business feature extraction

### AI Analysis
- Company name and industry classification
- Business model and revenue information
- Key products/services identification
- Strategic objectives and competitive advantages
- Geographic markets and target customers

### Matching Algorithm
- Industry similarity analysis
- Business model compatibility
- Geographic market overlap
- Size and scale considerations
- Strategic alignment assessment

### Synergy Analysis
- Revenue synergy predictions
- Cost synergy opportunities
- Strategic synergy identification
- Risk assessment and mitigation
- Value driver quantification

## 🗄️ Database Schema

### Core Tables
- **users**: User authentication and profiles
- **documents**: Uploaded document metadata
- **companies**: Company information (user and market data)
- **matches**: Merger match results
- **analysis_results**: Detailed analysis outcomes

## 🚀 Deployment

### Local Development
```bash
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

### Production Deployment
The application is designed to be deployed on cloud platforms that support Streamlit applications:
- Streamlit Cloud
- Heroku
- AWS/GCP/Azure with Docker
- Any Python-compatible hosting service

## 🧪 Testing

The application includes comprehensive testing for:
- User authentication system
- Document upload and processing
- AI analysis functionality
- Database operations
- Financial data integration

## 📊 API Integration

### Polygon.io Integration
- Real-time stock data
- Company fundamentals
- Financial metrics
- Market data

### Yahoo Finance Integration
- Company information
- Financial statements
- Stock prices
- Market statistics

## 🔒 Security

- Password hashing with secure algorithms
- Environment variable configuration
- Input validation and sanitization
- Secure file upload handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `docs/` folder
- Review the Product Requirements Document (PRD)

## 🔮 Future Enhancements

- Advanced ML models for better matching
- Real-time collaboration features
- Integration with more financial data sources
- Mobile application development
- Advanced visualization and reporting
- Deal pipeline management
- Due diligence automation

## 📈 Version History

### v1.0.0 (MVP)
- Initial release with core functionality
- Document upload and AI analysis
- Basic company matching
- Streamlit-based user interface
- SQLite database integration
- Financial data integration

---

**Merger Book MVP** - Empowering M&A decisions with AI-driven insights

