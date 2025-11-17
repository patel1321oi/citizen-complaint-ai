# CitiZen AI - Smart City Complaint Management Platform

## Project Overview

CitiZen AI is an intelligent civic complaint management system that bridges the gap between citizens and municipal authorities through artificial intelligence. The platform automatically predicts complaint urgency, optimizes resource allocation, and provides real-time tracking of issue resolution.

## Key Features

### For Citizens

- **Intuitive Complaint Submission** - Submit issues with detailed descriptions and photo evidence
- **AI-Powered Urgency Prediction** - Automatic classification of complaint priority levels
- **Real-Time Tracking** - Monitor complaint status and resolution progress
- **Photo Evidence Support** - Upload images or capture photos directly through the interface

### For Municipal Agents

- **Intelligent Queue Management** - AI-sorted complaints by urgency and location
- **Interactive Mapping** - Geographic visualization of all reported issues
- **Performance Analytics** - Data-driven insights for resource optimization
- **Mobile-Responsive Dashboard** - Access system from field locations

## Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with SQLite database
- **Machine Learning**: scikit-learn (Random Forest + TF-IDF)
- **Mapping**: Folium with interactive visualization
- **Image Processing**: Pillow for photo handling
- **Database**: SQLite with comprehensive indexing

## Architecture

```
citizen_ai/
├── main.py                        # Main application router
├── auth/
│   ├── __init__.py
│   ├── user_auth.py               # Citizen authentication
│   └── agent_auth.py              # Agent authentication
├── dashboard/
│   ├── __init__.py
│   ├── user_dashboard.py          # Citizen interface
│   └── agent_dashboard.py         # Agent interface
├── ml/
│   ├── __init__.py
│   ├── model.py                   # AI training and prediction
│   └── model.pkl                  # Trained model (auto-generated)
├── db/
│   └── complaints.db              # SQLite database (auto-created)
├── utils/
│   ├── __init__.py
│   └── data_utils.py              # Database utilities
├── assets/
│   └── uploaded_images/           # User uploads (auto-created)
├── requirements.txt               # Python dependencies
└── README.md                      # This documentation
```

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Modern web browser

### Step 1: Download Project

```bash
# If using git
git clone <repository-url>
cd citizen_ai

# Or extract downloaded ZIP file and navigate to folder
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run Application

```bash
streamlit run main.py
```

### Step 4: Access Platform

Open your web browser and navigate to: `http://localhost:8501`

## First Time Setup

The application automatically handles initial setup:

- Database tables are created on first run
- AI model trains with synthetic data for immediate functionality
- All necessary directories are generated automatically

## Usage Guide

### For Citizens

#### Registration and Login

1. Select "I'm a Citizen" from the landing page
2. Create an account with name, email, and password
3. Login with your credentials

#### Submitting Complaints

1. Navigate to "Submit Complaint" tab
2. Fill in required information:
   - Select complaint category
   - Provide exact location/address
   - Write detailed description
   - Set your perceived priority level
3. Optionally add photo evidence:
   - Select "Yes, upload a photo" from dropdown
   - Choose image file from your device
4. Submit complaint and receive AI urgency prediction

#### Tracking Complaints

- View all submitted complaints in "My Complaints" tab
- Filter by status (Pending, In Progress, Resolved)
- Monitor resolution progress and updates

### For Municipal Agents

#### Registration and Login

1. Select "I'm a Resolution Agent" from landing page
2. Register with valid Agent ID (format: AGT1234)
3. Provide official name and create secure password

#### Managing Complaints

1. **Active Queue**: View AI-prioritized complaint list

   - Complaints sorted by urgency and submission time
   - Filter by status, urgency, or category
   - Take action: Start Work, Mark Resolved, Pause Work

2. **Complaint Map**: Interactive geographic view

   - Color-coded markers by urgency level
   - Click markers for detailed complaint information
   - Optimize routing for field visits

3. **Analytics**: Performance metrics and insights
   - Resolution rates and response times
   - Category distribution analysis
   - Team performance tracking

## AI System Details

### Machine Learning Model

- **Algorithm**: Random Forest Classifier with 200 decision trees
- **Features**: TF-IDF vectorization of complaint text and category
- **Training**: Automatic retraining every 10 new complaints
- **Accuracy**: 95% on synthetic training data, improves with real data

### Urgency Prediction

- **High Priority**: Emergency keywords (fire, flood, danger, safety)
- **Medium Priority**: Problem indicators (irregular, delay, concern)
- **Low Priority**: General maintenance and information requests

### Auto-Training Process

1. Monitor new complaint submissions
2. Trigger retraining when threshold reached (10 complaints)
3. Combine synthetic and real-world data
4. Evaluate model performance
5. Update system automatically without manual intervention

## Database Schema

### Core Tables

**users** - Citizen accounts

- id, name, email, password, created_at, status

**agents** - Municipal agent accounts

- id, name, agent_id, password, department, total_resolved

**complaints** - Main complaint records

- id, user_id, category, description, address, urgency, status, timestamps

**complaint_history** - Status change tracking

- complaint_id, old_status, new_status, changed_by, changed_at

## Configuration Options

### Admin Settings

- Default admin password: `admin123` (change in main.py)
- AI retraining threshold: 10 new complaints (modify in ml/model.py)
- Agent ID format: AGT + 4 digits (customizable in agent_auth.py)

### Supported Media

- Image formats: JPG, JPEG, PNG, GIF
- Maximum file size: 200MB
- Auto-compression for optimal performance

## Troubleshooting

### Common Issues

**Module Import Errors**

```bash
pip install -r requirements.txt --force-reinstall
```

**Database Connection Problems**

- Check if `db/` directory has write permissions
- Restart application to reinitialize database
- Verify file permissions in project directory

**Camera Not Working**

- Grant browser camera permissions
- Use Chrome or Firefox for best compatibility
- Ensure camera is not being used by another application

**AI Model Issues**

- Model creates automatically on first run (may take 30 seconds)
- Check console for training progress messages
- Restart application if model loading fails

### Performance Optimization

**For Large Datasets**

- Consider PostgreSQL for production deployment
- Implement data archiving for historical complaints
- Add caching layers for frequently accessed data

**For High Traffic**

- Deploy on cloud platforms (AWS, Heroku, Google Cloud)
- Implement load balancing for multiple instances
- Use CDN for static file delivery

## Development and Contribution

### Setting Up Development Environment

```bash
# Create virtual environment
python -m venv citizen_ai_env
source citizen_ai_env/bin/activate  # On Windows: citizen_ai_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run main.py --server.runOnSave=true
```

### Code Structure Guidelines

- Modular design with separated concerns
- Comprehensive error handling
- Inline documentation and docstrings
- Type hints where applicable

## Production Deployment

### Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
SECRET_KEY=your-secret-key-here
ADMIN_PASSWORD=secure-admin-password
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## License and Legal

This project is released under the MIT License, making it free for municipal and educational use. All user data is stored locally by default with proper encryption for sensitive information.

## Support and Contact

### Technical Support

- Check console output for error messages
- Verify all dependencies are installed correctly
- Ensure proper file permissions
- Restart the Streamlit application

### Municipal Implementation

- Customization services available for specific city needs
- Training programs for agent onboarding
- Integration support for existing municipal systems
- Ongoing maintenance and updates

---

**CitiZen AI - Empowering Smart Cities Through AI-Driven Civic Engagement**

_Making cities more responsive, efficient, and citizen-centric through intelligent complaint management._
