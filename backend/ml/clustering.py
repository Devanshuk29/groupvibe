import numpy as np
import hdbscan
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances
import json

def extract_features(friends):
    """Convert friend profiles to feature vectors"""
    category_list = ["dining", "nightlife", "adventure", "sports", "nature", "shopping"]
    
    features = []
    for friend in friends:
        budget = friend["budget"]
        vibe = friend["vibe_score"]
        cat_vector = [1 if cat in friend["preferred_categories"] else 0 for cat in category_list]
        feature_vector = [budget, vibe] + cat_vector
        features.append(feature_vector)
    
    return np.array(features)

def cluster_friends(friends):
    if len(friends) == 1:
        return {
            "assignments": {friends[0]["id"]: {"cluster": 0, "is_outlier": False}},
            "num_clusters": 1,
            "outliers": []
        }
    
    # If only 2 friends, also skip clustering
    if len(friends) == 2:
        return {
            "assignments": {f["id"]: {"cluster": 0, "is_outlier": False} for f in friends},
            "num_clusters": 1,
            "outliers": []
        }
    """
    Cluster friends using HDBSCAN
    Input: list of friend profiles
    Output: cluster assignments per friend
    """
    features = extract_features(friends)
    
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2, min_samples=1, allow_single_cluster=True)
    clusters = clusterer.fit_predict(features_scaled)
    
    result = {}
    for i, friend in enumerate(friends):
        cluster_id = int(clusters[i])
        result[friend["id"]] = {
            "cluster": cluster_id,
            "is_outlier": cluster_id == -1
        }
    
    unique_clusters = set(clusters) - {-1}
    
    return {
        "assignments": result,
        "num_clusters": len(unique_clusters),
        "outliers": [friend["id"] for i, friend in enumerate(friends) if clusters[i] == -1]
    }

def get_group_compatibility(friends):
    """
    Calculate how compatible a group of friends is
    Returns score 0-1 (1 = very compatible)
    """
    if len(friends) <= 1:
        return 1.0
    
    features = extract_features(friends)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    distances = euclidean_distances(features_scaled)
    avg_distance = np.mean(distances[np.triu_indices_from(distances, k=1)])
    compatibility = 1 / (1 + avg_distance)
    
    return round(float(compatibility), 2)

if __name__ == "__main__":
    with open("data/training_data.json") as f:
        data = json.load(f)
    
    friends = data["friends"]
    
    result = cluster_friends(friends)
    print(f"✅ Number of clusters found: {result['num_clusters']}")
    print(f"✅ Outliers: {result['outliers']}")
    print(f"✅ Sample assignments: {list(result['assignments'].items())[:5]}")
    
    sample_group = friends[:5]
    score = get_group_compatibility(sample_group)
    print(f"✅ Group compatibility score: {score}")