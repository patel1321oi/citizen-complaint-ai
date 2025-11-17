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

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def create_user(name, email, password):
    """Create a new user account"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Email already registered"
        
        # Insert new user
        hashed_password = hash_password(password)
        cursor.execute("""
            INSERT INTO users (name, email, password, created_at)
            VALUES (?, ?, ?, ?)
        """, (name, email, hashed_password, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        return True, "Account created successfully"
    
    except Exception as e:
        return False, f"Error creating account: {str(e)}"

def authenticate_user(email, password):
    """Authenticate user login"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(password)
        cursor.execute("""
            SELECT id, name, email FROM users 
            WHERE email = ? AND password = ?
        """, (email, hashed_password))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, {
                'id': user[0],
                'name': user[1],
                'email': user[2]
            }
        else:
            return False, "Invalid email or password"
    
    except Exception as e:
        return False, f"Authentication error: {str(e)}"

def show_user_auth():
    """Display user authentication interface"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
        <h1>🏠 Citizen Portal</h1>
        <p style="font-size: 1.1em;">Join thousands of citizens making their city better</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_signup_form()

def show_login_form():
    """Display login form"""
    st.markdown("### 🔑 **Login to Your Account**")
    
    with st.form("login_form"):
        col1, col2 = st.columns([1, 2])
        
        with col2:
            email = st.text_input(
                "📧 Email Address",
                placeholder="Enter your email address",
                help="Use the email you registered with"
            )
            
            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your password",
                help="Enter your account password"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                login_btn = st.form_submit_button(
                    "🚀 Login",
                    type="primary",
                    use_container_width=True
                )
        
        if login_btn:
            if not email or not password:
                st.error("Please fill in all fields")
            elif not validate_email(email):
                st.error("Please enter a valid email address")
            else:
                success, result = authenticate_user(email, password)
                
                if success:
                    st.session_state.authenticated = True
                    st.session_state.current_user = result
                    st.session_state.page = 'user_dashboard'
                    st.success(f"Welcome back, {result['name']}!")
                    st.rerun()
                else:
                    st.error(result)

def show_signup_form():
    """Display signup form"""
    st.markdown("### 📝 **Create New Account**")
    
    with st.form("signup_form"):
        col1, col2 = st.columns([1, 2])
        
        with col2:
            name = st.text_input(
                "👤 Full Name",
                placeholder="Enter your full name",
                help="This name will be displayed on your complaints"
            )
            
            email = st.text_input(
                "📧 Email Address",
                placeholder="Enter your email address",
                help="We'll use this for login and notifications"
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
            
            # Terms and conditions
            terms_agreed = st.checkbox(
                "I agree to the Terms of Service and Privacy Policy",
                help="Required to create an account"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                signup_btn = st.form_submit_button(
                    "🎉 Create Account",
                    type="primary",
                    use_container_width=True
                )
        
        if signup_btn:
            # Validation
            if not all([name, email, password, confirm_password]):
                st.error("Please fill in all fields")
            elif not validate_email(email):
                st.error("Please enter a valid email address")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif not terms_agreed:
                st.error("Please agree to the Terms of Service")
            else:
                # Validate password strength
                is_valid, message = validate_password(password)
                if not is_valid:
                    st.error(message)
                else:
                    # Create account
                    success, result = create_user(name, email, password)
                    
                    if success:
                        st.success("🎉 Account created successfully!")
                        st.info("Please use the Login tab to access your account")
                        
                        # Auto-fill login form
                        st.session_state.signup_email = email
                    else:
                        st.error(result)

    # Additional information
    with st.expander("ℹ️ **About Citizen Portal**"):
        st.markdown("""
        **What you can do:**
        - 📝 Submit complaints about civic issues
        - 📸 Upload photos or capture images directly
        - 🤖 Get AI-powered urgency predictions
        - 📊 Track resolution progress
        - 🗺️ View complaint locations on map
        
        **Common complaint categories:**
        - Garbage overflow and waste management
        - Drainage and water logging issues
        - Streetlight failures
        - Road damage and potholes
        - Water supply problems
        - Electricity and power issues
        """)