import streamlit as st

# Set page config FIRST - before any other imports or Streamlit commands
st.set_page_config(
    page_title="CitiZen AI - Smart City Platform",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import other modules after page config is set
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth.user_auth import show_user_auth
from auth.agent_auth import show_agent_auth
from dashboard.user_dashboard import show_user_dashboard
from dashboard.agent_dashboard import show_agent_dashboard
from utils.data_utils import init_database

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        text-align: center;
        min-height: 280px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    .feature-card h3 {
        color: #2c3e50;
        margin-bottom: 1rem;
        font-size: 1.4rem;
    }
    .feature-card p {
        color: #5a6c7d;
        line-height: 1.6;
        font-size: 1rem;
    }
    .user-type-card {
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem;
        cursor: pointer;
        transition: transform 0.3s ease;
        color: white;
    }
    .user-type-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    .agent-type-card {
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem;
        cursor: pointer;
        transition: transform 0.3s ease;
        color: white;
    }
    .agent-type-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    .stats-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem;
        border: 1px solid #e9ecef;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .stats-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.12);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

def show_landing_page():
    """Display the attractive landing page"""
    
    # Hero Section
    st.markdown("""
    <div class="main-header">
        <h1>🏙️ CitiZen AI</h1>
        <h2>Smart City Complaint Management Platform</h2>
        <p style="font-size: 1.2em; margin-top: 1rem;">
            Revolutionizing civic engagement through AI-powered complaint resolution
        </p>
        <p style="font-size: 1em; opacity: 0.9;">
            Report issues • Get AI predictions • Track resolutions • Build better cities
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown("## 🌟 **Platform Features**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem;">🤖</div>
            </div>
            <h3>AI-Powered Urgency</h3>
            <p>Advanced machine learning algorithms automatically predict complaint urgency and resolution time, ensuring critical issues get immediate attention.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem;">📱</div>
            </div>
            <h3>Multi-Modal Reporting</h3>
            <p>Submit complaints with text, photos, or real-time camera capture. Our platform supports comprehensive issue documentation.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem;">🗺️</div>
            </div>
            <h3>Interactive Mapping</h3>
            <p>Visualize complaints geographically with our integrated mapping system, helping authorities prioritize and route resources efficiently.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row of features
    st.markdown("<br>", unsafe_allow_html=True)
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem;">🔄</div>
            </div>
            <h3>Auto-Training ML</h3>
            <p>System automatically improves its predictions with every new complaint, continuously enhancing accuracy without manual intervention.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem;">📊</div>
            </div>
            <h3>Real-Time Analytics</h3>
            <p>Comprehensive dashboards with performance metrics, resolution tracking, and data-driven insights for municipal decision making.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem;">🔐</div>
            </div>
            <h3>Secure & Scalable</h3>
            <p>Role-based authentication, encrypted data storage, and architecture ready for city-wide deployment with thousands of users.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Statistics Section
    st.markdown("## 📊 **Platform Impact**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <h2 style="color: #667eea; font-size: 2.5rem; margin-bottom: 0.5rem;">1000+</h2>
            <p style="font-weight: bold; color: #2c3e50; margin: 0;">Issues Resolved</p>
            <p style="color: #7f8c8d; font-size: 0.9rem; margin-top: 0.5rem;">Across all categories</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-card">
            <h2 style="color: #e74c3c; font-size: 2.5rem; margin-bottom: 0.5rem;">95%</h2>
            <p style="font-weight: bold; color: #2c3e50; margin: 0;">AI Accuracy Rate</p>
            <p style="color: #7f8c8d; font-size: 0.9rem; margin-top: 0.5rem;">Urgency predictions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-card">
            <h2 style="color: #3498db; font-size: 2.5rem; margin-bottom: 0.5rem;">24hrs</h2>
            <p style="font-weight: bold; color: #2c3e50; margin: 0;">Avg Response Time</p>
            <p style="color: #7f8c8d; font-size: 0.9rem; margin-top: 0.5rem;">For high priority issues</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stats-card">
            <h2 style="color: #9b59b6; font-size: 2.5rem; margin-bottom: 0.5rem;">50+</h2>
            <p style="font-weight: bold; color: #2c3e50; margin: 0;">Active Agents</p>
            <p style="color: #7f8c8d; font-size: 0.9rem; margin-top: 0.5rem;">Municipal officers</p>
        </div>
        """, unsafe_allow_html=True)

def show_user_selection():
    """Show user type selection interface"""
    st.markdown("## 👤 **Choose Your Role**")
    st.markdown("Select your role to access the appropriate dashboard and features.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏠 I'm a Citizen", key="citizen_btn", help="Report civic issues and track resolutions"):
            st.session_state.user_type = "citizen"
            st.session_state.page = "user_auth"
            st.rerun()
        
        st.markdown("""
        <div class="user-type-card">
            <h3>🏠 Citizen Portal</h3>
            <p>Report civic issues like:</p>
            <ul style="text-align: left; margin-top: 1rem;">
                <li>Garbage overflow</li>
                <li>Drainage problems</li>
                <li>Streetlight failures</li>
                <li>Road damage</li>
                <li>Water supply issues</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("⚡ I'm a Resolution Agent", key="agent_btn", help="Manage and resolve citizen complaints"):
            st.session_state.user_type = "agent"
            st.session_state.page = "agent_auth"
            st.rerun()
        
        st.markdown("""
        <div class="agent-type-card">
            <h3>⚡ Resolution Agent Portal</h3>
            <p>Manage complaints with:</p>
            <ul style="text-align: left; margin-top: 1rem;">
                <li>AI-prioritized queue</li>
                <li>Interactive complaint map</li>
                <li>Resolution tracking</li>
                <li>Performance analytics</li>
                <li>Real-time notifications</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application logic with routing"""
    
    # Initialize database first thing
    try:
        init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        st.error(f"❌ Database initialization failed: {e}")
        st.stop()
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("### 🏙️ **CitiZen AI**")
        st.markdown("---")
        
        if st.session_state.authenticated:
            st.success(f"Welcome, {st.session_state.current_user['name']}!")
            if st.button("🚪 Logout", key="logout_btn"):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        else:
            st.info("Please login to access your dashboard")
        
        st.markdown("---")
        
        # Navigation buttons
        if st.button("🏠 Home", key="home_btn"):
            st.session_state.page = 'landing'
            st.rerun()
        
        if not st.session_state.authenticated:
            if st.button("👤 User Login", key="nav_user_btn"):
                st.session_state.user_type = "citizen"
                st.session_state.page = "user_auth"
                st.rerun()
            
            if st.button("⚡ Agent Login", key="nav_agent_btn"):
                st.session_state.user_type = "agent"
                st.session_state.page = "agent_auth"
                st.rerun()
    
    # Main content routing
    if st.session_state.page == 'landing':
        show_landing_page()
        st.markdown("---")
        show_user_selection()
    
    elif st.session_state.page == 'user_auth':
        if not st.session_state.authenticated:
            show_user_auth()
        else:
            show_user_dashboard()
    
    elif st.session_state.page == 'agent_auth':
        if not st.session_state.authenticated:
            show_agent_auth()
        else:
            show_agent_dashboard()
    
    elif st.session_state.page == 'user_dashboard':
        if st.session_state.authenticated and st.session_state.user_type == "citizen":
            show_user_dashboard()
        else:
            st.error("Access denied. Please login as a citizen.")
            st.session_state.page = 'landing'
            st.rerun()
    
    elif st.session_state.page == 'agent_dashboard':
        if st.session_state.authenticated and st.session_state.user_type == "agent":
            show_agent_dashboard()
        else:
            st.error("Access denied. Please login as a resolution agent.")
            st.session_state.page = 'landing'
            st.rerun()

if __name__ == "__main__":
    main()