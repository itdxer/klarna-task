import os
import time

import pandas as pd
from joblib import load
from waitress import serve
from flask import request, Flask

from constants import CATEGORICAL_FEATURES, NUMERICAL_FEATURES, MODEL_FEATURES, VALID_FEATURES


app = Flask(__name__)
RUN_PROD = os.environ.get("RUN_PROD")
MODEL = load("/home/project/models/model.joblib")


@app.route("/estimate-default-probability", methods=["POST"])
def predict_default_probability():
    data = request.json

    if not set(data).issubset(VALID_FEATURES):
        unknown_features = set(data) - set(VALID_FEATURES)
        return {"status": "error", "message": f"Unknown feature(s): {', '.join(unknown_features)}"}

    if not set(MODEL_FEATURES).issubset(data):
        missing_features = set(MODEL_FEATURES) - set(data)
        return {"status": "error", "message": f"Some of the features are missing: {', '.join(missing_features)}"}

    features_with_incorrect_type = [feature for feature in CATEGORICAL_FEATURES if not isinstance(data[feature], str)]
    if features_with_incorrect_type:
        return {
            "status": "error",
            "message": (
                f"The following features should be specified as "
                f"strings: {', '.join(features_with_incorrect_type)}"
            ),
        }

    features_with_incorrect_type = [
        feature for feature in NUMERICAL_FEATURES
        if not isinstance(data[feature], (int, float, type(None)))
    ]
    if features_with_incorrect_type:
        return {
            "status": "error",
            "message": (
                f"The following features should be specified as integers, floats "
                f"or NaNs: {', '.join(features_with_incorrect_type)}"
            ),
        }

    input_data = pd.DataFrame([data])
    start_prediction_time = time.time()
    probabilities = MODEL.predict_proba(input_data)
    prediction_time = time.time() - start_prediction_time
    default_probability = probabilities[0, 1]

    return {"default_probability": default_probability, "status": "success", "prediction_eta": prediction_time}


if __name__ == "__main__":
    if RUN_PROD:
        print("Running production server")
        serve(app, host="0.0.0.0", port=80)
    else:
        print("Running development server")
        app.run(host="0.0.0.0", port=5000, debug=True)
