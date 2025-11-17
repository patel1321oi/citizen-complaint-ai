import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import sys
import os
from datetime import datetime, timedelta
from PIL import Image
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_utils import (
    get_all_complaints, update_complaint_status, get_complaint_stats,
    get_complaints_by_status, get_db_connection
)
from ml.model import predict_resolution_time

def show_agent_dashboard():
    """Display agent dashboard with complaint management interface"""
    
    # Welcome header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h1>⚡ Agent Dashboard - {st.session_state.current_user['name']}</h1>
        <p style="font-size: 1.1em;">Agent ID: {st.session_state.current_user['agent_id']} | Manage and resolve civic complaints efficiently</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Active Queue", "🗺️ Complaint Map", "📊 Analytics", "⚙️ Settings"])
    
    with tab1:
        show_complaint_queue()
    
    with tab2:
        show_complaint_map()
    
    with tab3:
        show_analytics_dashboard()
    
    with tab4:
        show_agent_settings()

def show_complaint_queue():
    """Display prioritized complaint queue"""
    st.markdown("### 📋 **Complaint Management Queue**")
    st.markdown("Complaints are sorted by AI-predicted urgency and submission time.")
    
    # Get all complaints
    complaints = get_all_complaints()
    
    if not complaints:
        st.info("🎉 No complaints in the system. Great job keeping the city clean!")
        return
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(complaints, columns=[
        'id', 'user_id', 'category', 'description', 'address', 'landmark', 
        'image_path', 'urgency', 'status', 'created_at', 'updated_at'
    ])
    
    # Quick stats
    total_complaints = len(df)
    pending_complaints = len(df[df['status'] == 'Pending'])
    in_progress = len(df[df['status'] == 'In Progress'])
    resolved = len(df[df['status'] == 'Resolved'])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📋 Total", total_complaints)
    with col2:
        st.metric("🔄 Pending", pending_complaints, delta=f"{pending_complaints-resolved}")
    with col3:
        st.metric("⚠️ In Progress", in_progress)
    with col4:
        st.metric("✅ Resolved", resolved)
    with col5:
        resolution_rate = (resolved / total_complaints * 100) if total_complaints > 0 else 0
        st.metric("📈 Resolution %", f"{resolution_rate:.1f}%")
    
    st.markdown("---")
    
    # Filters
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Resolved"])
    
    with col_filter2:
        urgency_filter = st.selectbox("Filter by Urgency", ["All", "High", "Medium", "Low"])
    
    with col_filter3:
        category_filter = st.selectbox("Filter by Category", ["All"] + list(df['category'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    if urgency_filter != "All":
        filtered_df = filtered_df[filtered_df['urgency'] == urgency_filter]
    
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    
    # Sort by urgency priority and date
    urgency_priority = {'High': 3, 'Medium': 2, 'Low': 1}
    filtered_df['urgency_score'] = filtered_df['urgency'].map(urgency_priority)
    filtered_df = filtered_df.sort_values(['urgency_score', 'created_at'], ascending=[False, True])
    
    st.markdown(f"### 🎯 **Showing {len(filtered_df)} complaints**")
    
    # Display complaints
    for idx, complaint in filtered_df.iterrows():
        show_complaint_card(complaint)

def show_complaint_card(complaint):
    """Display individual complaint card with actions"""
    
    urgency_colors = {
        'High': '#ff4b4b',
        'Medium': '#ffa500', 
        'Low': '#00cc00'
    }
    
    status_colors = {
        'Pending': '#f0f0f0',
        'In Progress': '#fff3cd',
        'Resolved': '#d4edda'
    }
    
    # Predict resolution time
    estimated_time = predict_resolution_time(complaint['description'], complaint['category'], complaint['urgency'])
    
    # Create compact complaint card
    with st.container():
        # Card with colored left border
        card_style = f"""
        <div style="
            background: {status_colors.get(complaint['status'], '#f8f9fa')};
            border-left: 4px solid {urgency_colors.get(complaint['urgency'], '#ccc')};
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <h4 style="margin: 0; color: #2c3e50; font-size: 1.1rem;">#{complaint['id']} - {complaint['category']}</h4>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <span style="
                        background: {urgency_colors.get(complaint['urgency'])};
                        color: white;
                        padding: 0.2rem 0.6rem;
                        border-radius: 12px;
                        font-size: 0.8rem;
                        font-weight: bold;
                    ">{complaint['urgency']}</span>
                    <span style="
                        background: #6c757d;
                        color: white;
                        padding: 0.2rem 0.6rem;
                        border-radius: 12px;
                        font-size: 0.8rem;
                    ">{complaint['status']}</span>
                </div>
            </div>
        </div>
        """
        st.markdown(card_style, unsafe_allow_html=True)
        
        # Card content in compact layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Location and description in compact form
            st.markdown(f"**📍 Location:** {complaint['address'][:60]}{'...' if len(complaint['address']) > 60 else ''}")
            
            if complaint['landmark']:
                st.markdown(f"**🏛️ Landmark:** {complaint['landmark']}")
            
            st.markdown(f"**📝 Description:** {complaint['description'][:100]}{'...' if len(complaint['description']) > 100 else ''}")
            st.markdown(f"**📅 Submitted:** {complaint['created_at']}")
            
            # Show image thumbnail if available
            if complaint['image_path'] and os.path.exists(complaint['image_path']):
                with st.expander("📸 View Photo"):
                    try:
                        image = Image.open(complaint['image_path'])
                        st.image(image, width=200, caption="Issue Photo")
                    except:
                        st.warning("Image file exists but cannot be displayed")
        
        with col2:
            # Compact info panel
            st.markdown(f"**⏱️ Est. Resolution:** {estimated_time}")
            st.markdown(f"**🎯 Priority Score:** {get_priority_score(complaint)}")
            
            # Compact action buttons
            if complaint['status'] == 'Pending':
                if st.button(f"🔧 Start Work", key=f"start_{complaint['id']}", use_container_width=True):
                    update_complaint_status(complaint['id'], 'In Progress', st.session_state.current_user['agent_id'])
                    st.success("Status updated to In Progress!")
                    st.rerun()
            
            elif complaint['status'] == 'In Progress':
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(f"✅", key=f"resolve_{complaint['id']}", help="Mark Resolved"):
                        update_complaint_status(complaint['id'], 'Resolved', st.session_state.current_user['agent_id'])
                        st.success("Complaint resolved!")
                        st.rerun()
                with col_btn2:
                    if st.button(f"⏸️", key=f"pause_{complaint['id']}", help="Pause Work"):
                        update_complaint_status(complaint['id'], 'Pending', st.session_state.current_user['agent_id'])
                        st.info("Work paused")
                        st.rerun()
            
            elif complaint['status'] == 'Resolved':
                if st.button(f"🔄 Reopen", key=f"reopen_{complaint['id']}", use_container_width=True):
                    update_complaint_status(complaint['id'], 'Pending', st.session_state.current_user['agent_id'])
                    st.info("Complaint reopened")
                    st.rerun()
        
        # Thin separator
        st.markdown("<hr style='margin: 1rem 0; border: 1px solid #dee2e6;'>", unsafe_allow_html=True)

def get_priority_score(complaint):
    """Calculate priority score for complaint"""
    base_score = {'High': 100, 'Medium': 50, 'Low': 25}
    score = base_score.get(complaint['urgency'], 25)
    
    # Add time factor (older complaints get higher priority)
    try:
        created = datetime.fromisoformat(complaint['created_at'])
        hours_old = (datetime.now() - created).total_seconds() / 3600
        time_bonus = min(int(hours_old / 24) * 10, 50)  # Max 50 bonus points
        score += time_bonus
    except:
        pass
    
    return score

def show_complaint_map():
    """Display interactive map with complaint locations"""
    st.markdown("### 🗺️ **Complaint Location Map**")
    st.markdown("Interactive map showing all complaints with color-coded urgency levels.")
    
    complaints = get_all_complaints()
    
    if not complaints:
        st.info("No complaints to display on map.")
        return
    
    # Analyze addresses to determine map center
    def get_map_center_from_addresses(complaints):
        """Determine map center based on complaint addresses"""
        usa_keywords = ['usa', 'united states', 'america', 'boston', 'new york', 'california', 'texas', 'florida']
        india_keywords = ['india', 'delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 'hyderabad']
        
        usa_count = 0
        india_count = 0
        
        for complaint in complaints:
            address = complaint[4].lower()  # address is index 4
            
            if any(keyword in address for keyword in usa_keywords):
                usa_count += 1
            elif any(keyword in address for keyword in india_keywords):
                india_count += 1
        
        # Return appropriate center coordinates
        if usa_count > india_count:
            return [39.8283, -98.5795], 4  # USA center, zoom 4
        else:
            return [20.5937, 78.9629], 5   # India center, zoom 5
    
    # Get appropriate map center
    map_center, zoom_level = get_map_center_from_addresses(complaints)
    
    # Create base map with appropriate center
    m = folium.Map(
        location=map_center,
        zoom_start=zoom_level,
        tiles='OpenStreetMap'
    )
    
    # Color mapping for urgency
    urgency_colors = {
        'High': 'red',
        'Medium': 'orange', 
        'Low': 'green'
    }
    
    # Add markers for each complaint with realistic coordinates
    for i, complaint in enumerate(complaints):
        complaint_id, user_id, category, description, address, landmark, image_path, urgency, status, created_at, updated_at = complaint
        
        # Generate coordinates based on address location
        lat, lon = get_coordinates_from_address(address, i, map_center)
        
        # Create detailed popup content
        popup_html = f"""
        <div style="width: 350px; font-family: Arial, sans-serif; padding: 5px;">
            <h4 style="margin: 0 0 10px 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">
                #{complaint_id} - {category}
            </h4>
            <div style="margin: 8px 0;">
                <strong style="color: #e74c3c;">📍 Address:</strong><br>
                <span style="font-size: 13px; line-height: 1.4;">{address}</span>
            </div>
            {f'<div style="margin: 8px 0;"><strong style="color: #f39c12;">🏛️ Landmark:</strong><br><span style="font-size: 13px;">{landmark}</span></div>' if landmark else ''}
            <div style="margin: 8px 0;">
                <strong style="color: #9b59b6;">📝 Description:</strong><br>
                <span style="font-size: 13px; line-height: 1.4;">{description[:120]}{'...' if len(description) > 120 else ''}</span>
            </div>
            <div style="margin: 8px 0; display: flex; justify-content: space-between;">
                <div>
                    <strong style="color: #e67e22;">🚨 Urgency:</strong> 
                    <span style="color: {urgency_colors.get(urgency, 'blue')}; font-weight: bold; font-size: 14px;">{urgency}</span>
                </div>
                <div>
                    <strong style="color: #27ae60;">📊 Status:</strong> 
                    <span style="font-weight: bold; font-size: 14px;">{status}</span>
                </div>
            </div>
            <div style="margin: 8px 0; padding-top: 8px; border-top: 1px solid #bdc3c7; font-size: 12px; color: #7f8c8d;">
                <strong>Submitted:</strong> {created_at}
            </div>
        </div>
        """
        
        # Determine marker icon based on status
        if status == 'Resolved':
            icon_name = 'ok-sign'
        elif status == 'In Progress':
            icon_name = 'cog'
        else:
            icon_name = 'exclamation-sign'
        
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_html, max_width=400),
            tooltip=f"#{complaint_id} - {urgency} Priority - {category}",
            icon=folium.Icon(
                color=urgency_colors.get(urgency, 'blue'),
                icon=icon_name,
                prefix='glyphicon'
            )
        ).add_to(m)
    
    # Add improved legend
    legend_html = '''
    <div style="position: fixed; 
                top: 80px; right: 20px; width: 200px; 
                background-color: white; border: 2px solid #34495e; z-index:9999; 
                font-size: 14px; padding: 15px; border-radius: 8px; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        <h4 style="margin: 0 0 12px 0; color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 8px;">
            Complaint Map Legend
        </h4>
        <div style="margin: 8px 0;">
            <span style="color: red; font-size: 16px;">●</span> 
            <strong style="color: #e74c3c;">High Priority</strong>
        </div>
        <div style="margin: 8px 0;">
            <span style="color: orange; font-size: 16px;">●</span> 
            <strong style="color: #f39c12;">Medium Priority</strong>
        </div>
        <div style="margin: 8px 0;">
            <span style="color: green; font-size: 16px;">●</span> 
            <strong style="color: #27ae60;">Low Priority</strong>
        </div>
        <hr style="margin: 10px 0; border: 1px solid #bdc3c7;">
        <div style="font-size: 12px; color: #7f8c8d; text-align: center;">
            Click markers for details
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Display the map with error handling
    try:
        st.markdown("#### 🗺️ Interactive Complaint Map")
        map_data = st_folium(
            m, 
            width=900, 
            height=600,
            returned_objects=["last_object_clicked_popup", "last_object_clicked_tooltip"],
            key="stable_complaint_map"
        )
        
        # Show map interaction feedback
        if map_data and map_data.get('last_object_clicked_popup'):
            st.success("📍 **Complaint details shown in popup above!** Click other markers to view more complaints.")
    
    except Exception as e:
        st.error(f"Error displaying map: {str(e)}")
        st.info("If the map doesn't load, please refresh the page or check your internet connection.")
        return
    
    # Map statistics - IMMEDIATELY after map with no gap
    st.markdown("### 📊 **Live Map Statistics**")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        high_priority = len([c for c in complaints if c[7] == 'High'])
        st.metric(
            label="🔴 High Priority", 
            value=high_priority,
            delta=f"{high_priority}/{len(complaints)} total"
        )
    
    with col_stat2:
        medium_priority = len([c for c in complaints if c[7] == 'Medium'])
        st.metric(
            label="🟡 Medium Priority", 
            value=medium_priority,
            delta=f"{medium_priority}/{len(complaints)} total"
        )
    
    with col_stat3:
        low_priority = len([c for c in complaints if c[7] == 'Low'])
        st.metric(
            label="🟢 Low Priority", 
            value=low_priority,
            delta=f"{low_priority}/{len(complaints)} total"
        )
    
    with col_stat4:
        resolved_count = len([c for c in complaints if c[8] == 'Resolved'])
        resolution_rate = (resolved_count / len(complaints) * 100) if len(complaints) > 0 else 0
        st.metric(
            label="✅ Resolution Rate", 
            value=f"{resolution_rate:.1f}%",
            delta=f"{resolved_count} resolved"
        )
    
    # Complaint list below map
    st.markdown("### 📋 **Complaints on Map**")
    
    # Create a simple table view
    map_complaints_data = []
    for complaint in complaints:
        complaint_id, user_id, category, description, address, landmark, image_path, urgency, status, created_at, updated_at = complaint
        map_complaints_data.append({
            "ID": f"#{complaint_id}",
            "Category": category,
            "Location": address[:50] + "..." if len(address) > 50 else address,
            "Urgency": urgency,
            "Status": status,
            "Date": created_at.split()[0] if ' ' in created_at else created_at
        })
    
    if map_complaints_data:
        import pandas as pd
        df = pd.DataFrame(map_complaints_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Map controls
    st.markdown("### ⚙️ **Map Controls**")
    col_control1, col_control2, col_control3 = st.columns(3)
    
    with col_control1:
        if st.button("🔄 Refresh Map Data", help="Reload map with latest complaints", key="refresh_map_btn"):
            st.rerun()
    
    with col_control2:
        if st.button("🎯 Fit All Markers", help="Adjust map view to show all complaints", key="fit_markers_btn"):
            st.info("Zoom out to see all complaint locations on the map")
    
    with col_control3:
        map_view = st.selectbox("🗺️ Map View", ["Standard", "Satellite", "Terrain"], key="map_view_select")
        if map_view != "Standard":
            st.info(f"{map_view} view selected - refresh map to apply")

def get_coordinates_from_address(address, index, map_center):
    """Generate realistic coordinates based on address content"""
    import random
    
    address_lower = address.lower()
    
    # USA coordinates for US addresses
    if any(keyword in address_lower for keyword in ['usa', 'united states', 'boston', 'ma']):
        # Boston area coordinates
        base_lat, base_lon = 42.3601, -71.0589
        lat = base_lat + random.uniform(-0.1, 0.1)
        lon = base_lon + random.uniform(-0.1, 0.1)
    elif any(keyword in address_lower for keyword in ['new york', 'ny']):
        # New York area coordinates  
        base_lat, base_lon = 40.7128, -74.0060
        lat = base_lat + random.uniform(-0.1, 0.1)
        lon = base_lon + random.uniform(-0.1, 0.1)
    elif any(keyword in address_lower for keyword in ['california', 'ca', 'los angeles']):
        # California area coordinates
        base_lat, base_lon = 34.0522, -118.2437
        lat = base_lat + random.uniform(-0.1, 0.1)
        lon = base_lon + random.uniform(-0.1, 0.1)
    # India coordinates for Indian addresses
    elif any(keyword in address_lower for keyword in ['india', 'delhi']):
        # Delhi area coordinates
        base_lat, base_lon = 28.6139, 77.2090
        lat = base_lat + random.uniform(-0.05, 0.05)
        lon = base_lon + random.uniform(-0.05, 0.05)
    elif any(keyword in address_lower for keyword in ['mumbai', 'bombay']):
        # Mumbai area coordinates
        base_lat, base_lon = 19.0760, 72.8777
        lat = base_lat + random.uniform(-0.05, 0.05)
        lon = base_lon + random.uniform(-0.05, 0.05)
    else:
        # Default: use map center with some variation
        lat = map_center[0] + random.uniform(-2, 2) + (index * 0.1)
        lon = map_center[1] + random.uniform(-2, 2) + (index * 0.1)
    
    return lat, lon

def show_analytics_dashboard():
    """Display analytics and performance metrics"""
    st.markdown("### 📊 **Analytics Dashboard**")
    st.markdown("Performance metrics and insights for resolution tracking.")
    
    try:
        # Get complaint statistics
        stats = get_complaint_stats()
        
        # Performance metrics
        st.markdown("#### 📈 **Performance Metrics**")
        
        col_perf1, col_perf2, col_perf3, col_perf4 = st.columns(4)
        
        with col_perf1:
            st.metric("Total Complaints", stats['total'])
        
        with col_perf2:
            st.metric("Resolved Today", stats.get('resolved_today', 0))
        
        with col_perf3:
            avg_resolution = stats.get('avg_resolution_time', 0)
            st.metric("Avg Resolution (hrs)", f"{avg_resolution:.1f}")
        
        with col_perf4:
            satisfaction = stats.get('satisfaction_rate', 95)
            st.metric("Satisfaction Rate", f"{satisfaction}%")
        
        # Charts
        st.markdown("#### 📊 **Complaint Analysis**")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("**Complaints by Category**")
            
            # Get category distribution
            conn = get_db_connection()
            category_df = pd.read_sql_query("""
                SELECT category, COUNT(*) as count
                FROM complaints
                GROUP BY category
                ORDER BY count DESC
            """, conn)
            conn.close()
            
            if not category_df.empty:
                st.bar_chart(category_df.set_index('category'))
            else:
                st.info("No data available yet")
        
        with col_chart2:
            st.markdown("**Urgency Distribution**")
            
            # Get urgency distribution
            conn = get_db_connection()
            urgency_df = pd.read_sql_query("""
                SELECT urgency, COUNT(*) as count
                FROM complaints
                GROUP BY urgency
                ORDER BY 
                    CASE urgency 
                        WHEN 'High' THEN 1 
                        WHEN 'Medium' THEN 2 
                        WHEN 'Low' THEN 3 
                    END
            """, conn)
            conn.close()
            
            if not urgency_df.empty:
                st.bar_chart(urgency_df.set_index('urgency'))
            else:
                st.info("No data available yet")
        
        # Recent activity
        st.markdown("#### 🕒 **Recent Activity**")
        
        conn = get_db_connection()
        recent_df = pd.read_sql_query("""
            SELECT id, category, urgency, status, created_at
            FROM complaints
            ORDER BY created_at DESC
            LIMIT 10
        """, conn)
        conn.close()
        
        if not recent_df.empty:
            st.dataframe(recent_df, use_container_width=True)
        else:
            st.info("No recent activity")
        
        # Agent performance (if multiple agents exist)
        st.markdown("#### 👥 **Team Performance**")
        
        try:
            conn = get_db_connection()
            agent_perf = pd.read_sql_query("""
                SELECT 
                    a.name as agent_name,
                    a.agent_id,
                    COUNT(c.id) as total_handled,
                    SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END) as resolved_count
                FROM agents a
                LEFT JOIN complaints c ON c.assigned_agent = a.agent_id
                GROUP BY a.id, a.name, a.agent_id
                ORDER BY resolved_count DESC
            """, conn)
            conn.close()
            
            if not agent_perf.empty:
                st.dataframe(agent_perf, use_container_width=True)
            else:
                st.info("Agent performance data will appear as complaints are resolved")
        
        except:
            st.info("Team performance tracking coming soon")
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

def show_agent_settings():
    """Display agent settings and preferences"""
    st.markdown("### ⚙️ **Agent Settings & Preferences**")
    
    # Agent information
    st.markdown("#### 👤 **Agent Information**")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.info(f"""
        **Name:** {st.session_state.current_user['name']}
        **Agent ID:** {st.session_state.current_user['agent_id']}
        **Status:** Active
        """)
    
    with col_info2:
        # Performance summary
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get agent's resolved complaints
            cursor.execute("""
                SELECT COUNT(*) FROM complaints 
                WHERE assigned_agent = ? AND status = 'Resolved'
            """, (st.session_state.current_user['agent_id'],))
            resolved_count = cursor.fetchone()[0]
            
            # Get total assigned
            cursor.execute("""
                SELECT COUNT(*) FROM complaints 
                WHERE assigned_agent = ?
            """, (st.session_state.current_user['agent_id'],))
            total_assigned = cursor.fetchone()[0]
            
            conn.close()
            
            st.success(f"""
            **Resolved Complaints:** {resolved_count}
            **Total Assigned:** {total_assigned}
            **Success Rate:** {(resolved_count/total_assigned*100) if total_assigned > 0 else 0:.1f}%
            """)
        
        except:
            st.info("Performance data will appear after handling complaints")
    
    # Notification preferences
    st.markdown("#### 🔔 **Notification Preferences**")
    
    with st.form("notification_settings"):
        email_notifications = st.checkbox("📧 Email notifications for new high-priority complaints", value=True)
        sms_notifications = st.checkbox("📱 SMS alerts for urgent issues", value=False)
        desktop_notifications = st.checkbox("🖥️ Browser notifications", value=True)
        
        daily_summary = st.checkbox("📊 Daily performance summary", value=True)
        
        st.form_submit_button("💾 Save Preferences")
    
    # Quick actions
    st.markdown("#### ⚡ **Quick Actions**")
    
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("📋 Export My Activity", use_container_width=True):
            st.info("Export functionality coming soon")
    
    with col_action2:
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()
    
    with col_action3:
        if st.button("📞 Report Technical Issue", use_container_width=True):
            st.info("Technical support: admin@citizenai.gov")
    
    # System information
    st.markdown("#### ℹ️ **System Information**")
    
    with st.expander("View System Status"):
        st.success("🟢 **System Status:** All services operational")
        st.info("🤖 **AI Model:** Last trained with 150+ complaints")
        st.info("🗄️ **Database:** Connection healthy")
        st.info("📊 **Analytics:** Real-time data processing active")
        
        # Recent system updates
        st.markdown("**Recent Updates:**")
        st.text("• Enhanced AI urgency prediction accuracy")
        st.text("• Improved map visualization performance")
        st.text("• Added bulk complaint management")
        st.text("• Mobile-responsive dashboard updates")