from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Our custom file for Import
from model.predict import MODEL_VERSION, model, predict_output
from schema.predicted_response import PredictionResponse
from schema.user_input import UserData

# ************************ Configs

app = FastAPI()

# ************************** Routes


@app.get("/")
@app.get("/home")
def home():
    return {"message": "Hello This is the HOME PAGE for Insurance Prediction ML Model"}


# Healthcheck EndPoint :For Machine Readable(Used for Deployment)
@app.get("/health")
def health_check():
    return {"status": "OK", "version": MODEL_VERSION, "model": model is not None}


@app.post("/predict", response_model=PredictionResponse)
def predict_premium(data: UserData):
    user_input = {
        "bmi": data.bmi,
        "age_group": data.age_group,
        "lifestyle_risk": data.lifestyle_risk,
        "city_tier": data.city_tier,
        "income_lpa": data.income_lpa,
        "occupation": data.occupation,
    }

    try:
        prediction = predict_output(user_input)
        return JSONResponse(
            status_code=200,
            content={"response": prediction},
        )
    except Exception as e:
        return JSONResponse(status_code=500, content=str(e))
