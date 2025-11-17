import streamlit as st
import sqlite3
import hashlib
import re
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_utils import get_db_connection

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_agent_id(agent_id):
    """Validate agent ID format (AGT followed by 4 digits)"""
    pattern = r'^AGT\d{4}$'
    return re.match(pattern, agent_id) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def create_agent(name, agent_id, password):
    """Create a new agent account"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if agent ID already exists
        cursor.execute("SELECT id FROM agents WHERE agent_id = ?", (agent_id,))
        if cursor.fetchone():
            conn.close()
            return False, "Agent ID already registered"
        
        # Insert new agent
        hashed_password = hash_password(password)
        cursor.execute("""
            INSERT INTO agents (name, agent_id, password, created_at, status)
            VALUES (?, ?, ?, ?, ?)
        """, (name, agent_id, hashed_password, datetime.now().isoformat(), 'active'))
        
        conn.commit()
        conn.close()
        return True, "Agent account created successfully"
    
    except Exception as e:
        return False, f"Error creating account: {str(e)}"

def authenticate_agent(agent_id, password):
    """Authenticate agent login"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(password)
        cursor.execute("""
            SELECT id, name, agent_id, status FROM agents 
            WHERE agent_id = ? AND password = ?
        """, (agent_id, hashed_password))
        
        agent = cursor.fetchone()
        conn.close()
        
        if agent:
            if agent[3] != 'active':
                return False, "Agent account is inactive. Contact administrator."
            
            return True, {
                'id': agent[0],
                'name': agent[1],
                'agent_id': agent[2],
                'status': agent[3]
            }
        else:
            return False, "Invalid Agent ID or password"
    
    except Exception as e:
        return False, f"Authentication error: {str(e)}"

def show_agent_auth():
    """Display agent authentication interface"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
        <h1>⚡ Resolution Agent Portal</h1>
        <p style="font-size: 1.1em;">Empowering municipal officers to resolve civic issues efficiently</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["🔑 Agent Login", "📝 Agent Registration"])
    
    with tab1:
        show_agent_login_form()
    
    with tab2:
        show_agent_signup_form()

def show_agent_login_form():
    """Display agent login form"""
    st.markdown("### 🔑 **Agent Login**")
    
    with st.form("agent_login_form"):
        col1, col2 = st.columns([1, 2])
        
        with col2:
            agent_id = st.text_input(
                "🆔 Agent ID",
                placeholder="AGT1234",
                help="Your unique agent identifier (Format: AGT followed by 4 digits)",
                max_chars=7
            )
            
            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your password",
                help="Enter your agent account password"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                login_btn = st.form_submit_button(
                    "🚀 Login",
                    type="primary",
                    use_container_width=True
                )
        
        if login_btn:
            if not agent_id or not password:
                st.error("Please fill in all fields")
            elif not validate_agent_id(agent_id):
                st.error("Invalid Agent ID format. Use format: AGT1234")
            else:
                success, result = authenticate_agent(agent_id, password)
                
                if success:
                    st.session_state.authenticated = True
                    st.session_state.current_user = result
                    st.session_state.page = 'agent_dashboard'
                    st.success(f"Welcome back, Agent {result['name']}!")
                    st.rerun()
                else:
                    st.error(result)

def show_agent_signup_form():
    """Display agent signup form"""
    st.markdown("### 📝 **Agent Registration**")
    
    st.info("🔒 **Note:** Agent registration requires administrative approval. Contact your supervisor for valid Agent IDs.")
    
    with st.form("agent_signup_form"):
        col1, col2 = st.columns([1, 2])
        
        with col2:
            name = st.text_input(
                "👤 Full Name",
                placeholder="Enter your full name",
                help="Your official name as per municipal records"
            )
            
            agent_id = st.text_input(
                "🆔 Agent ID",
                placeholder="AGT1234",
                help="Your assigned Agent ID (Format: AGT followed by 4 digits)",
                max_chars=7
            )
            
            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Create a strong password",
                help="Minimum 6 characters with letters and numbers"
            )
            
            confirm_password = st.text_input(
                "🔒 Confirm Password",
                type="password",
                placeholder="Re-enter your password",
                help="Must match the password above"
            )
            
            # Department selection
            department = st.selectbox(
                "🏢 Department",
                options=[
                    "Waste Management",
                    "Water & Drainage",
                    "Electricity",
                    "Roads & Infrastructure",
                    "Public Safety",
                    "General Municipal Services"
                ],
                help="Select your primary department"
            )
            
            # Terms and conditions
            terms_agreed = st.checkbox(
                "I agree to the Agent Terms of Service and Code of Conduct",
                help="Required for agent registration"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                signup_btn = st.form_submit_button(
                    "🎉 Register Agent",
                    type="primary",
                    use_container_width=True
                )
        
        if signup_btn:
            # Validation
            if not all([name, agent_id, password, confirm_password]):
                st.error("Please fill in all fields")
            elif not validate_agent_id(agent_id):
                st.error("Invalid Agent ID format. Use format: AGT1234")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif not terms_agreed:
                st.error("Please agree to the Agent Terms of Service")
            else:
                # Validate password strength
                is_valid, message = validate_password(password)
                if not is_valid:
                    st.error(message)
                else:
                    # Create agent account
                    success, result = create_agent(name, agent_id, password)
                    
                    if success:
                        st.success("🎉 Agent account registered successfully!")
                        st.info("Please use the Agent Login tab to access your dashboard")
                        
                        # Store department info (you can extend the database schema to include this)
                        st.session_state.agent_department = department
                    else:
                        st.error(result)

    # Additional information for agents
    with st.expander("ℹ️ **About Resolution Agent Portal**"):
        st.markdown("""
        **Agent Responsibilities:**
        - 📋 Review and prioritize complaints based on AI predictions
        - 🎯 Resolve assigned complaints efficiently
        - 📊 Update complaint status and progress
        - 🗺️ Use geographic mapping for optimal routing
        - 📈 Monitor performance analytics
        
        **Key Features:**
        - **AI-Powered Queue**: Complaints sorted by urgency and category
        - **Interactive Map**: Visual representation of complaint locations
        - **Real-time Updates**: Live status tracking and notifications
        - **Performance Analytics**: Track resolution rates and efficiency
        - **Mobile Friendly**: Access dashboard from field locations
        
        **Agent ID Format:**
        - Must start with 'AGT' followed by 4 digits (e.g., AGT1234)
        - Contact your department supervisor for valid Agent IDs
        - Each Agent ID is unique and tied to municipal records
        """)