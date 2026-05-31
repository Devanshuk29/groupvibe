import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml'))

from ml.embeddings import train_embeddings
from ml.neural_net import train_model, PlaceScoringNet
import sqlite3
import torch
import json

def train_all_models():
    print("🚀 Training all GroupVibe ML models...\n")
    
    conn = sqlite3.connect("data/app.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM places")
    places = [dict(p) for p in cursor.fetchall()]
    conn.close()
    
    print(f"✅ Loaded {len(places)} places from database\n")
    
    print("📝 Training Word2Vec embeddings...")
    w2v_model = train_embeddings(places)
    os.makedirs("models", exist_ok=True)
    w2v_model.save("models/word2vec.model")
    print("✅ Word2Vec saved to models/word2vec.model\n")
    
    print("🧠 Training Neural Network...")
    nn_model = train_model(places)
    torch.save(nn_model.state_dict(), "models/neural_net.pth")
    print("✅ Neural Network saved to models/neural_net.pth\n")
    
   
    print("🔍 Testing HDBSCAN clustering...")
    from ml.clustering import cluster_friends
    with open("data/training_data.json") as f:
        training_data = json.load(f)
    result = cluster_friends(training_data["friends"])
    print(f"✅ HDBSCAN working! Found {result['num_clusters']} clusters")
    print(f"   Outliers: {result['outliers']}\n")
    
    print("🎉 All models trained and saved successfully!")
    print("\nModels saved:")
    print("   - models/word2vec.model")
    print("   - models/neural_net.pth")
    print("   - HDBSCAN: runs dynamically (no save needed)")

if __name__ == "__main__":
    train_all_models()