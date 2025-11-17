import streamlit as st
import os
from datetime import datetime
from PIL import Image
import hashlib
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_utils import add_complaint, get_user_complaints, get_db_connection
from ml.model import predict_urgency, train_model_if_needed

def save_uploaded_image(uploaded_file, complaint_type):
    """Save uploaded image and return file path"""
    try:
        # Create directory if it doesn't exist
        os.makedirs("assets/uploaded_images", exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()[:8]
        
        # Get file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        filename = f"{complaint_type}_{timestamp}_{file_hash}.{file_extension}"
        file_path = os.path.join("assets/uploaded_images", filename)
        
        # Save image
        image = Image.open(uploaded_file)
        # Resize if too large (max 1920x1080)
        if image.size[0] > 1920 or image.size[1] > 1080:
            image.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
        
        image.save(file_path, optimize=True, quality=85)
        return file_path
    
    except Exception as e:
        st.error(f"Error saving image: {str(e)}")
        return None

import streamlit as st
import os
from datetime import datetime
from PIL import Image
import hashlib
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_utils import add_complaint, get_user_complaints, get_db_connection
from ml.model import predict_urgency, train_model_if_needed

def add_custom_css():
    """Add custom CSS for better styling"""
    st.markdown("""
    <style>
        .complaint-history-container {
            background: transparent;
            padding: 0;
        }
        .stContainer > div {
            background: transparent !important;
        }
        .complaint-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: none;
        }
        .status-badge {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
            margin: 0 0.25rem;
        }
        .metric-container {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        /* Hide empty streamlit containers */
        .element-container:empty {
            display: none !important;
        }
        .stEmpty {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

def show_user_dashboard():
    """Display user dashboard with complaint submission form"""
    
    # Add custom CSS
    add_custom_css()
    """Display user dashboard with complaint submission form"""
    
    # Welcome header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h1>🏠 Welcome, {st.session_state.current_user['name']}!</h1>
        <p style="font-size: 1.1em;">Submit civic complaints and help make your city better</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📝 Submit Complaint", "📊 My Complaints", "ℹ️ Help & Guidelines"])
    
    with tab1:
        show_complaint_form()
    
    with tab2:
        show_user_complaints()
    
    with tab3:
        show_help_guidelines()

def show_complaint_form():
    """Display complaint submission form"""
    st.markdown("### 📋 **Submit New Complaint**")
    st.markdown("Help us improve your city by reporting civic issues. Our AI will predict the urgency automatically.")
    
    with st.form("complaint_form", clear_on_submit=True):
        # Basic complaint information
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox(
                "🏷️ **Complaint Category**",
                options=[
                    "Garbage & Waste Management",
                    "Drainage & Water Logging",
                    "Streetlight & Electricity",
                    "Roads & Potholes",
                    "Water Supply Issues",
                    "Public Safety & Security",
                    "Noise Pollution",
                    "Tree Fall & Maintenance",
                    "Traffic & Parking",
                    "Other Municipal Issues"
                ],
                help="Select the category that best describes your complaint"
            )
            
            priority_level = st.radio(
                "🚨 **How urgent do you think this is?**",
                options=["Low", "Medium", "High"],
                horizontal=True,
                help="Your assessment - our AI will provide its own prediction"
            )
        
        with col2:
            address = st.text_area(
                "📍 **Location/Address**",
                placeholder="Enter the exact location where the issue is occurring...",
                height=100,
                help="Be as specific as possible for faster resolution"
            )
            
            landmark = st.text_input(
                "🏛️ **Nearby Landmark** (Optional)",
                placeholder="e.g., Near City Mall, Opposite Bus Station",
                help="This helps agents locate the issue quickly"
            )
        
        # Complaint description
        description = st.text_area(
            "📝 **Describe the Issue**",
            placeholder="Provide detailed description of the problem...",
            height=150,
            help="Include when you noticed it, how it affects you, and any other relevant details"
        )
        
        # Image upload section
        st.markdown("### 📸 **Add Photo Evidence** (Optional)")
        st.markdown("Visual evidence helps resolve complaints faster and more accurately.")
        
        image_option = st.radio(
            "Choose how to add photo:",
            options=["No Photo", "Upload from Device", "Take Photo with Camera"],
            horizontal=True,
            help="Select your preferred method to add visual evidence"
        )
        
        uploaded_image = None
        camera_image = None
        
        # Show appropriate input based on selection
        if image_option == "Upload from Device":
            st.markdown("#### 📤 Upload Image File")
            uploaded_image = st.file_uploader(
                "Choose an image file",
                type=['png', 'jpg', 'jpeg', 'gif'],
                help="Upload a clear photo showing the issue (PNG, JPG, JPEG, GIF supported)",
                key="complaint_file_uploader"
            )
            
            if uploaded_image is not None:
                # Display preview of uploaded image
                col_preview1, col_preview2 = st.columns([1, 2])
                with col_preview1:
                    st.success("✅ Image uploaded successfully!")
                    st.info(f"**File:** {uploaded_image.name}")
                    st.info(f"**Size:** {len(uploaded_image.getvalue())/1024:.1f} KB")
                with col_preview2:
                    try:
                        image = Image.open(uploaded_image)
                        st.image(image, caption="Preview of uploaded image", width=300)
                    except Exception as e:
                        st.error(f"Could not display image preview: {str(e)}")
        
        elif image_option == "Take Photo with Camera":
            st.markdown("#### 📷 Capture Photo with Camera")
            st.info("💡 **Tip:** Make sure to grant camera permissions in your browser")
            
            camera_image = st.camera_input(
                "Take a photo of the issue",
                help="Click the camera button to capture a photo",
                key="complaint_camera_input"
            )
            
            if camera_image is not None:
                # Display confirmation and preview
                col_camera1, col_camera2 = st.columns([1, 2])
                with col_camera1:
                    st.success("✅ Photo captured successfully!")
                    st.info(f"**Size:** {len(camera_image.getvalue())/1024:.1f} KB")
                with col_camera2:
                    try:
                        st.image(camera_image, caption="Captured photo", width=300)
                    except Exception as e:
                        st.error(f"Could not display captured photo: {str(e)}")
        
        elif image_option == "No Photo":
            st.markdown("#### ℹ️ No Photo Selected")
            st.info("You can submit your complaint without a photo. However, adding visual evidence helps authorities understand and resolve issues more quickly.")
            
            # Show example of what good photos look like
            with st.expander("📖 What makes a good complaint photo?"):
                st.markdown("""
                **Good complaint photos should:**
                - 📐 **Be clear and well-lit** - Take photos during daylight when possible
                - 🎯 **Focus on the problem** - Show the specific issue clearly
                - 📏 **Include context** - Show surrounding area for location reference
                - 🏷️ **Show scale** - Include objects for size comparison when relevant
                
                **Examples of effective photos:**
                - Pothole: Show the hole with road markings or nearby objects for scale
                - Garbage: Show the pile with street signs or buildings for location
                - Streetlight: Show the dark area and the non-functioning light
                - Water leak: Show the source and extent of the water damage
                """)
        
        # Additional photo guidelines
        if image_option != "No Photo":
            with st.expander("📋 Photo Guidelines & Tips"):
                st.markdown("""
                **📸 Photo Requirements:**
                - **Supported formats:** PNG, JPG, JPEG, GIF
                - **Maximum size:** 200MB per image
                - **Recommended:** Well-lit, clear, and focused images
                
                **🔒 Privacy & Safety:**
                - Avoid including personal information in photos
                - Don't photograph people without their consent
                - Be safe when taking photos near traffic or dangerous areas
                
                **⚡ Troubleshooting:**
                - **Camera not working?** Check browser permissions
                - **Upload failing?** Try a smaller file size
                - **Image too dark?** Use flash or take photo during daylight
                """)
        
        # Visual separator
        st.markdown("---")
        
        col3, col4 = st.columns(2)
        with col3:
            email_updates = st.checkbox("📧 Email updates on resolution", value=True)
        with col4:
            sms_updates = st.checkbox("📱 SMS notifications (if available)")
        
        # Submit button
        col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
        with col_submit2:
            submit_btn = st.form_submit_button(
                "🚀 Submit Complaint",
                type="primary",
                use_container_width=True
            )
        
        # Form submission logic
        if submit_btn:
            if not description.strip():
                st.error("❌ Please provide a description of the issue")
            elif not address.strip():
                st.error("❌ Please provide the location/address")
            else:
                try:
                    # Process image if provided
                    image_path = None
                    if uploaded_image:
                        image_path = save_uploaded_image(uploaded_image, category.replace(" ", "_").lower())
                        if image_path:
                            st.info(f"📸 Image saved successfully: {os.path.basename(image_path)}")
                        else:
                            st.warning("⚠️ Image could not be saved, but complaint will still be submitted.")
                    
                    # Get AI prediction for urgency
                    with st.spinner("🤖 AI is analyzing your complaint..."):
                        ai_urgency = predict_urgency(description, category)
                    
                    # Debug info
                    st.info(f"🔍 Debug: User ID: {st.session_state.current_user['id']}, AI Urgency: {ai_urgency}")
                    
                    # Add complaint to database
                    complaint_id = add_complaint(
                        user_id=st.session_state.current_user['id'],
                        category=category,
                        description=description,
                        address=address,
                        landmark=landmark if landmark.strip() else None,
                        image_path=image_path,
                        urgency=ai_urgency,
                        user_priority=priority_level
                    )
                    
                    if complaint_id:
                        # Train model in background
                        try:
                            train_model_if_needed()
                        except Exception as train_error:
                            print(f"⚠️ Model training error: {train_error}")
                            # Continue even if training fails
                        
                        # Success message
                        st.success("🎉 **Complaint Submitted Successfully!**")
                        
                        # Display complaint details
                        st.markdown("---")
                        st.markdown("### 📋 **Complaint Details**")
                        
                        col_detail1, col_detail2 = st.columns(2)
                        
                        with col_detail1:
                            st.info(f"""
                            **Complaint ID:** {complaint_id}
                            **Category:** {category}
                            **Your Priority:** {priority_level}
                            **AI Predicted Urgency:** {ai_urgency}
                            """)
                        
                        with col_detail2:
                            urgency_color = {
                                'High': '🔴',
                                'Medium': '🟡', 
                                'Low': '🟢'
                            }
                            
                            st.markdown(f"""
                            **Status:** 🔄 Pending
                            
                            **Urgency Level:** {urgency_color[ai_urgency]} {ai_urgency}
                            
                            **Location:** {address}
                            """)
                        
                        if image_path:
                            st.markdown("**📸 Attached Image:**")
                            try:
                                image = Image.open(image_path)
                                st.image(image, width=400, caption="Issue Photo")
                            except:
                                st.warning("Image uploaded but cannot be displayed")
                        
                        # Final message
                        st.markdown("### 💬 **What's Next?**")
                        st.success("""
                        ✅ **Your complaint will be resolved soon by the responsible authorities.**
                        
                        📧 You'll receive updates via email as the status changes.
                        
                        🔍 You can track progress in the "My Complaints" tab.
                        """)
                    
                    else:
                        st.error("❌ Error submitting complaint. Please try again.")
                        st.error("🔍 Check the console for detailed error information.")
                        
                        # Show debug information
                        with st.expander("🛠️ Debug Information"):
                            st.write("**Database Status:**")
                            try:
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute("SELECT COUNT(*) FROM complaints")
                                count = cursor.fetchone()[0]
                                conn.close()
                                st.success(f"✅ Database connection successful. Total complaints: {count}")
                            except Exception as db_error:
                                st.error(f"❌ Database error: {db_error}")
                            
                            st.write("**Session State:**")
                            st.write(f"Current User: {st.session_state.current_user}")
                            
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
                    st.error("Please try again or contact support if the problem persists.")

def show_user_complaints():
    """Display user's complaint history"""
    st.markdown("### 📊 **My Complaint History**")
    
    # Get user complaints
    complaints = get_user_complaints(st.session_state.current_user['id'])
    
    if not complaints:
        st.info("📝 You haven't submitted any complaints yet. Use the 'Submit Complaint' tab to report issues.")
        return
    
    # Display statistics
    total_complaints = len(complaints)
    resolved_complaints = len([c for c in complaints if c[8] == 'Resolved'])  # status is index 8
    pending_complaints = total_complaints - resolved_complaints
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📋 Total Complaints", total_complaints)
    with col2:
        st.metric("✅ Resolved", resolved_complaints)
    with col3:
        st.metric("🔄 Pending", pending_complaints)
    
    st.markdown("---")
    
    # Filter options
    status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Resolved", "In Progress"])
    
    # Display complaints with proper styling
    filtered_complaints = []
    for complaint in complaints:
        if status_filter == "All" or complaint[8] == status_filter:
            filtered_complaints.append(complaint)
    
    if not filtered_complaints:
        st.info(f"No complaints found with status: {status_filter}")
        return
    
    # Display each complaint in a styled container
    for complaint in filtered_complaints:
        complaint_id, user_id, category, description, address, landmark, image_path, urgency, status, created_at, updated_at = complaint
        
        # Status and urgency styling
        status_colors = {
            'Pending': {'bg': '#fff3cd', 'text': '#856404'},
            'In Progress': {'bg': '#d1ecf1', 'text': '#0c5460'},
            'Resolved': {'bg': '#d4edda', 'text': '#155724'}
        }
        
        urgency_colors = {
            'High': {'bg': '#f8d7da', 'text': '#721c24', 'border': '#dc3545'},
            'Medium': {'bg': '#fff3cd', 'text': '#856404', 'border': '#ffc107'},
            'Low': {'bg': '#d4edda', 'text': '#155724', 'border': '#28a745'}
        }
        
        urgency_emoji = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
        status_emoji = {'Pending': '🔄', 'In Progress': '⚠️', 'Resolved': '✅'}
        
        # Get colors
        status_style = status_colors.get(status, {'bg': '#f8f9fa', 'text': '#6c757d'})
        urgency_style = urgency_colors.get(urgency, {'bg': '#f8f9fa', 'text': '#6c757d', 'border': '#6c757d'})
        
        # Create complaint card
        with st.container():
            # Header with ID and badges
            col_header1, col_header2 = st.columns([2, 1])
            
            with col_header1:
                st.markdown(f"#### 📋 #{complaint_id} - {category}")
            
            with col_header2:
                st.markdown(f"""
                <div style="text-align: right;">
                    <span style="
                        background: {status_style['bg']}; 
                        color: {status_style['text']};
                        padding: 0.25rem 0.6rem; 
                        border-radius: 15px; 
                        font-size: 0.8rem;
                        font-weight: bold;
                        margin-left: 0.5rem;
                    ">
                        {status_emoji.get(status, '❓')} {status}
                    </span>
                    <span style="
                        background: {urgency_style['bg']}; 
                        color: {urgency_style['text']};
                        padding: 0.25rem 0.6rem; 
                        border-radius: 15px; 
                        font-size: 0.8rem;
                        font-weight: bold;
                        border: 1px solid {urgency_style['border']};
                        margin-left: 0.5rem;
                    ">
                        {urgency_emoji.get(urgency, '❓')} {urgency}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            # Complaint details
            col_details1, col_details2 = st.columns([3, 1])
            
            with col_details1:
                st.markdown(f"""
                **📝 Description:** {description}
                
                **📍 Location:** {address}
                """)
                
                if landmark:
                    st.write(f"**🏛️ Landmark:** {landmark}")
                
                st.write(f"**📅 Submitted:** {created_at}")
                
                # Show image if available
                if image_path and os.path.exists(image_path):
                    with st.expander("📸 View Photo"):
                        try:
                            image = Image.open(image_path)
                            st.image(image, width=300, caption="Issue Photo")
                        except Exception as e:
                            st.warning("Cannot display image")
            
            with col_details2:
                # Status-specific information
                if status == 'Resolved':
                    st.success("🎉 **Completed!**")
                    st.write("Issue has been resolved.")
                elif status == 'In Progress':
                    st.warning("⚠️ **Active**")
                    st.write("Team is working on this.")
                else:
                    st.info("🔄 **Queued**")
                    st.write("Waiting for assignment.")
                
                # Quick info
                st.markdown(f"""
                **Complaint Details:**
                - ID: #{complaint_id}
                - Priority: {urgency}
                - Status: {status}
                """)
            
            # Separator
            st.markdown("---")

def show_help_guidelines():
    """Display help and guidelines for users"""
    st.markdown("### ℹ️ **Help & Guidelines**")
    
    # Guidelines accordion
    with st.expander("📋 **How to Submit Effective Complaints**"):
        st.markdown("""
        **For faster resolution, please:**
        
        1. **Be Specific**: Provide exact location with nearby landmarks
        2. **Add Photos**: Visual evidence helps agents understand the issue better
        3. **Detailed Description**: Explain when you noticed it, how it affects you
        4. **Choose Correct Category**: This helps route to the right department
        5. **Monitor Progress**: Check back regularly for updates
        
        **Example of a Good Complaint:**
        > "Large pothole on Main Street, 50 meters before City Mall traffic signal. 
        > Water accumulates here during rain causing traffic jams. 
        > Issue started after last week's heavy rainfall."
        """)
    
    with st.expander("🤖 **Understanding AI Urgency Prediction**"):
        st.markdown("""
        Our AI analyzes your complaint text and predicts urgency based on:
        
        - **Keywords**: Emergency, danger, safety, health hazard
        - **Category**: Public safety issues get higher priority
        - **Impact**: Issues affecting many people get higher urgency
        - **Time Sensitivity**: Problems that worsen quickly
        
        **Urgency Levels:**
        - 🔴 **High**: Immediate attention needed (safety, health hazards)
        - 🟡 **Medium**: Should be resolved within a few days
        - 🟢 **Low**: General maintenance, can wait for scheduled resolution
        """)
    
    with st.expander("📞 **Contact & Support**"):
        st.markdown("""
        **Need Help?**
        
        - **Technical Issues**: Use the feedback button below
        - **Emergency**: Call emergency services directly (don't rely on this app)
        - **Follow Up**: Check "My Complaints" tab for updates
        
        **Response Times:**
        - High Priority: 24-48 hours
        - Medium Priority: 3-7 days  
        - Low Priority: 1-2 weeks
        
        **Complaint Categories:**
        - 🗑️ Garbage & Waste Management
        - 💧 Drainage & Water Issues
        - 💡 Streetlight & Electricity
        - 🛣️ Roads & Infrastructure
        - 🚔 Public Safety
        """)
    
    # Quick stats
    st.markdown("### 📊 **Platform Statistics**")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total complaints
        cursor.execute("SELECT COUNT(*) FROM complaints")
        total = cursor.fetchone()[0]
        
        # Get resolved complaints
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
        resolved = cursor.fetchone()[0]
        
        conn.close()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Complaints", total)
        with col2:
            st.metric("Resolved Issues", resolved)
        with col3:
            resolution_rate = (resolved / total * 100) if total > 0 else 0
            st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
    
    except:
        st.info("Statistics will be available once complaints are submitted")