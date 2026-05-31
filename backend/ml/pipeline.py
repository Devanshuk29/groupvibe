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

def generate_recommendations(session_members, top_n=5):
    """
    Main pipeline: takes session members and returns top N recommendations
    
    Flow:
    1. HDBSCAN → cluster friends by preferences
    2. Word2Vec → embed places
    3. Neural Net → score each place
    4. Rank → return top N
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
    
    scored_places = []
    
    for place in places:
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
            "price_range": place["price_range"],
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
            "avg_budget": round(avg_budget, 0)
        }
    }

if __name__ == "__main__":
    test_members = [
        {"id": 1, "budget": 2000, "vibe_score": 4, "preferred_categories": ["dining", "nightlife"], "dietary": ["vegetarian"]},
        {"id": 2, "budget": 1800, "vibe_score": 5, "preferred_categories": ["dining", "adventure"], "dietary": []},
        {"id": 3, "budget": 1500, "vibe_score": 3, "preferred_categories": ["dining", "shopping"], "dietary": ["vegetarian"]},
        {"id": 4, "budget": 2200, "vibe_score": 4, "preferred_categories": ["nightlife", "dining"], "dietary": []},
        {"id": 5, "budget": 1900, "vibe_score": 4, "preferred_categories": ["adventure", "dining"], "dietary": []}
    ]
    
    result = generate_recommendations(test_members)
    
    print(f"\n📊 GROUP ANALYSIS:")
    print(f"   Compatibility: {result['group_analysis']['compatibility_score']}")
    print(f"   Clusters: {result['group_analysis']['num_clusters']}")
    print(f"   Top Categories: {result['group_analysis']['top_categories']}")
    print(f"   Avg Budget: ₹{result['group_analysis']['avg_budget']}")
    
    print(f"\n🏆 TOP {len(result['recommendations'])} RECOMMENDATIONS:")
    for rec in result["recommendations"]:
        print(f"   {rec['rank']}. {rec['name']} (Score: {rec['score']}) - {rec['category']}")