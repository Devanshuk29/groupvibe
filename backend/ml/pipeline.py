import json
import sqlite3
import numpy as np
import torch
import os
from gensim.models import Word2Vec
from clustering import cluster_friends, get_group_compatibility, extract_features
from embeddings import get_place_embedding, get_similarity
from neural_net import PlaceScoringNet, score_place, build_feature_vector

def load_models():
    """Load all trained models"""
    models = {}
    
    if os.path.exists("models/word2vec.model"):
        models["word2vec"] = Word2Vec.load("models/word2vec.model")
        print("✅ Word2Vec loaded")
    
    if os.path.exists("models/neural_net.pth"):
        nn_model = PlaceScoringNet(input_size=12)
        nn_model.load_state_dict(torch.load("models/neural_net.pth", weights_only=True))
        nn_model.eval()
        models["neural_net"] = nn_model
        print("✅ Neural Network loaded")
    
    return models

def get_places_from_db():
    """Load all places from database"""
    conn = sqlite3.connect("data/app.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM places")
    places = [dict(p) for p in cursor.fetchall()]
    conn.close()
    return places

def is_place_open(place, available_date, available_time):
    """
    Check if a place is open on the requested date and time
    Returns True if open, False if closed
    """
    if not available_date and not available_time:
        return True  
    
    time_slots = {
        'morning': (9, 12),
        'afternoon': (12, 17),
        'evening': (17, 21),
        'night': (21, 24)
    }
    
    try:
        hours = json.loads(place['hours']) if isinstance(place['hours'], str) else place['hours']
        
        if not hours:
            return True
        
        if available_date:
            from datetime import datetime as dt
            date_obj = dt.strptime(available_date, '%Y-%m-%d')
            day_name = date_obj.strftime('%A').lower()
        else:
            day_name = None
        
        if day_name and day_name in hours:
            place_hours = hours[day_name]
            
            if place_hours == 'CLOSED':
                return False
            
            if available_time and available_time.lower() in time_slots:
                slot_start, slot_end = time_slots[available_time.lower()]
                
                try:
                    open_time, close_time = place_hours.split('-')
                    open_hour = int(open_time.split(':')[0])
                    close_hour = int(close_time.split(':')[0])
                    
                    if close_hour < open_hour:
                        close_hour += 24
                    
                    if slot_end <= open_hour or slot_start >= close_hour:
                        return False
                        
                except:
                    return True  
        
        return True
        
    except Exception as e:
        return True  

def generate_recommendations(session_members, top_n=5):
    """
    Main pipeline: takes session members and returns top N recommendations
    
    Flow:
    1. HDBSCAN → cluster friends by preferences
    2. Word2Vec → embed places
    3. Neural Net → score each place
    4. Filter by availability
    5. Rank → return top N
    """
    print(f"\n🚀 Generating recommendations for {len(session_members)} members...")
    
    models = load_models()
    places = get_places_from_db()
    
    clustering_result = cluster_friends(session_members)
    compatibility_score = get_group_compatibility(session_members)
    print(f"✅ Clusters found: {clustering_result['num_clusters']}")
    print(f"✅ Compatibility score: {compatibility_score}")
    
    all_categories = []
    total_budget = []
    
    for member in session_members:
        all_categories.extend(member.get("preferred_categories", []))
        total_budget.append(member.get("budget", 1000))
    
    from collections import Counter
    category_counts = Counter(all_categories)
    top_categories = [cat for cat, _ in category_counts.most_common(3)]
    avg_budget = np.mean(total_budget)
    
    group_preferences = {
        "preferred_categories": top_categories,
        "avg_budget": avg_budget
    }
    
    print(f"✅ Group top categories: {top_categories}")
    print(f"✅ Group avg budget: ₹{avg_budget:.0f}")

    available_dates = [m.get('available_date', '') for m in session_members if m.get('available_date')]
    available_times = [m.get('available_time', '') for m in session_members if m.get('available_time')]

    common_date = Counter(available_dates).most_common(1)[0][0] if available_dates else ''
    common_time = Counter(available_times).most_common(1)[0][0] if available_times else ''

    print(f"✅ Filtering for date: {common_date or 'any'}, time: {common_time or 'any'}")

    scored_places = []
    filtered_count = 0

    for place in places:
        if not is_place_open(place, common_date, common_time):
            filtered_count += 1
            print(f"❌ {place['name']} filtered out (closed at requested time)")
            continue

        nn_score = score_place(models["neural_net"], place, group_preferences)
        
        w2v_bonus = 0.0
        if "word2vec" in models:
            place_category = place.get("category", "")
            for cat in top_categories:
                if cat in models["word2vec"].wv and place_category in models["word2vec"].wv:
                    similarity = models["word2vec"].wv.similarity(cat, place_category)
                    w2v_bonus += max(0, similarity) * 0.1
        
        final_score = (nn_score * 0.7) + (w2v_bonus * 0.3)
        final_score = round(float(min(1.0, final_score)), 4)
        
        scored_places.append({
            "place": place,
            "score": final_score,
            "nn_score": nn_score,
            "w2v_bonus": round(w2v_bonus, 4)
        })

    print(f"✅ {filtered_count} places filtered out, {len(scored_places)} places scored")
    
    scored_places.sort(key=lambda x: x["score"], reverse=True)
    top_places = scored_places[:top_n]
    
    recommendations = []
    for rank, item in enumerate(top_places, 1):
        place = item["place"]
        recommendations.append({
            "rank": rank,
            "place_id": place["id"],
            "name": place["name"],
            "type": place["type"],
            "category": place["category"],
            "score": float(item["score"]),
            "address": place["address"],
            "google_maps_link": place["google_maps_link"],
            "rating": float(place["rating"]) if place["rating"] else 0.0,
            "review_count": place["review_count"],
            "price_range": place["price_range"],
            "group_friendly": bool(place["group_friendly"]),
            "parking": bool(place["parking"]),
            "food_inside": bool(place["food_inside"]),
            "best_season": place["best_season"],
            "duration_hours": place["duration_hours"],
            "hours": place["hours"],
            "why_recommended": f"Matches group's top preferences: {', '.join(top_categories)}"
        })
    
    return {
        "success": True,
        "recommendations": recommendations,
        "group_analysis": {
            "total_members": len(session_members),
            "compatibility_score": compatibility_score,
            "num_clusters": clustering_result["num_clusters"],
            "outliers": clustering_result["outliers"],
            "top_categories": top_categories,
            "avg_budget": round(avg_budget, 0),
            "filtered_places": filtered_count,
            "common_date": common_date,
            "common_time": common_time
        }
    }

if __name__ == "__main__":
    test_members = [
        {"id": 1, "budget": 2000, "vibe_score": 4, "preferred_categories": ["dining", "nightlife"], "dietary": ["vegetarian"], "available_date": "2026-06-07", "available_time": "evening"},
        {"id": 2, "budget": 1800, "vibe_score": 5, "preferred_categories": ["dining", "adventure"], "dietary": [], "available_date": "2026-06-07", "available_time": "evening"},
        {"id": 3, "budget": 1500, "vibe_score": 3, "preferred_categories": ["dining", "shopping"], "dietary": ["vegetarian"], "available_date": "2026-06-07", "available_time": "evening"},
        {"id": 4, "budget": 2200, "vibe_score": 4, "preferred_categories": ["nightlife", "dining"], "dietary": [], "available_date": "2026-06-07", "available_time": "evening"},
        {"id": 5, "budget": 1900, "vibe_score": 4, "preferred_categories": ["adventure", "dining"], "dietary": [], "available_date": "2026-06-07", "available_time": "evening"}
    ]
    
    result = generate_recommendations(test_members)
    
    print(f"\n📊 GROUP ANALYSIS:")
    print(f"   Compatibility: {result['group_analysis']['compatibility_score']}")
    print(f"   Clusters: {result['group_analysis']['num_clusters']}")
    print(f"   Top Categories: {result['group_analysis']['top_categories']}")
    print(f"   Avg Budget: ₹{result['group_analysis']['avg_budget']}")
    print(f"   Filtered Places: {result['group_analysis']['filtered_places']}")
    print(f"   Date: {result['group_analysis']['common_date']}")
    print(f"   Time: {result['group_analysis']['common_time']}")
    
    print(f"\n🏆 TOP {len(result['recommendations'])} RECOMMENDATIONS:")
    for rec in result["recommendations"]:
        print(f"   {rec['rank']}. {rec['name']} (Score: {rec['score']}) - {rec['category']}")