import json
import numpy as np
from gensim.models import Word2Vec
import os

def prepare_place_sentences(places):
    """Convert place data into sentences for Word2Vec training"""
    sentences = []
    for place in places:
        sentence = []
        sentence.append(place["type"])
        sentence.append(place["category"])
        
        activities = json.loads(place["activities"]) if isinstance(place["activities"], str) else place["activities"]
        sentence.extend(activities)
        
        sentence.append(place.get("best_season", "all_year"))
        sentence.append(place.get("area", "").lower().replace(" ", "_"))
        
        sentences.append(sentence)
    
    return sentences

def train_embeddings(places, vector_size=64, window=3, min_count=1):
    """
    Train Word2Vec embeddings on place data
    Input: list of places
    Output: trained Word2Vec model
    """
    sentences = prepare_place_sentences(places)
    
    print(f"Training on {len(sentences)} places...")
    print(f"Sample sentences: {sentences[:2]}")
    
    model = Word2Vec(
        sentences=sentences,
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        workers=4,
        epochs=100
    )
    
    return model

def get_place_embedding(model, place):
    """Get embedding vector for a single place"""
    sentence = []
    sentence.append(place["type"])
    sentence.append(place["category"])
    
    activities = json.loads(place["activities"]) if isinstance(place["activities"], str) else place["activities"]
    sentence.extend(activities)
    sentence.append(place.get("best_season", "all_year"))
    
    vectors = []
    for word in sentence:
        if word in model.wv:
            vectors.append(model.wv[word])
    
    if vectors:
        return np.mean(vectors, axis=0)
    else:
        return np.zeros(model.vector_size)

def get_similarity(model, place1, place2):
    """Get similarity score between two places (0-1)"""
    emb1 = get_place_embedding(model, place1)
    emb2 = get_place_embedding(model, place2)
    
    dot_product = np.dot(emb1, emb2)
    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = dot_product / (norm1 * norm2)
    return round(float(similarity), 4)

if __name__ == "__main__":
    import sqlite3
    
    conn = sqlite3.connect("data/app.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM places")
    places = [dict(p) for p in cursor.fetchall()]
    conn.close()
    
    print(f"✅ Loaded {len(places)} places from database")
    
    model = train_embeddings(places)
    print(f"✅ Word2Vec trained! Vocabulary size: {len(model.wv)}")
    
    os.makedirs("models", exist_ok=True)
    model.save("models/word2vec.model")
    print(f"✅ Model saved to models/word2vec.model")
    
    if len(places) >= 2:
        sim = get_similarity(model, places[0], places[1])
        print(f"✅ Similarity between '{places[0]['name']}' and '{places[1]['name']}': {sim}")
    
    print(f"✅ Words in vocabulary: {list(model.wv.key_to_index.keys())}")