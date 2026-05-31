from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATABASE = 'data/app.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/api/health', methods=['GET'])
def health():
    """Check if backend is running"""
    return jsonify({"status": "Backend is running!", "timestamp": datetime.now().isoformat()})


@app.route('/api/sessions/create', methods=['POST'])
def create_session():
    """Create a new trip planning session"""
    try:
        data = request.json
        session_id = str(uuid.uuid4())[:8]  
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO sessions (id, created_at, trip_date, trip_time, status)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            session_id,
            datetime.now(),
            data.get('trip_date', ''),
            data.get('trip_time', ''),
            'active'
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "shareable_link": f"https://groupvibe.vercel.app/join/{session_id}",
            "message": f"Session created! Share this link with friends."
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details and member progress"""
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
                "email": member['email'],
                "submitted": bool(member['submitted']),
                "created_at": member['created_at']
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
    """Submit member preferences"""
    try:
        data = request.json
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Session not found"}), 404
        
        cursor.execute('''
        INSERT OR REPLACE INTO session_members 
        (session_id, name, email, budget_min, budget_max, vibe_score, 
         cuisines, activity_types, dietary_restrictions, submitted, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            data.get('name'),
            data.get('email'),
            data.get('budget_min'),
            data.get('budget_max'),
            data.get('vibe_score'),
            ','.join(data.get('cuisines', [])),
            ','.join(data.get('activity_types', [])),
            ','.join(data.get('dietary_restrictions', [])),
            1,  
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Preferences submitted successfully!"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/places', methods=['GET'])
def get_all_places():
    """Get all places from database"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM places LIMIT 50')
        places = cursor.fetchall()
        conn.close()
        
        places_list = [dict(place) for place in places]
        
        return jsonify({
            "success": True,
            "places": places_list,
            "count": len(places_list)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    print("🚀 GroupVibe Backend Starting...")
    print("📍 API Base URL: http://localhost:5000")
    print("📊 Endpoints:")
    print("   - GET  /api/health")
    print("   - POST /api/sessions/create")
    print("   - GET  /api/sessions/<session_id>")
    print("   - POST /api/sessions/<session_id>/submit-preferences")
    print("   - GET  /api/places")
    app.run(debug=True, port=5000)