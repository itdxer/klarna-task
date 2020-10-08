import pandas as pd
from joblib import load
from flask import request, Flask

from constants import CATEGORICAL_FEATURES, NUMERICAL_FEATURES, MODEL_FEATURES, VALID_FEATURES


app = Flask(__name__)
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
    probabilities = MODEL.predict_proba(input_data)
    default_probability = probabilities[0, 1]

    return {"default_probability": default_probability, "status": "success"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, threaded=True)
