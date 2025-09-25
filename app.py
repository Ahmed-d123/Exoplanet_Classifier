from fastapi import FastAPI, UploadFile, File
import pandas as pd
import joblib
import numpy as np
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware



# Load Saved (1)
scaler = joblib.load("models/scaler.joblib")
label_encoder = joblib.load("models/label_encoder.joblib")
ensemble = joblib.load("models/ensemble_pipeline.joblib")

# Features (2)
features = [
    'koi_period', 'koi_prad', 'koi_sma', 'koi_incl',
    'koi_teq', 'koi_slogg', 'koi_srad', 'koi_smass', 'koi_steff'
]

# Extra features
extra_features = ['density_star', 'prad_ratio', 'period_ratio', 'teq_scaled']
all_features = features + extra_features


# Create FastAPI app (3)

app = FastAPI(title="AI-Powered Exoplanet Classifier")


# Health check

@app.get("/")
def home():
    return {"message": "🚀 Exoplanet Classifier API is running!"}


# Prediction endpoint (4)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # read uploaded CSV
    df = pd.read_csv(file.file)

    # check required columns
    missing = [f for f in features if f not in df.columns]
    if missing:
        return {"error": f"Missing columns: {missing}"}

    # feature engineering
    df['density_star'] = df['koi_smass'] / (df['koi_srad']**3 + 1e-6)
    df['prad_ratio']   = df['koi_prad'] / (df['koi_srad'] + 1e-6)
    df['period_ratio'] = df['koi_period'] / (df['koi_sma'] + 1e-6)
    df['teq_scaled']   = df['koi_teq'] / (df['koi_steff'] + 1e-6)

    # scale features
    X = scaler.transform(df[all_features])

    # predict
    preds = ensemble.predict(X)
    probs = ensemble.predict_proba(X)

    # decode labels
    classes = label_encoder.inverse_transform(preds)

    results = []
    for i in range(len(classes)):
        result = {
            "predicted_class": str(classes[i]),
            "probabilities": {
                label_encoder.classes_[j]: float(probs[i][j])
                for j in range(len(label_encoder.classes_))
            }
        }
        results.append(result)

    return {"results": results}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
