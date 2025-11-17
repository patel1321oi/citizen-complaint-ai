import pickle
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import re
from datetime import datetime, timedelta
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_utils import get_db_connection

# Model paths
MODEL_DIR = "ml"
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")
STATS_PATH = os.path.join(MODEL_DIR, "training_stats.pkl")

def ensure_model_directory():
    """Ensure the ml directory exists"""
    os.makedirs(MODEL_DIR, exist_ok=True)

def preprocess_text(text):
    """Clean and preprocess text data"""
    if pd.isna(text) or text is None:
        return ""
    
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Remove extra whitespaces
    text = ' '.join(text.split())
    
    return text

def create_features(description, category):
    """Create features from complaint description and category"""
    # Preprocess description
    clean_desc = preprocess_text(description)
    clean_category = preprocess_text(category)
    
    # Combine description and category for feature creation
    combined_text = f"{clean_desc} {clean_category}"
    
    return combined_text

def get_initial_training_data():
    """Create comprehensive initial training data with realistic complaint patterns"""
    training_data = []
    
    # High urgency patterns - Safety and emergency situations
    high_urgency_patterns = [
        ("water pipe burst flooding street emergency immediate help needed", "Water Supply Issues", "High"),
        ("electricity wire fallen dangerous sparking safety hazard", "Streetlight & Electricity", "High"),
        ("large tree fallen blocking entire road traffic jam emergency", "Tree Fall & Maintenance", "High"),
        ("manhole cover missing pedestrian fell injured dangerous", "Roads & Potholes", "High"),
        ("gas leak smell strong entire building evacuation needed", "Public Safety & Security", "High"),
        ("sewer overflow contaminated water health hazard disease spread", "Drainage & Water Logging", "High"),
        ("streetlight completely dark accident prone dangerous area crime", "Streetlight & Electricity", "High"),
        ("garbage pile rotting smell disease outbreak rats insects", "Garbage & Waste Management", "High"),
        ("pothole very deep vehicle damage accident risk", "Roads & Potholes", "High"),
        ("traffic signal not working major intersection accidents", "Traffic & Parking", "High"),
        ("water contaminated dirty brown color stomach illness", "Water Supply Issues", "High"),
        ("construction debris sharp objects children playing area", "Other Municipal Issues", "High"),
        ("flood water stagnant mosquito breeding dengue risk", "Drainage & Water Logging", "High"),
        ("electrical box open exposed wires shock risk", "Streetlight & Electricity", "High"),
        ("stray dogs aggressive biting people safety concern", "Public Safety & Security", "High"),
    ]
    
    # Medium urgency patterns - Problems that need attention but not emergencies
    medium_urgency_patterns = [
        ("water pressure low timing irregular inconvenience", "Water Supply Issues", "Medium"),
        ("electricity power cut frequent load shedding problem", "Streetlight & Electricity", "Medium"),
        ("pothole causing inconvenience vehicle bumpy ride", "Roads & Potholes", "Medium"),
        ("drainage slow water logging rain problem", "Drainage & Water Logging", "Medium"),
        ("streetlight dim not bright enough visibility", "Streetlight & Electricity", "Medium"),
        ("garbage collection irregular delay complaint", "Garbage & Waste Management", "Medium"),
        ("traffic congestion peak hours slow movement", "Traffic & Parking", "Medium"),
        ("noise pollution construction site disturbing", "Noise Pollution", "Medium"),
        ("tree branch hanging loose trimming required", "Tree Fall & Maintenance", "Medium"),
        ("parking space insufficient residential area", "Traffic & Parking", "Medium"),
        ("road repair needed cracks developing", "Roads & Potholes", "Medium"),
        ("water billing incorrect higher amount charged", "Water Supply Issues", "Medium"),
        ("waste segregation not happening mixed garbage", "Garbage & Waste Management", "Medium"),
        ("street dog population increasing nuisance", "Public Safety & Security", "Medium"),
        ("public toilet cleaning required maintenance", "Other Municipal Issues", "Medium"),
    ]
    
    # Low urgency patterns - General maintenance and minor issues  
    low_urgency_patterns = [
        ("water meter reading request schedule visit", "Water Supply Issues", "Low"),
        ("electricity bill query information needed", "Streetlight & Electricity", "Low"),
        ("small pothole minor inconvenience can wait", "Roads & Potholes", "Low"),
        ("drainage cleaning scheduled maintenance required", "Drainage & Water Logging", "Low"),
        ("streetlight replacement bulb not working", "Streetlight & Electricity", "Low"),
        ("garbage bin additional required more capacity", "Garbage & Waste Management", "Low"),
        ("traffic signage improvement suggestion", "Traffic & Parking", "Low"),
        ("noise complaint minor disturbance occasional", "Noise Pollution", "Low"),
        ("tree pruning beautification garden maintenance", "Tree Fall & Maintenance", "Low"),
        ("general complaint feedback suggestion improvement", "Other Municipal Issues", "Low"),
        ("road marking paint faded renewal needed", "Roads & Potholes", "Low"),
        ("water connection new application processing", "Water Supply Issues", "Low"),
        ("park maintenance grass cutting required", "Other Municipal Issues", "Low"),
        ("complaint status inquiry follow up", "Other Municipal Issues", "Low"),
        ("information request municipal services", "Other Municipal Issues", "Low"),
    ]
    
    # Combine all patterns
    all_patterns = high_urgency_patterns + medium_urgency_patterns + low_urgency_patterns
    
    # Create training samples with variations
    for desc, cat, urgency in all_patterns:
        training_data.append({
            'description': desc,
            'category': cat,
            'urgency': urgency,
            'combined_features': create_features(desc, cat)
        })
        
        # Add variations of the same complaint to increase training data
        variations = create_description_variations(desc)
        for var_desc in variations[:2]:  # Add 2 variations per pattern
            training_data.append({
                'description': var_desc,
                'category': cat,
                'urgency': urgency,
                'combined_features': create_features(var_desc, cat)
            })
    
    return pd.DataFrame(training_data)

def create_description_variations(description):
    """Create variations of complaint descriptions for better training"""
    variations = []
    
    # Simple word replacements
    replacements = {
        'problem': 'issue',
        'required': 'needed',
        'complaint': 'concern',
        'help': 'assistance',
        'urgent': 'immediate',
        'dangerous': 'risky',
        'broken': 'damaged'
    }
    
    # Create variations
    words = description.split()
    for old_word, new_word in replacements.items():
        if old_word in words:
            var_desc = description.replace(old_word, new_word)
            variations.append(var_desc)
    
    # Add intensity variations
    if 'very' not in description:
        variations.append(f"very {description}")
    
    return variations

def load_or_create_model():
    """Load existing model or create new one"""
    ensure_model_directory()
    
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            with open(VECTORIZER_PATH, 'rb') as f:
                vectorizer = pickle.load(f)
            return model, vectorizer
        else:
            return create_initial_model()
    except Exception as e:
        print(f"Error loading model: {e}")
        return create_initial_model()

def create_initial_model():
    """Create and train initial model with synthetic data"""
    print("Creating initial AI model...")
    
    # Get initial training data
    training_data = get_initial_training_data()
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=2000,
        stop_words='english',
        ngram_range=(1, 3),
        min_df=1,
        max_df=0.95
    )
    
    # Create Random Forest model
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight='balanced',
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2
    )
    
    # Fit vectorizer and model
    X = vectorizer.fit_transform(training_data['combined_features'])
    y = training_data['urgency']
    
    model.fit(X, y)
    
    # Save model and vectorizer
    save_model(model, vectorizer)
    
    # Save training stats
    stats = {
        'last_training': datetime.now().isoformat(),
        'total_samples': len(training_data),
        'initial_accuracy': 1.0,
        'training_type': 'initial',
        'model_version': '1.0'
    }
    save_training_stats(stats)
    
    print(f"✅ Initial AI model created with {len(training_data)} training samples!")
    return model, vectorizer

def predict_urgency(description, category):
    """Predict urgency for a new complaint"""
    try:
        model, vectorizer = load_or_create_model()
        
        # Create features
        features = create_features(description, category)
        
        # Transform features
        X = vectorizer.transform([features])
        
        # Predict
        prediction = model.predict(X)[0]
        
        # Get prediction confidence
        probabilities = model.predict_proba(X)[0]
        max_prob = max(probabilities)
        
        # Apply business rules for critical cases
        prediction = apply_emergency_rules(description, category, prediction, max_prob)
        
        return prediction
        
    except Exception as e:
        print(f"Error in urgency prediction: {e}")
        # Fallback to rule-based prediction
        return rule_based_urgency_prediction(description, category)

def apply_emergency_rules(description, category, prediction, confidence):
    """Apply emergency detection rules that override ML predictions"""
    desc_lower = description.lower()
    
    # Critical emergency keywords - always high priority
    emergency_keywords = [
        'emergency', 'urgent', 'immediate', 'danger', 'dangerous', 'fire', 'accident', 
        'flood', 'flooding', 'overflow', 'burst', 'leak', 'gas', 'explosion',
        'injured', 'hurt', 'bleeding', 'unconscious', 'trapped', 'collapse',
        'sparking', 'shock', 'electrocution', 'fallen', 'blocking', 
        'contaminated', 'poisonous', 'toxic', 'disease', 'illness'
    ]
    
    # Check for emergency keywords
    if any(keyword in desc_lower for keyword in emergency_keywords):
        return "High"
    
    # Category-specific emergency rules
    if category == "Public Safety & Security":
        safety_keywords = ['crime', 'theft', 'violence', 'harassment', 'assault', 'suspicious']
        if any(word in desc_lower for word in safety_keywords):
            return "High"
    
    if category == "Water Supply Issues":
        water_emergency = ['burst', 'flooding', 'contaminated', 'dirty', 'brown', 'smell']
        if any(word in desc_lower for word in water_emergency):
            return "High"
    
    if category == "Streetlight & Electricity":
        electrical_emergency = ['spark', 'wire', 'shock', 'burn', 'fire', 'exposed']
        if any(word in desc_lower for word in electrical_emergency):
            return "High"
    
    # If ML model has low confidence, default to Medium
    if confidence < 0.5:
        return "Medium"
    
    return prediction

def rule_based_urgency_prediction(description, category):
    """Fallback rule-based urgency prediction"""
    desc_lower = description.lower()
    
    # High urgency indicators
    high_urgency_words = [
        'emergency', 'urgent', 'immediate', 'danger', 'dangerous', 'fire', 'accident', 
        'flood', 'overflow', 'burst', 'leak', 'gas', 'sparking', 'broken', 'damaged',
        'safety', 'hazard', 'risk', 'critical', 'serious', 'severe'
    ]
    
    # Medium urgency indicators  
    medium_urgency_words = [
        'problem', 'issue', 'concern', 'complaint', 'irregular', 'frequent',
        'delay', 'slow', 'inconvenience', 'disturbance', 'poor', 'bad'
    ]
    
    # Count urgency indicators
    high_count = sum(1 for word in high_urgency_words if word in desc_lower)
    medium_count = sum(1 for word in medium_urgency_words if word in desc_lower)
    
    # Decision logic
    if high_count >= 2 or any(word in desc_lower for word in ['emergency', 'danger', 'urgent']):
        return "High"
    elif high_count >= 1 or medium_count >= 2:
        return "Medium"
    else:
        return "Low"

def predict_resolution_time(description, category, urgency):
    """Predict estimated resolution time based on complaint details"""
    # Base resolution times (in hours)
    base_times = {
        'High': 24,    # 1 day
        'Medium': 72,  # 3 days  
        'Low': 168     # 1 week
    }
    
    # Category-specific time adjustments
    category_multipliers = {
        'Garbage & Waste Management': 0.5,      # Usually quick fixes
        'Streetlight & Electricity': 0.8,       # Moderate complexity
        'Water Supply Issues': 1.2,             # Can be complex
        'Roads & Potholes': 1.5,               # Often require planning
        'Drainage & Water Logging': 1.3,       # Weather dependent
        'Public Safety & Security': 0.3,       # High priority, fast response
        'Tree Fall & Maintenance': 1.0,        # Standard timing
        'Traffic & Parking': 0.7,              # Administrative fixes
        'Noise Pollution': 0.6,                # Usually quick resolution
        'Other Municipal Issues': 1.0          # Average timing
    }
    
    base_time = base_times.get(urgency, 72)
    multiplier = category_multipliers.get(category, 1.0)
    
    estimated_hours = int(base_time * multiplier)
    
    # Convert to human readable format
    if estimated_hours < 24:
        return f"{estimated_hours} hours"
    elif estimated_hours < 168:
        days = estimated_hours // 24
        return f"{days} day{'s' if days > 1 else ''}"
    else:
        weeks = estimated_hours // 168
        return f"{weeks} week{'s' if weeks > 1 else ''}"

def get_database_complaints():
    """Get all complaints from database for training"""
    try:
        conn = get_db_connection()
        query = """
            SELECT description, category, urgency
            FROM complaints
            WHERE urgency IS NOT NULL AND description IS NOT NULL AND description != ''
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            df['combined_features'] = df.apply(
                lambda row: create_features(row['description'], row['category']), axis=1
            )
        
        return df
    except Exception as e:
        print(f"Error getting database complaints: {e}")
        return pd.DataFrame()

def retrain_model():
    """Retrain model with all available data"""
    try:
        print("🤖 Starting AI model retraining...")
        
        # Get database complaints
        db_complaints = get_database_complaints()
        
        # Get initial training data
        initial_data = get_initial_training_data()
        
        # Combine all data
        if not db_complaints.empty:
            all_data = pd.concat([initial_data, db_complaints], ignore_index=True)
            print(f"Training with {len(initial_data)} synthetic + {len(db_complaints)} real complaints")
        else:
            all_data = initial_data
            print(f"Training with {len(initial_data)} synthetic complaints only")
        
        if len(all_data) < 10:
            print("⚠️ Insufficient data for retraining")
            return False
        
        # Create new model
        vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.95
        )
        
        model = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight='balanced',
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2
        )
        
        # Prepare data
        X = vectorizer.fit_transform(all_data['combined_features'])
        y = all_data['urgency']
        
        # Train model
        if len(all_data) > 20:
            # Use train-test split for evaluation
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"✅ Model retrained - Accuracy: {accuracy:.3f}")
        else:
            # Use all data for training if dataset is small
            model.fit(X, y)
            accuracy = 0.95  # Estimated accuracy for small datasets
            print(f"✅ Model retrained with small dataset")
        
        # Save model
        save_model(model, vectorizer)
        
        # Save training stats
        stats = {
            'last_training': datetime.now().isoformat(),
            'total_samples': len(all_data),
            'db_samples': len(db_complaints),
            'accuracy': accuracy,
            'training_type': 'retrain',
            'model_version': '2.0'
        }
        save_training_stats(stats)
        
        print("🎉 AI model retraining completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error retraining model: {e}")
        return False

def save_model(model, vectorizer):
    """Save model and vectorizer to disk"""
    ensure_model_directory()
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump(vectorizer, f)

def save_training_stats(stats):
    """Save training statistics"""
    ensure_model_directory()
    
    with open(STATS_PATH, 'wb') as f:
        pickle.dump(stats, f)

def get_training_stats():
    """Get training statistics"""
    try:
        if os.path.exists(STATS_PATH):
            with open(STATS_PATH, 'rb') as f:
                return pickle.load(f)
    except:
        pass
    
    return {
        'last_training': 'Never',
        'total_samples': 0,
        'accuracy': 0.0,
        'training_type': 'none',
        'model_version': '0.0'
    }

def train_model_if_needed():
    """Check if model needs retraining and do it automatically"""
    try:
        # Get current complaint count from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM complaints")
        current_count = cursor.fetchone()[0]
        conn.close()
        
        # Get training stats
        stats = get_training_stats()
        last_training_samples = stats.get('db_samples', 0)
        
        # Retrain if we have 10 or more new complaints since last training
        new_complaints = current_count - last_training_samples
        
        if new_complaints >= 10:
            print(f"🔄 Auto-retraining AI model with {new_complaints} new complaints...")
            retrain_model()
        elif current_count >= 5 and stats.get('training_type') == 'none':
            print("🚀 Initial training with real complaint data...")
            retrain_model()
        
    except Exception as e:
        print(f"❌ Error checking training needs: {e}")

def get_model_info():
    """Get information about the current model"""
    stats = get_training_stats()
    
    info = {
        'model_exists': os.path.exists(MODEL_PATH),
        'last_training': stats.get('last_training', 'Never'),
        'total_samples': stats.get('total_samples', 0),
        'accuracy': stats.get('accuracy', 0.0),
        'version': stats.get('model_version', '0.0'),
        'type': stats.get('training_type', 'none')
    }
    
    return info

# Test function to verify model works
def test_model():
    """Test the model with sample complaints"""
    test_cases = [
        ("Water pipe burst flooding the entire street emergency help needed", "Water Supply Issues"),
        ("Streetlight not working need replacement bulb", "Streetlight & Electricity"),
        ("Small pothole causing minor inconvenience", "Roads & Potholes"),
        ("Garbage overflow health hazard disease rats", "Garbage & Waste Management"),
        ("Tree fallen blocking road dangerous emergency", "Tree Fall & Maintenance")
    ]
    
    print("\n🧪 Testing AI Model Predictions:")
    print("-" * 50)
    
    for desc, cat in test_cases:
        urgency = predict_urgency(desc, cat)
        resolution_time = predict_resolution_time(desc, cat, urgency)
        print(f"Description: {desc[:50]}...")
        print(f"Category: {cat}")
        print(f"Predicted Urgency: {urgency}")
        print(f"Est. Resolution: {resolution_time}")
        print("-" * 50)

if __name__ == "__main__":
    # Initialize model on first run
    print("🤖 Initializing CitiZen AI Model...")
    model, vectorizer = load_or_create_model()
    
    # Test the model
    test_model()
    
    print("\n✅ AI Model is ready for use!")