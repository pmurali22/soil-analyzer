from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import random
import os
import json
import pandas as pd
import numpy as np
import warnings
import asyncio
from datetime import datetime
import re
from sqlalchemy.orm import Session

# Import our new DB and Auth logic
from database import Base, engine, SessionLocal, User, AnalysisHistory, SensorRecord, get_db
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from pdf_generator import generate_soil_report_pdf

warnings.filterwarnings("ignore")

app = FastAPI(title="Advanced AI Soil Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database error on startup: {e}")

def generate_initial_sensor_reading(time_seed: datetime):
    return {
        "timestamp": time_seed,
        "N": round(random.uniform(50, 100), 2),
        "P": round(random.uniform(30, 80), 2),
        "K": round(random.uniform(30, 80), 2),
        "temperature": round(random.uniform(20.0, 30.0), 2),
        "humidity": round(random.uniform(50.0, 70.0), 2),
        "ph": round(random.uniform(6.0, 7.5), 2),
        "rainfall": round(random.uniform(50.0, 150.0), 2)
    }

async def sensor_simulation_task():
    await asyncio.sleep(2)
    while True:
        db = SessionLocal()
        try:
            last_record = db.query(SensorRecord).order_by(SensorRecord.timestamp.desc()).first()
            actual_now = datetime.utcnow()
            
            if not last_record:
                initial = generate_initial_sensor_reading(actual_now)
                new_rec = SensorRecord(**initial)
                db.add(new_rec)
                db.commit()
            else:
                new_n = max(0, min(150, last_record.N + random.uniform(-5, 5)))
                new_p = max(0, min(150, last_record.P + random.uniform(-5, 5)))
                new_k = max(0, min(150, last_record.K + random.uniform(-5, 5)))
                new_temp = max(15, min(40, last_record.temperature + random.uniform(-1.5, 1.5)))
                new_hum = max(30, min(90, last_record.humidity + random.uniform(-3, 3)))
                new_ph = max(5.0, min(8.0, last_record.ph + random.uniform(-0.1, 0.1)))
                new_rain = max(0, min(300, last_record.rainfall + random.uniform(-10, 10)))
                
                new_reading = SensorRecord(
                    timestamp=actual_now,
                    N=round(new_n, 2),
                    P=round(new_p, 2),
                    K=round(new_k, 2),
                    temperature=round(new_temp, 2),
                    humidity=round(new_hum, 2),
                    ph=round(new_ph, 2),
                    rainfall=round(new_rain, 2)
                )
                db.add(new_reading)
                db.commit()
                
                count = db.query(SensorRecord).count()
                if count > 100:
                    oldest = db.query(SensorRecord).order_by(SensorRecord.timestamp.asc()).first()
                    if oldest:
                        db.delete(oldest)
                        db.commit()
        except Exception as e:
            print(f"Simulation task error: {e}")
        finally:
            db.close()
            
        await asyncio.sleep(5) 

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(sensor_simulation_task())

base_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(base_dir, "..", "models")
crop_data_path = os.path.join(base_dir, "crop_data.json")

print("Loading models and JSON data...")
try:
    with open(crop_data_path, "r") as f:
        crop_db = json.load(f)

    crop_model = joblib.load(os.path.join(models_dir, 'crop_model.pkl'))
    crop_le = joblib.load(os.path.join(models_dir, 'crop_label_encoder.pkl'))
    
    health_model = joblib.load(os.path.join(models_dir, 'health_model.pkl'))
    health_crop_le = joblib.load(os.path.join(models_dir, 'health_crop_encoder.pkl'))
    health_le = joblib.load(os.path.join(models_dir, 'health_label_encoder.pkl'))
    print("Models loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")

class SoilData(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    
class UserLogin(BaseModel):
    email: str
    password: str

class ChatQuery(BaseModel):
    query: str

class AnalysisData(BaseModel):
    soil_data: SoilData
    top_crops: list
    health: dict

# =============== AUTH API ===============

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", user.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", user.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    if not re.search(r"\d", user.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", user.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character")
        
    formatted_name = user.name.strip().title()
    formatted_email = user.email.strip().lower()
    
    existing = db.query(User).filter(User.email == formatted_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = get_password_hash(user.password)
    new_user = User(name=formatted_name, email=formatted_email, password_hash=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": new_user.id, "name": new_user.name, "email": new_user.email}}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    formatted_email = user.email.strip().lower()
    db_user = db.query(User).filter(User.email == formatted_email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": db_user.id, "name": db_user.name, "email": db_user.email}}

@app.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "name": current_user.name, "email": current_user.email}

# =============== CORE API ===============

@app.get("/get-soil-data")
def get_soil_data(mode: Optional[str] = "random", scenario: Optional[str] = None):
    if mode == "test":
        scenarios = ["rice", "wheat", "poor"]
        if not scenario or scenario not in scenarios:
            scenario = random.choice(scenarios)
            
        if scenario == "rice":
            return {
                "N": round(random.uniform(100, 150), 2),
                "P": round(random.uniform(40, 80), 2),
                "K": round(random.uniform(40, 80), 2),
                "temperature": round(random.uniform(20.0, 35.0), 2),
                "humidity": round(random.uniform(70.0, 90.0), 2),
                "ph": round(random.uniform(5.5, 7.0), 2),
                "rainfall": round(random.uniform(200.0, 300.0), 2),
            }
        elif scenario == "wheat":
            return {
                "N": round(random.uniform(50, 90), 2),
                "P": round(random.uniform(30, 60), 2),
                "K": round(random.uniform(30, 60), 2),
                "temperature": round(random.uniform(15.0, 25.0), 2),
                "humidity": round(random.uniform(40.0, 60.0), 2),
                "ph": round(random.uniform(6.0, 7.5), 2),
                "rainfall": round(random.uniform(50.0, 150.0), 2),
            }
        elif scenario == "poor":
            return {
                "N": round(random.uniform(0, 30), 2),
                "P": round(random.uniform(0, 20), 2),
                "K": round(random.uniform(0, 20), 2),
                "temperature": round(random.uniform(20.0, 40.0), 2),
                "humidity": round(random.uniform(30.0, 50.0), 2),
                "ph": round(random.uniform(5.0, 8.0), 2),
                "rainfall": round(random.uniform(0.0, 50.0), 2),
            }
            
    return {
        "N": round(random.uniform(0, 150), 2),
        "P": round(random.uniform(0, 150), 2),
        "K": round(random.uniform(0, 150), 2),
        "temperature": round(random.uniform(15.0, 40.0), 2),
        "humidity": round(random.uniform(30.0, 90.0), 2),
        "ph": round(random.uniform(5.0, 8.0), 2),
        "rainfall": round(random.uniform(0.0, 300.0), 2),
    }

@app.get("/sensor-history")
def get_sensor_history(db: Session = Depends(get_db)):
    records = db.query(SensorRecord).order_by(SensorRecord.timestamp.desc()).limit(24).all()
    result = []
    for r in reversed(records):
        result.append({
            "timestamp": r.timestamp.isoformat(),
            "N": r.N, "P": r.P, "K": r.K,
            "temperature": r.temperature, "humidity": r.humidity,
            "ph": r.ph, "rainfall": r.rainfall
        })
    return result

@app.get("/sensor-stream")
def get_sensor_stream(db: Session = Depends(get_db)):
    last = db.query(SensorRecord).order_by(SensorRecord.timestamp.desc()).first()
    if last:
        return {
            "timestamp": last.timestamp.isoformat(),
            "N": last.N, "P": last.P, "K": last.K,
            "temperature": last.temperature, "humidity": last.humidity,
            "ph": last.ph, "rainfall": last.rainfall
        }
    return {}

@app.post("/predict-all")
def predict_all(data: SoilData):
    crop_features = pd.DataFrame([np.array([data.N, data.P, data.K, data.temperature, data.humidity, data.ph, data.rainfall])], 
                                 columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
    
    probabilities = crop_model.predict_proba(crop_features)[0]
    top_5_idx = np.argsort(probabilities)[-5:][::-1]
    
    top_crops = []
    for idx in top_5_idx:
        crop_name = crop_le.inverse_transform([idx])[0]
        prob_percent = round(float(probabilities[idx]) * 100, 2)
        
        cdata = crop_db.get(crop_name.lower(), crop_db.get("rice"))
        
        cost = cdata["cost_per_acre"]
        yield_kg = cdata["yield_per_acre"]
        price = cdata["market_price_per_kg"]
        profit = (yield_kg * price) - cost
        
        top_crops.append({
            "name": crop_name.capitalize(),
            "probability": prob_percent,
            "fertilizer_schedule": cdata["fertilizer_schedule"],
            "water_schedule": cdata["water_schedule"],
            "economics": {
                "cost": cost,
                "yield": yield_kg,
                "price": price,
                "profit": profit
            }
        })

    top_crop_name = top_crops[0]["name"].lower()
    try:
        health_crop_encoded = health_crop_le.transform([top_crop_name])[0]
    except ValueError:
        health_crop_encoded = 0
        
    health_features = pd.DataFrame([np.array([data.N, data.P, data.K, data.ph, data.temperature, data.humidity, data.rainfall, health_crop_encoded])],
                                   columns=['N', 'P', 'K', 'ph', 'temperature', 'humidity', 'rainfall', 'crop_encoded'])
    health_pred_encoded = health_model.predict(health_features)
    health_pred = health_le.inverse_transform(health_pred_encoded)[0]
    health_proba = health_model.predict_proba(health_features)[0]
    health_confidence = round(float(np.max(health_proba)) * 100, 2)

    return {
        "top_crops": top_crops,
        "health": {
            "prediction": str(health_pred),
            "confidence": health_confidence
        }
    }

@app.post("/save-analysis")
def save_analysis(data: AnalysisData, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    history = AnalysisHistory(
        user_id=current_user.id,
        timestamp=datetime.utcnow(),
        N=data.soil_data.N,
        P=data.soil_data.P,
        K=data.soil_data.K,
        temperature=data.soil_data.temperature,
        humidity=data.soil_data.humidity,
        ph=data.soil_data.ph,
        rainfall=data.soil_data.rainfall,
        top_crops=data.top_crops,
        health=data.health
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return {"status": "success", "history_id": history.id}

@app.get("/download-report/{history_id}")
def download_report(history_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(AnalysisHistory).filter(AnalysisHistory.id == history_id, AnalysisHistory.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Report not found")
        
    pdf_buffer = generate_soil_report_pdf(record, current_user.name)
    
    headers = {
        'Content-Disposition': f'attachment; filename="SoilSmart_Report_{history_id}.pdf"'
    }
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)

@app.get("/history")
def get_user_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    records = db.query(AnalysisHistory).filter(AnalysisHistory.user_id == current_user.id).order_by(AnalysisHistory.timestamp.desc()).all()
    # Serialize for JSON
    res = []
    for r in records:
        res.append({
            "id": r.id,
            "timestamp": r.timestamp.isoformat(),
            "soil_metrics": {"N": r.N, "P": r.P, "K": r.K, "temperature": r.temperature, "humidity": r.humidity, "ph": r.ph, "rainfall": r.rainfall},
            "top_crops": r.top_crops,
            "health": r.health
        })
    return res

# =============== CHATBOT API ===============

@app.post("/chat")
def chat(query: ChatQuery, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    last_analysis = db.query(AnalysisHistory).filter(AnalysisHistory.user_id == current_user.id).order_by(AnalysisHistory.timestamp.desc()).first()
    
    q_lower = query.query.lower()
    
    if not last_analysis:
        return {"response": "Hi there! I am your AI Soil Assistant. Please run a soil analysis on the Dashboard first, so I can give you personalized farming advice!"}
        
    health = last_analysis.health.get("prediction", "Unknown")
    top_crop = last_analysis.top_crops[0]["name"] if last_analysis.top_crops else "Unknown"
    
    if "crop" in q_lower or "best" in q_lower or "suitable" in q_lower:
        return {"response": f"Based on your latest soil analysis, **{top_crop}** is highly suitable for your land. Overall soil health is measured as {health}."}
    
    elif "water" in q_lower or "irrigation" in q_lower or "often" in q_lower:
        schedule = last_analysis.top_crops[0]["water_schedule"]["Frequency"] if last_analysis.top_crops else "regularly"
        return {"response": f"For your top recommended crop ({top_crop}), you should water it **{schedule}**. However, always adjust based on current rainfall levels in the sensor dashboard!"}
        
    elif "fertiliz" in q_lower or "nutrient" in q_lower or "add" in q_lower:
        base_fert = last_analysis.top_crops[0]["fertilizer_schedule"]["Basal"] if last_analysis.top_crops else "standard compost"
        return {"response": f"To optimize growth for {top_crop}, apply **{base_fert}** as a basal dose. Your soil health is '{health}', so focus on maintaining balanced NPK levels."}
        
    elif "ph" in q_lower or "acid" in q_lower:
        ph_val = last_analysis.ph
        if ph_val < 6.0:
            return {"response": f"Your soil pH is {ph_val}, which is quite acidic. Consider adding agricultural lime to raise it for {top_crop}."}
        elif ph_val > 7.5:
            return {"response": f"Your soil pH is {ph_val}, which is alkaline. You might want to add sulfur or organic mulch safely."}
        else:
            return {"response": f"Your soil pH is {ph_val}, which is in a great neutral range for {top_crop}!"}
            
    else:
        return {"response": f"I'm your Soil Smart Assistant! I mostly know about your latest analysis showing **{top_crop}** potential. Ask me about crops, watering, or fertilizers for your specific conditions!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
