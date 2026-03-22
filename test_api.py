import requests
import json

BASE_URL = "http://localhost:8000"

def run_test(name, payload):
    print(f"\n--- {name} ---")
    print(f"Input: {json.dumps(payload)}")
    response = requests.post(f"{BASE_URL}/predict-all", json=payload)
    if response.status_code == 200:
        res = response.json()
        print("Output (ML Predictions):")
        print(f" - Crop: {res['crop']['prediction']} (Confidence: {res['crop']['confidence']}%)")
        print(f" - Fertilizer: {res['fertilizer']['prediction']} (Confidence: {res['fertilizer']['confidence']}%)")
        print(f" - Watering Expected: Every {res['watering']['prediction_days']} days")
        print(f" - Soil Health: {res['health']['prediction']} (Confidence: {res['health']['confidence']}%)")
    else:
        print(f"Error: {response.text}")

# Test Case 1: High Nitrogen, high humidity -> expect Rice
tc1 = {
    "N": 120.0, "P": 40.0, "K": 40.0, 
    "temperature": 25.0, "humidity": 85.0, "ph": 6.5, "rainfall": 200.0
}

# Test Case 2: Moderate NPK, low rainfall -> expect Maize or similar
tc2 = {
    "N": 60.0, "P": 50.0, "K": 50.0, 
    "temperature": 22.0, "humidity": 50.0, "ph": 6.5, "rainfall": 40.0
}

# Test Case 3: Low nutrients -> Expect Poor health + fertilizer need
tc3 = {
    "N": 15.0, "P": 10.0, "K": 10.0, 
    "temperature": 30.0, "humidity": 40.0, "ph": 7.0, "rainfall": 100.0
}

print("Checking GET /get-soil-data...")
get_res = requests.get(f"{BASE_URL}/get-soil-data")
print("Simulated Sensor Payload:", get_res.json())

run_test("Test Case 1 (High N, High Humidity => Rice)", tc1)
run_test("Test Case 2 (Moderate NPK, Low Rainfall => Maize/Wheat)", tc2)
run_test("Test Case 3 (Low Nutrients => Poor Health, Needs Fertilizer)", tc3)
