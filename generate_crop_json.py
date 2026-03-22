import json

crops = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate', 'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 'apple', 'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee']

data = {}

# Baseline templates mapping crop to rough profiles
# Category logic to build structured variance
for c in crops:
    if c in ['rice', 'cotton', 'jute', 'banana', 'sugarcane']:
        cost = 15000 + (len(c)*500)
        yield_kg = 2000 + (len(c)*200)
        price = 20 + len(c)
        fert = {
            "Basal": "DAP 30 kg/acre + MOP 15 kg/acre + Urea 20 kg/acre",
            "Vegetative": "Urea 30 kg/acre (after 30 days)",
            "Flowering": "Urea 15 kg/acre + Zinc spray"
        }
        water = {
            "Frequency": "Every 2-4 days",
            "Stages": "Continuous moisture needed. Drain slightly before harvest."
        }
    elif c in ['mango', 'apple', 'orange', 'papaya', 'grapes', 'pomegranate', 'coconut', 'coffee']:
        cost = 25000 + (len(c)*300)
        yield_kg = 4000 + (len(c)*150)
        price = 45 + (len(c)*2)
        fert = {
            "Basal": "FYM 5 tons/acre + SSP 50 kg/acre + MOP 30 kg/acre",
            "Vegetative": "Urea 25 kg/acre (Spring)",
            "Flowering": "Foliar Boron + Calcium during fruit set"
        }
        water = {
            "Frequency": "Every 7-12 days",
            "Stages": "Critical during fruit development, reduce before ripening."
        }
    else: # legumes, maize, etc
        cost = 8000 + (len(c)*400)
        yield_kg = 1200 + (len(c)*100)
        price = 50 + len(c)
        fert = {
            "Basal": "DAP 20 kg/acre + Rhizobium culture",
            "Vegetative": "Urea 10 kg/acre (if required)",
            "Flowering": "2% DAP spray at pod formation"
        }
        water = {
            "Frequency": "Every 15-20 days",
            "Stages": "Crucial at flowering and pod filling stages."
        }

    data[c.lower()] = {
        "cost_per_acre": cost,
        "yield_per_acre": yield_kg,
        "market_price_per_kg": price,
        "fertilizer_schedule": fert,
        "water_schedule": water
    }
    
# Save to backend/crop_data.json
with open('backend/crop_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Created backend/crop_data.json")
