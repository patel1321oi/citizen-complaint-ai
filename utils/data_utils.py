import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta
import hashlib

# Database path
DATABASE_PATH = "db/complaints.db"

def ensure_db_directory():
    """Ensure the db directory exists"""
    os.makedirs("db", exist_ok=True)

def get_db_connection():
    """Get database connection"""
    ensure_db_directory()
    return sqlite3.connect(DATABASE_PATH)

def init_database():
    """Initialize the SQLite database and create all necessary tables"""
    ensure_db_directory()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            last_login DATETIME,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Create agents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            agent_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            last_login DATETIME,
            status TEXT DEFAULT 'active',
            department TEXT,
            total_resolved INTEGER DEFAULT 0
        )
    ''')
    
    # Create complaints table with comprehensive fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            address TEXT NOT NULL,
            landmark TEXT,
            image_path TEXT,
            urgency TEXT NOT NULL,
            user_priority TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            assigned_agent TEXT,
            resolution_notes TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME,
            resolved_at DATETIME,
            estimated_resolution_time TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (assigned_agent) REFERENCES agents (agent_id)
        )
    ''')
    
    # Create complaint_history table for tracking status changes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaint_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            old_status TEXT,
            new_status TEXT,
            changed_by TEXT,
            change_reason TEXT,
            changed_at DATETIME NOT NULL,
            FOREIGN KEY (complaint_id) REFERENCES complaints (id)
        )
    ''')
    
    # Create feedback table for citizen feedback on resolutions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            comments TEXT,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (complaint_id) REFERENCES complaints (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaints_urgency ON complaints(urgency)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaints_category ON complaints(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaints_created_at ON complaints(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaints_user_id ON complaints(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaints_assigned_agent ON complaints(assigned_agent)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_agents_agent_id ON agents(agent_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaint_history_complaint_id ON complaint_history(complaint_id)')
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully with all tables and indexes!")

def add_complaint(user_id, category, description, address, landmark=None, image_path=None, urgency='Medium', user_priority='Medium'):
    """Add a new complaint to the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        created_at = datetime.now().isoformat()
        
        # Debug: Print what we're trying to insert
        print(f"Inserting complaint: user_id={user_id}, category={category}, urgency={urgency}")
        
        cursor.execute('''
            INSERT INTO complaints 
            (user_id, category, description, address, landmark, image_path, urgency, 
             user_priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, category, description, address, landmark, image_path, urgency, 
              user_priority, 'Pending', created_at, created_at))
        
        complaint_id = cursor.lastrowid
        print(f"✅ Complaint inserted with ID: {complaint_id}")
        
        # Add to complaint history
        cursor.execute('''
            INSERT INTO complaint_history 
            (complaint_id, old_status, new_status, changed_by, change_reason, changed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (complaint_id, None, 'Pending', f'user_{user_id}', 'Initial submission', created_at))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Complaint {complaint_id} successfully saved to database")
        return complaint_id
    
    except Exception as e:
        print(f"❌ Error adding complaint: {e}")
        print(f"Database path: {DATABASE_PATH}")
        print(f"Database exists: {os.path.exists(DATABASE_PATH)}")
        
        # Try to reconnect database
        try:
            init_database()
        except Exception as init_error:
            print(f"❌ Error reinitializing database: {init_error}")
        
        return None

def get_all_complaints():
    """Get all complaints from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, category, description, address, landmark, 
                   image_path, urgency, status, created_at, updated_at
            FROM complaints
            ORDER BY 
                CASE urgency 
                    WHEN 'High' THEN 1 
                    WHEN 'Medium' THEN 2 
                    WHEN 'Low' THEN 3 
                END,
                created_at ASC
        ''')
        
        complaints = cursor.fetchall()
        conn.close()
        
        return complaints
    
    except Exception as e:
        print(f"Error getting complaints: {e}")
        return []

def get_user_complaints(user_id):
    """Get all complaints submitted by a specific user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, category, description, address, landmark, 
                   image_path, urgency, status, created_at, updated_at
            FROM complaints
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        complaints = cursor.fetchall()
        conn.close()
        
        return complaints
    
    except Exception as e:
        print(f"Error getting user complaints: {e}")
        return []

def get_complaints_by_status(status):
    """Get complaints filtered by status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, category, description, address, landmark, 
                   image_path, urgency, status, created_at, updated_at
            FROM complaints
            WHERE status = ?
            ORDER BY created_at DESC
        ''', (status,))
        
        complaints = cursor.fetchall()
        conn.close()
        
        return complaints
    
    except Exception as e:
        print(f"Error getting complaints by status: {e}")
        return []

def update_complaint_status(complaint_id, new_status, agent_id=None, resolution_notes=None):
    """Update complaint status with history tracking"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current status
        cursor.execute('SELECT status FROM complaints WHERE id = ?', (complaint_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False
        
        old_status = result[0]
        updated_at = datetime.now().isoformat()
        
        # Update complaint
        if new_status == 'Resolved':
            cursor.execute('''
                UPDATE complaints
                SET status = ?, assigned_agent = ?, resolution_notes = ?, 
                    updated_at = ?, resolved_at = ?
                WHERE id = ?
            ''', (new_status, agent_id, resolution_notes, updated_at, updated_at, complaint_id))
            
            # Update agent's resolved count
            if agent_id:
                cursor.execute('''
                    UPDATE agents 
                    SET total_resolved = total_resolved + 1 
                    WHERE agent_id = ?
                ''', (agent_id,))
        
        else:
            cursor.execute('''
                UPDATE complaints
                SET status = ?, assigned_agent = ?, updated_at = ?
                WHERE id = ?
            ''', (new_status, agent_id, updated_at, complaint_id))
        
        # Add to history
        cursor.execute('''
            INSERT INTO complaint_history 
            (complaint_id, old_status, new_status, changed_by, change_reason, changed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (complaint_id, old_status, new_status, agent_id or 'system', 
              f'Status changed from {old_status} to {new_status}', updated_at))
        
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error updating complaint status: {e}")
        return False

def get_complaint_stats():
    """Get comprehensive complaint statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Basic counts
        cursor.execute('SELECT COUNT(*) FROM complaints')
        stats['total'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM complaints WHERE status = "Pending"')
        stats['pending'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM complaints WHERE status = "In Progress"')
        stats['in_progress'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM complaints WHERE status = "Resolved"')
        stats['resolved'] = cursor.fetchone()[0]
        
        # Urgency distribution
        cursor.execute('SELECT COUNT(*) FROM complaints WHERE urgency = "High"')
        stats['high_urgency'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM complaints WHERE urgency = "Medium"')
        stats['medium_urgency'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM complaints WHERE urgency = "Low"')
        stats['low_urgency'] = cursor.fetchone()[0]
        
        # Today's statistics
        today = datetime.now().date().isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM complaints 
            WHERE DATE(created_at) = ?
        ''', (today,))
        stats['submitted_today'] = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM complaints 
            WHERE DATE(resolved_at) = ?
        ''', (today,))
        stats['resolved_today'] = cursor.fetchone()[0]
        
        # Average resolution time (for resolved complaints)
        cursor.execute('''
            SELECT AVG(
                (JULIANDAY(resolved_at) - JULIANDAY(created_at)) * 24
            ) as avg_hours
            FROM complaints
            WHERE status = 'Resolved' AND resolved_at IS NOT NULL
        ''')
        result = cursor.fetchone()
        stats['avg_resolution_time'] = result[0] if result[0] else 0
        
        # Category distribution
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM complaints
            GROUP BY category
            ORDER BY count DESC
        ''')
        stats['category_distribution'] = cursor.fetchall()
        
        # Agent performance
        cursor.execute('''
            SELECT 
                a.name,
                a.agent_id,
                COUNT(c.id) as total_assigned,
                SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END) as resolved_count
            FROM agents a
            LEFT JOIN complaints c ON c.assigned_agent = a.agent_id
            WHERE a.status = 'active'
            GROUP BY a.id, a.name, a.agent_id
            ORDER BY resolved_count DESC
        ''')
        stats['agent_performance'] = cursor.fetchall()
        
        conn.close()
        return stats
    
    except Exception as e:
        print(f"Error getting complaint stats: {e}")
        return {
            'total': 0, 'pending': 0, 'in_progress': 0, 'resolved': 0,
            'high_urgency': 0, 'medium_urgency': 0, 'low_urgency': 0,
            'submitted_today': 0, 'resolved_today': 0, 'avg_resolution_time': 0,
            'category_distribution': [], 'agent_performance': []
        }

def get_complaint_by_id(complaint_id):
    """Get detailed complaint information by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, u.name as user_name, u.email as user_email,
                   a.name as agent_name
            FROM complaints c
            LEFT JOIN users u ON c.user_id = u.id
            LEFT JOIN agents a ON c.assigned_agent = a.agent_id
            WHERE c.id = ?
        ''', (complaint_id,))
        
        complaint = cursor.fetchone()
        
        if complaint:
            # Get complaint history
            cursor.execute('''
                SELECT old_status, new_status, changed_by, change_reason, changed_at
                FROM complaint_history
                WHERE complaint_id = ?
                ORDER BY changed_at ASC
            ''', (complaint_id,))
            
            history = cursor.fetchall()
            
            conn.close()
            return {
                'complaint': complaint,
                'history': history
            }
        
        conn.close()
        return None
    
    except Exception as e:
        print(f"Error getting complaint by ID: {e}")
        return None

def search_complaints(search_term, filters=None):
    """Search complaints with optional filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query
        query = '''
            SELECT id, user_id, category, description, address, landmark, 
                   image_path, urgency, status, created_at, updated_at
            FROM complaints
            WHERE (description LIKE ? OR address LIKE ? OR category LIKE ?)
        '''
        
        params = [f'%{search_term}%', f'%{search_term}%', f'%{search_term}%']
        
        # Add filters
        if filters:
            if filters.get('status'):
                query += ' AND status = ?'
                params.append(filters['status'])
            
            if filters.get('urgency'):
                query += ' AND urgency = ?'
                params.append(filters['urgency'])
            
            if filters.get('category'):
                query += ' AND category = ?'
                params.append(filters['category'])
            
            if filters.get('date_from'):
                query += ' AND DATE(created_at) >= ?'
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                query += ' AND DATE(created_at) <= ?'
                params.append(filters['date_to'])
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        complaints = cursor.fetchall()
        conn.close()
        
        return complaints
    
    except Exception as e:
        print(f"Error searching complaints: {e}")
        return []

def add_feedback(complaint_id, user_id, rating, comments):
    """Add citizen feedback for a resolved complaint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (complaint_id, user_id, rating, comments, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (complaint_id, user_id, rating, comments, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error adding feedback: {e}")
        return False

def get_complaint_feedback(complaint_id):
    """Get feedback for a specific complaint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.rating, f.comments, f.created_at, u.name
            FROM feedback f
            JOIN users u ON f.user_id = u.id
            WHERE f.complaint_id = ?
            ORDER BY f.created_at DESC
        ''', (complaint_id,))
        
        feedback = cursor.fetchall()
        conn.close()
        
        return feedback
    
    except Exception as e:
        print(f"Error getting feedback: {e}")
        return []

def cleanup_old_images():
    """Clean up orphaned image files"""
    try:
        # Get all image paths from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT image_path FROM complaints WHERE image_path IS NOT NULL')
        db_images = set(row[0] for row in cursor.fetchall() if row[0])
        conn.close()
        
        # Get all actual image files
        images_dir = "assets/uploaded_images"
        if os.path.exists(images_dir):
            actual_files = set()
            for filename in os.listdir(images_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    actual_files.add(os.path.join(images_dir, filename))
            
            # Find and delete orphaned files
            orphaned_files = actual_files - db_images
            deleted_count = 0
            
            for file_path in orphaned_files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
            
            return deleted_count
        
        return 0
    
    except Exception as e:
        print(f"Error cleaning up images: {e}")
        return 0

def export_complaints_to_csv(filename=None, filters=None):
    """Export complaints to CSV with optional filters"""
    try:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"complaints_export_{timestamp}.csv"
        
        conn = get_db_connection()
        
        # Build query with filters
        query = '''
            SELECT 
                c.id, c.category, c.description, c.address, c.landmark,
                c.urgency, c.user_priority, c.status, c.created_at, c.updated_at,
                c.resolved_at, u.name as user_name, u.email as user_email,
                a.name as agent_name, a.agent_id
            FROM complaints c
            LEFT JOIN users u ON c.user_id = u.id
            LEFT JOIN agents a ON c.assigned_agent = a.agent_id
        '''
        
        params = []
        
        if filters:
            where_conditions = []
            
            if filters.get('status'):
                where_conditions.append('c.status = ?')
                params.append(filters['status'])
            
            if filters.get('urgency'):
                where_conditions.append('c.urgency = ?')
                params.append(filters['urgency'])
            
            if filters.get('category'):
                where_conditions.append('c.category = ?')
                params.append(filters['category'])
            
            if filters.get('date_from'):
                where_conditions.append('DATE(c.created_at) >= ?')
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                where_conditions.append('DATE(c.created_at) <= ?')
                params.append(filters['date_to'])
            
            if where_conditions:
                query += ' WHERE ' + ' AND '.join(where_conditions)
        
        query += ' ORDER BY c.created_at DESC'
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        df.to_csv(filename, index=False)
        return filename
    
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None

def backup_database(backup_path=None):
    """Create a backup of the database"""
    try:
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"db/backup_complaints_{timestamp}.db"
        
        import shutil
        shutil.copy2(DATABASE_PATH, backup_path)
        return backup_path
    
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None

def get_dashboard_summary():
    """Get summary data for dashboard displays"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        summary = {}
        
        # Recent complaints (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM complaints 
            WHERE created_at >= ?
        ''', (week_ago,))
        summary['recent_complaints'] = cursor.fetchone()[0]
        
        # Urgent complaints needing attention
        cursor.execute('''
            SELECT COUNT(*) FROM complaints 
            WHERE urgency = 'High' AND status IN ('Pending', 'In Progress')
        ''')
        summary['urgent_pending'] = cursor.fetchone()[0]
        
        # Average response time for resolved complaints
        cursor.execute('''
            SELECT AVG(
                (JULIANDAY(updated_at) - JULIANDAY(created_at)) * 24
            ) as avg_response_hours
            FROM complaints
            WHERE status != 'Pending'
        ''')
        result = cursor.fetchone()
        summary['avg_response_time'] = result[0] if result[0] else 0
        
        # Most common complaint category
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM complaints
            GROUP BY category
            ORDER BY count DESC
            LIMIT 1
        ''')
        result = cursor.fetchone()
        summary['top_category'] = result[0] if result else 'None'
        
        conn.close()
        return summary
    
    except Exception as e:
        print(f"Error getting dashboard summary: {e}")
        return {
            'recent_complaints': 0,
            'urgent_pending': 0,
            'avg_response_time': 0,
            'top_category': 'None'
        }

def test_database_connection():
    """Test database connection and basic operations"""
    try:
        print("🧪 Testing database connection...")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('users', 'agents', 'complaints')
        """)
        tables = cursor.fetchall()
        print(f"✅ Found tables: {[table[0] for table in tables]}")
        
        # Test complaints table structure
        cursor.execute("PRAGMA table_info(complaints)")
        columns = cursor.fetchall()
        print(f"✅ Complaints table columns: {[col[1] for col in columns]}")
        
        # Test inserting a sample complaint (if user exists)
        cursor.execute("SELECT id FROM users LIMIT 1")
        user = cursor.fetchone()
        
        if user:
            user_id = user[0]
            test_complaint_id = add_complaint(
                user_id=user_id,
                category="Test Category",
                description="Test complaint for database verification",
                address="Test Address",
                urgency="Medium"
            )
            
            if test_complaint_id:
                print(f"✅ Test complaint created with ID: {test_complaint_id}")
                # Clean up test complaint
                cursor.execute("DELETE FROM complaints WHERE id = ?", (test_complaint_id,))
                conn.commit()
                print("✅ Test complaint cleaned up")
            else:
                print("❌ Failed to create test complaint")
        else:
            print("ℹ️ No users found for complaint test")
        
        conn.close()
        print("✅ Database test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

# Initialize database on import
if __name__ == "__main__":
    print("🗄️ Initializing CitiZen AI Database...")
    init_database()
    test_database_connection()
    print("✅ Database setup complete!")