from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import os
import pandas as pd

app = FastAPI()

# get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# model paths
model_path = os.path.join(BASE_DIR, "model", "fraud_model.pkl")
credit_model_path = os.path.join(BASE_DIR, "model", "creditcard_fraud_model.pkl")

# load models
with open(model_path, "rb") as f:
    model = pickle.load(f)

with open(credit_model_path, "rb") as f:
    credit_model = pickle.load(f)


@app.get("/")
def home():
    return {"message": "FraudShield AI API is running"}


# -----------------------------
# Input Schemas
# -----------------------------

class Transaction(BaseModel):
    step: int
    type: int
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float
    isFlaggedFraud: int


class CreditCardTransaction(BaseModel):
    features: list


# -----------------------------
# PaySim Wallet Fraud Endpoint
# -----------------------------

@app.post("/predict")
def predict_fraud(transaction: Transaction):

    data = [[
        transaction.step,
        transaction.type,
        transaction.amount,
        transaction.oldbalanceOrg,
        transaction.newbalanceOrig,
        transaction.oldbalanceDest,
        transaction.newbalanceDest,
        transaction.isFlaggedFraud
    ]]

    prob = model.predict_proba(data)[0][1]
    risk_score = round(prob * 100, 2)

    if risk_score < 40:
        decision = "APPROVE"
    elif risk_score < 70:
        decision = "FLAG"
    else:
        decision = "BLOCK"

    return {
        "fraud_probability": float(prob),
        "risk_score": risk_score,
        "decision": decision
    }


# -----------------------------
# Credit Card Fraud Endpoint
# -----------------------------

@app.post("/predict_creditcard")
def predict_creditcard(transaction: CreditCardTransaction):

    columns = [
        "Time","V1","V2","V3","V4","V5","V6","V7","V8","V9",
        "V10","V11","V12","V13","V14","V15","V16","V17","V18",
        "V19","V20","V21","V22","V23","V24","V25","V26","V27",
        "V28","Amount"
    ]

    data = pd.DataFrame([transaction.features], columns=columns)

    prob = credit_model.predict_proba(data)[0][1]
    risk_score = round(prob * 100, 2)

    if risk_score < 40:
        decision = "APPROVE"
    elif risk_score < 70:
        decision = "FLAG"
    else:
        decision = "BLOCK"

    return {
        "fraud_probability": float(prob),
        "risk_score": risk_score,
        "decision": decision
    }
