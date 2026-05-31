import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import json
import os

class PlaceScoringNet(nn.Module):
    """
    Neural network to score how well a place fits a group
    Architecture: 12 → 64 → 32 → 1
    """
    def __init__(self, input_size=12):
        super(PlaceScoringNet, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.network(x)

def build_feature_vector(place, group_preferences):
    """
    Build a feature vector combining place + group preferences
    Input: place dict + group preferences dict
    Output: 12-dimensional feature vector
    """
    category_list = ["dining", "nightlife", "adventure", "sports", "nature", "shopping"]
    
    place_category = place.get("category", "dining")
    place_cat_vector = [1 if cat == place_category else 0 for cat in category_list]
    
    group_cats = group_preferences.get("preferred_categories", [])
    group_cat_vector = [1 if cat in group_cats else 0 for cat in category_list]
    
    feature_vector = place_cat_vector + group_cat_vector
    
    return np.array(feature_vector, dtype=np.float32)


def generate_training_data(places, num_samples=1000):
    """Generate synthetic training data"""
    category_list = ["dining", "nightlife", "adventure", "sports", "nature", "shopping"]
    X = []
    y = []
    
    for _ in range(num_samples):
        place = np.random.choice(places)
        
        num_cats = np.random.randint(1, 4)
        preferred_cats = np.random.choice(category_list, num_cats, replace=False).tolist()
        group_prefs = {"preferred_categories": preferred_cats}
        
        features = build_feature_vector(place, group_prefs)
        
        place_cat = place.get("category", "dining")
        label = 1.0 if place_cat in preferred_cats else 0.0
        
        label = min(1.0, max(0.0, label + np.random.normal(0, 0.1)))
        
        X.append(features)
        y.append(label)
    
    return np.array(X), np.array(y)


def train_model(places, epochs=200, lr=0.001):
    """Train the neural network"""
    print("Generating training data...")
    X, y = generate_training_data(places)
    
    X_tensor = torch.FloatTensor(X)
    y_tensor = torch.FloatTensor(y).unsqueeze(1)
    
    model = PlaceScoringNet(input_size=12)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCELoss()
    
    print(f"Training neural network for {epochs} epochs...")
    
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        
        outputs = model(X_tensor)
        loss = criterion(outputs, y_tensor)
        
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 50 == 0:
            print(f"Epoch [{epoch+1}/{epochs}] Loss: {loss.item():.4f}")
    
    print("✅ Training complete!")
    return model


def score_place(model, place, group_preferences):
    """
    Score a single place for a group
    Returns score 0-1
    """
    model.eval()
    with torch.no_grad():
        features = build_feature_vector(place, group_preferences)
        tensor = torch.FloatTensor(features).unsqueeze(0)
        score = model(tensor).item()
    return round(score, 4)


if __name__ == "__main__":
    import sqlite3
    
    conn = sqlite3.connect("data/app.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM places")
    places = [dict(p) for p in cursor.fetchall()]
    conn.close()
    
    print(f"✅ Loaded {len(places)} places")
    
    model = train_model(places)
    
    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/neural_net.pth")
    print("✅ Model saved to models/neural_net.pth")
    
    test_group_prefs = {
        "preferred_categories": ["dining", "nightlife"]
    }
    
    print("\n📊 Scores for each place:")
    for place in places:
        score = score_place(model, place, test_group_prefs)
        print(f"   {place['name']}: {score}")