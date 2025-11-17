#!/usr/bin/env python3
"""
Database Debug and Testing Script for CitiZen AI
Run this script to test database functionality
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_utils import (
    init_database, get_db_connection, add_complaint, 
    get_all_complaints, test_database_connection
)
from auth.user_auth import create_user
from ml.model import predict_urgency

def create_test_user():
    """Create a test user for complaint testing"""
    print("\n📝 Creating test user...")
    
    success, result = create_user(
        name="Test User",
        email="test@example.com", 
        password="test123"
    )
    
    if success:
        print(f"✅ Test user created: {result}")
        return True
    else:
        print(f"❌ Failed to create test user: {result}")
        return False

def create_test_complaint():
    """Create a test complaint"""
    print("\n📋 Creating test complaint...")
    
    try:
        # Get test user ID
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = 'test@example.com'")
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            print("❌ Test user not found")
            return False
        
        user_id = user[0]
        
        # Predict urgency
        description = "Water pipe burst flooding the street emergency help needed"
        category = "Water Supply Issues"
        urgency = predict_urgency(description, category)
        
        print(f"🤖 AI predicted urgency: {urgency}")
        
        # Create complaint
        complaint_id = add_complaint(
            user_id=user_id,
            category=category,
            description=description,
            address="123 Test Street, Test City",
            landmark="Near Test Mall",
            image_path=None,
            urgency=urgency,
            user_priority="High"
        )
        
        if complaint_id:
            print(f"✅ Test complaint created with ID: {complaint_id}")
            return True
        else:
            print("❌ Failed to create test complaint")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test complaint: {e}")
        return False

def verify_complaints():
    """Verify complaints can be retrieved"""
    print("\n🔍 Verifying complaint retrieval...")
    
    try:
        complaints = get_all_complaints()
        print(f"✅ Found {len(complaints)} complaints in database")
        
        if complaints:
            # Show first complaint details
            first_complaint = complaints[0]
            print(f"📋 Sample complaint: ID={first_complaint[0]}, Category={first_complaint[2]}, Status={first_complaint[8]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error retrieving complaints: {e}")
        return False

def main():
    """Run all database tests"""
    print("🧪 CitiZen AI Database Testing Script")
    print("=" * 50)
    
    # Test 1: Initialize database
    print("\n1️⃣ Testing database initialization...")
    try:
        init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return
    
    # Test 2: Test database connection
    print("\n2️⃣ Testing database connection...")
    if not test_database_connection():
        print("❌ Database connection test failed")
        return
    
    # Test 3: Create test user
    print("\n3️⃣ Testing user creation...")
    if not create_test_user():
        print("❌ User creation test failed")
        return
    
    # Test 4: Create test complaint
    print("\n4️⃣ Testing complaint creation...")
    if not create_test_complaint():
        print("❌ Complaint creation test failed")
        return
    
    # Test 5: Verify complaint retrieval
    print("\n5️⃣ Testing complaint retrieval...")
    if not verify_complaints():
        print("❌ Complaint retrieval test failed")
        return
    
    # Test 6: Database statistics
    print("\n6️⃣ Testing database statistics...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM complaints") 
        complaint_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM complaint_history")
        history_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📊 Database Statistics:")
        print(f"   Users: {user_count}")
        print(f"   Complaints: {complaint_count}")
        print(f"   History Records: {history_count}")
        
    except Exception as e:
        print(f"❌ Error getting database statistics: {e}")
        return
    
    print("\n🎉 All database tests passed successfully!")
    print("✅ Database is working correctly")
    print("\n💡 You can now run: streamlit run main.py")

if __name__ == "__main__":
    main()