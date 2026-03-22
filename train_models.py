import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, mean_absolute_error
import joblib
import os

def train_crop_model():
    print("Training Crop Prediction Model...")
    df = pd.read_csv("crop_data.csv")
    X = df.drop('label', axis=1)
    y = df['label']
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(f"Crop Model Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    
    joblib.dump(model, 'models/crop_model.pkl')
    joblib.dump(le, 'models/crop_label_encoder.pkl')
    print("Saved crop_model.pkl")

def train_fertilizer_model():
    print("Training Fertilizer Recommendation Model...")
    df = pd.read_csv("fertilizer_data.csv")
    # Features: N, P, K, ph
    X = df[['N', 'P', 'K', 'ph']]
    y = df['fertilizer']
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(f"Fertilizer Model Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    
    joblib.dump(model, 'models/fertilizer_model.pkl')
    joblib.dump(le, 'models/fertilizer_label_encoder.pkl')
    print("Saved fertilizer_model.pkl")

def train_water_model():
    print("Training Watering Schedule Model...")
    df = pd.read_csv("water_data.csv")
    # We have 'crop' as categorical feature, decode it using a label encoder
    le_crop = LabelEncoder()
    df['crop_encoded'] = le_crop.fit_transform(df['crop'])
    
    X = df[['temperature', 'humidity', 'rainfall', 'crop_encoded']]
    y = df['days_to_water']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(f"Watering Model MAE: {mean_absolute_error(y_test, y_pred):.2f} days")
    
    joblib.dump(model, 'models/water_model.pkl')
    joblib.dump(le_crop, 'models/water_crop_encoder.pkl')
    print("Saved water_model.pkl")

def train_health_model():
    print("Training Soil Health Model...")
    df = pd.read_csv("health_data.csv")
    le_crop = LabelEncoder()
    df['crop_encoded'] = le_crop.fit_transform(df['crop'])
    
    X = df[['N', 'P', 'K', 'ph', 'temperature', 'humidity', 'rainfall', 'crop_encoded']]
    y = df['health']
    
    le_health = LabelEncoder()
    y_encoded = le_health.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(f"Soil Health Model Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    
    joblib.dump(model, 'models/health_model.pkl')
    joblib.dump(le_crop, 'models/health_crop_encoder.pkl')
    joblib.dump(le_health, 'models/health_label_encoder.pkl')
    print("Saved health_model.pkl")

if __name__ == "__main__":
    os.makedirs('models', exist_ok=True)
    train_crop_model()
    train_fertilizer_model()
    train_water_model()
    train_health_model()
    print("All models trained and saved successfully.")
