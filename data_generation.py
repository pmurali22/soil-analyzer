import pandas as pd
import numpy as np
import requests
import os

def download_crop_dataset():
    print("Downloading Crop Recommendation Dataset...")
    url = "https://raw.githubusercontent.com/AbhishekKandoi/Crop-Yield-Prediction-based-on-Indian-Agriculture/main/Crop%20Recommendation%20dataset.csv"
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open("crop_data.csv", "wb") as f:
            f.write(response.content)
        print("Downloaded crop_data.csv successfully.")
    except Exception as e:
        print(f"Error downloading dataset: {e}")

def generate_fertilizer_dataset(num_samples=2000):
    print("Generating Fertilizer Recommendation Dataset...")
    np.random.seed(42)
    # Inputs: N, P, K, pH, crop (we can simplify to just soil nutrients for fertilizer)
    # Actually, crop type affects fertilizer too, but let's keep it based on soil deficiencies
    n = np.random.randint(0, 140, num_samples)
    p = np.random.randint(5, 145, num_samples)
    k = np.random.randint(5, 205, num_samples)
    ph = np.random.uniform(3.5, 9.5, num_samples)
    
    crops = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate', 'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 'apple', 'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee']
    crop = np.random.choice(crops, num_samples)

    labels = []
    for i in range(num_samples):
        # Very simplistic logic to generate somewhat realistic synthetic labels to train on
        if n[i] < 40 and p[i] < 40:
            labels.append("Urea")
        elif p[i] > 60 and k[i] > 60:
            labels.append("DAP")
        elif n[i] > 80:
            labels.append("14-35-14")
        elif k[i] < 30:
            labels.append("MOP")
        elif ph[i] < 5.5:
            labels.append("Lime")
        elif ph[i] > 8.0:
            labels.append("Sulfur")
        else:
            labels.append("28-28")
            
    df = pd.DataFrame({"N": n, "P": p, "K": k, "ph": ph, "crop": crop, "fertilizer": labels})
    df.to_csv("fertilizer_data.csv", index=False)
    print("Saved fertilizer_data.csv")

def generate_watering_dataset(num_samples=2000):
    print("Generating Watering Schedule Dataset...")
    np.random.seed(43)
    temp = np.random.uniform(10.0, 45.0, num_samples)
    humidity = np.random.uniform(15.0, 95.0, num_samples)
    rainfall = np.random.uniform(20.0, 300.0, num_samples)
    crops = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate', 'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 'apple', 'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee']
    crop = np.random.choice(crops, num_samples)
    
    days_to_water = []
    for i in range(num_samples):
        # Base days
        days = 7
        # Adjust based on temp
        if temp[i] > 35: days -= 3
        elif temp[i] < 20: days += 3
        # Adjust based on humidity
        if humidity[i] < 40: days -= 2
        elif humidity[i] > 70: days += 2
        # Adjust based on rainfall
        if rainfall[i] > 150: days += 5
        elif rainfall[i] < 50: days -= 2
        
        # Crop specific adjustments
        if crop[i] in ['rice', 'watermelon']: days -= 2
        elif crop[i] in ['cotton', 'coffee']: days += 2
        
        # Add some noise
        days += np.random.randint(-1, 2)
        
        # Cap between 1 and 15 days
        days = max(1, min(15, days))
        days_to_water.append(days)
        
    df = pd.DataFrame({"temperature": temp, "humidity": humidity, "rainfall": rainfall, "crop": crop, "days_to_water": days_to_water})
    df.to_csv("water_data.csv", index=False)
    print("Saved water_data.csv")

def generate_soil_health_dataset(num_samples=2000):
    print("Generating Soil Health Dataset...")
    np.random.seed(44)
    n = np.random.randint(0, 140, num_samples)
    p = np.random.randint(5, 145, num_samples)
    k = np.random.randint(5, 205, num_samples)
    ph = np.random.uniform(3.5, 9.5, num_samples)
    temp = np.random.uniform(10.0, 45.0, num_samples)
    humidity = np.random.uniform(15.0, 95.0, num_samples)
    rainfall = np.random.uniform(20.0, 300.0, num_samples)
    crops = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate', 'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 'apple', 'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee']
    crop = np.random.choice(crops, num_samples)

    health = []
    for i in range(num_samples):
        score = 0
        if 40 <= n[i] <= 100: score += 1
        if 30 <= p[i] <= 80: score += 1
        if 30 <= k[i] <= 80: score += 1
        if 5.5 <= ph[i] <= 7.5: score += 2
        if 20 <= temp[i] <= 35: score += 1
        if 40 <= humidity[i] <= 80: score += 1
        if 50 <= rainfall[i] <= 200: score += 1
        
        if score >= 6:
            health.append("Healthy")
        elif score >= 3:
            health.append("Moderate")
        else:
            health.append("Poor")
            
    df = pd.DataFrame({"N": n, "P": p, "K": k, "ph": ph, "temperature": temp, "humidity": humidity, "rainfall": rainfall, "crop": crop, "health": health})
    df.to_csv("health_data.csv", index=False)
    print("Saved health_data.csv")

if __name__ == "__main__":
    download_crop_dataset()
    generate_fertilizer_dataset()
    generate_watering_dataset()
    generate_soil_health_dataset()
    print("All data generation complete.")
