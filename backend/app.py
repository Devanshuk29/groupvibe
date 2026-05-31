from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import uuid
from datetime import datetime
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'ml'))

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False 
CORS(app)

DATABASE = 'data/app.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

print("🔄 Loading ML models...")
try:
    from ml.pipeline import load_models
    ML_MODELS = load_models()
    print("✅ ML models loaded successfully!")
except Exception as e:
    print(f"⚠️ ML models not loaded: {e}")
    ML_MODELS = {}


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "Backend is running!",
        "timestamp": datetime.now().isoformat(),
        "ml_models_loaded": len(ML_MODELS) > 0
    })


@app.route('/api/sessions/create', methods=['POST'])
def create_session():
    try:
        data = request.json or {}
        session_id = str(uuid.uuid4())[:8].upper()
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO sessions (id, created_at, trip_date, trip_time, status)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            session_id,
            datetime.now().isoformat(),
            data.get('trip_date', ''),
            data.get('trip_time', ''),
            'active'
        ))
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "shareable_link": f"http://localhost:3000/join/{session_id}",
            "message": "Session created! Share this link with friends."
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        session = cursor.fetchone()
        
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        cursor.execute('SELECT * FROM session_members WHERE session_id = ?', (session_id,))
        members = cursor.fetchall()
        conn.close()
        
        members_list = []
        for member in members:
            members_list.append({
                "id": member['id'],
                "name": member['name'],
                "submitted": bool(member['submitted'])
            })
        
        return jsonify({
            "success": True,
            "session_id": session['id'],
            "trip_date": session['trip_date'],
            "trip_time": session['trip_time'],
            "status": session['status'],
            "members": members_list,
            "total_members": len(members_list),
            "submitted_count": sum(1 for m in members_list if m['submitted'])
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<session_id>/submit-preferences', methods=['POST'])
def submit_preferences(session_id):
    try:
        data = request.json
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Session not found"}), 404
        
        cursor.execute('''
        INSERT INTO session_members 
        (session_id, name, email, budget_min, budget_max, vibe_score,
         cuisines, activity_types, dietary_restrictions, submitted, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            data.get('name'),
            data.get('email', ''),
            data.get('budget_min', 0),
            data.get('budget_max', 5000),
            data.get('vibe_score', 3),
            ','.join(data.get('cuisines', [])),
            ','.join(data.get('activity_types', [])),
            ','.join(data.get('dietary_restrictions', [])),
            1,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Preferences submitted for {data.get('name')}!"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/places', methods=['GET'])
def get_all_places():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM places LIMIT 50')
        places = cursor.fetchall()
        conn.close()
        
        return jsonify({
            "success": True,
            "places": [dict(p) for p in places],
            "count": len(places)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sessions/<session_id>/generate-recommendations', methods=['POST'])
def generate_recommendations(session_id):
    """
    Main endpoint - generates ML recommendations for a session
    Flow:
    1. Get session from database
    2. Get all members preferences from database
    3. Convert to ML format
    4. Run ML pipeline
    5. Save results to database
    6. Return top 5 recommendations
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        session = cursor.fetchone()
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        cursor.execute('''
            SELECT * FROM session_members 
            WHERE session_id = ? AND submitted = 1
        ''', (session_id,))
        members = cursor.fetchall()
        
        if len(members) == 0:
            return jsonify({
                "error": "No preferences submitted yet!",
                "hint": "Ask friends to submit their preferences first"
            }), 400
        
        session_members = []
        for member in members:
            activity_types = member['activity_types'].split(',') if member['activity_types'] else []
            activity_types = [a.strip() for a in activity_types if a.strip()]
            
            category_mapping = {
                "dining": "dining",
                "nightlife": "nightlife",
                "adventure": "adventure",
                "sports": "sports",
                "nature": "nature",
                "shopping": "shopping"
            }
            
            preferred_categories = [
                category_mapping.get(a, a) for a in activity_types
            ]
            
            budget = (member['budget_min'] + member['budget_max']) / 2
            
            session_members.append({
                "id": member['id'],
                "budget": budget,
                "vibe_score": member['vibe_score'],
                "preferred_categories": preferred_categories,
                "dietary": member['dietary_restrictions'].split(',') if member['dietary_restrictions'] else []
            })
        
        print(f"✅ Processing {len(session_members)} members for session {session_id}")
        
        from ml.pipeline import generate_recommendations as ml_generate
        ml_result = ml_generate(session_members, top_n=5)
        
        cursor.execute('DELETE FROM recommendations WHERE session_id = ?', (session_id,))
        for rec in ml_result['recommendations']:
            cursor.execute('''
            INSERT INTO recommendations (session_id, place_id, score, rank, created_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                session_id,
                rec['place_id'],
                rec['score'],
                rec['rank'],
                datetime.now().isoformat()
            ))
        
        cursor.execute('''
            UPDATE sessions SET status = 'recommendations_generated' 
            WHERE id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "total_members": len(session_members),
            "group_analysis": ml_result['group_analysis'],
            "recommendations": ml_result['recommendations']
        }), 200
        
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    print("\n🚀 GroupVibe Backend Starting...")
    print("📍 API Base URL: http://localhost:5000")
    print("📊 Endpoints:")
    print("   - GET  /api/health")
    print("   - POST /api/sessions/create")
    print("   - GET  /api/sessions/<session_id>")
    print("   - POST /api/sessions/<session_id>/submit-preferences")
    print("   - POST /api/sessions/<session_id>/generate-recommendations")
    print("   - GET  /api/places\n")
    app.run(debug=True, port=5000)