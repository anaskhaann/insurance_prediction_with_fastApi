import pickle

import pandas as pd

# Model Version from MLFlow(But we are doing it manually)
MODEL_VERSION = "1.0.0"

# *********************** Import Model

with open("model/model.pkl", "rb") as f:
    model = pickle.load(f)


# Get class labels from model (important for matching probabilities to class names)
class_labels = model.classes_.tolist()


# Function to predict output


def predict_output(user_input: dict):
    # convert the data to df
    input_df = pd.DataFrame([user_input])

    predicted_class = model.predict(input_df)[0]

    # Get probabilities for all classes
    probabilities = model.predict_proba(input_df)[0]
    confidence = max(probabilities)

    # Create mapping: {class_name: probability}
    class_probs = dict(zip(class_labels, map(lambda p: round(p, 4), probabilities)))

    return {
        "predicted_category": predicted_class,
        "confidence": round(confidence, 4),
        "class_probabilities": class_probs,
    }
