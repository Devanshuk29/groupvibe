import sqlite3
import json
from datetime import datetime
import os

# Create database
conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMP,
  trip_date TEXT,
  trip_time TEXT,
  status TEXT DEFAULT 'active'
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS session_members (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT,
  name TEXT,
  email TEXT,
  budget_min INTEGER,
  budget_max INTEGER,
  vibe_score INTEGER,
  cuisines TEXT,
  activity_types TEXT,
  dietary_restrictions TEXT,
  submitted BOOLEAN DEFAULT 0,
  created_at TIMESTAMP,
  FOREIGN KEY(session_id) REFERENCES sessions(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS places (
  id INTEGER PRIMARY KEY,
  name TEXT,
  type TEXT,
  category TEXT,
  latitude REAL,
  longitude REAL,
  google_maps_link TEXT,
  address TEXT,
  area TEXT,
  price_range TEXT,
  rating REAL,
  review_count INTEGER,
  hours TEXT,
  activities TEXT,
  group_friendly BOOLEAN,
  parking BOOLEAN,
  food_inside BOOLEAN,
  best_season TEXT,
  duration_hours INTEGER,
  age_restriction TEXT,
  created_at TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS recommendations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT,
  place_id INTEGER,
  score REAL,
  rank INTEGER,
  created_at TIMESTAMP,
  FOREIGN KEY(session_id) REFERENCES sessions(id),
  FOREIGN KEY(place_id) REFERENCES places(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS votes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT,
  member_id INTEGER,
  place_id INTEGER,
  vote_type TEXT,
  created_at TIMESTAMP,
  FOREIGN KEY(session_id) REFERENCES sessions(id),
  FOREIGN KEY(member_id) REFERENCES session_members(id),
  FOREIGN KEY(place_id) REFERENCES places(id)
)
''')

# Load places from JSON
with open('data/places.json') as f:
  data = json.load(f)
  for place in data['places']:

    # Handle both restaurant_specific and activity_specific
    spec = place.get('activity_specific', place.get('restaurant_specific', {}))

    cursor.execute('''
    INSERT OR REPLACE INTO places VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
      place['id'],
      place['name'],
      place['type'],
      place['category'],
      place['location']['latitude'],
      place['location']['longitude'],
      place['location']['google_maps_link'],
      place['location']['address'],
      place['location']['area'],
      place['details']['price_range'],
      place['details']['rating'],
      place['details']['review_count'],
      json.dumps(place['details']['hours']),
      json.dumps(spec.get('activities', [])),
      spec.get('group_friendly', True),
      spec.get('parking', False),
      spec.get('food_inside', False),
      spec.get('best_season', 'all_year'),
      spec.get('duration_hours', 2),
      spec.get('age_restriction', 'all_ages'),
      datetime.now()
    ))

conn.commit()
conn.close()
print("✅ Database initialized successfully!")
print("✅ Tables created: sessions, session_members, places, recommendations, votes")
print(f"✅ Loaded {len(data['places'])} places from places.json")