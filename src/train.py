import argparse

import lightgbm
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import roc_auc_score
from category_encoders.ordinal import OrdinalEncoder

from constants import CATEGORICAL_FEATURES, NUMERICAL_FEATURES


model = Pipeline([
    ("feature_preprocessor", ColumnTransformer([
        # Note: Oridnal encoding works quite well for the models based on decision trees
        ("categorical", OrdinalEncoder(handle_missing="return_nan"), CATEGORICAL_FEATURES),
        # Numerical features will be passed through the model without any changes
        ("numerical", "passthrough", NUMERICAL_FEATURES)
    ])),
    ("classifier", lightgbm.LGBMClassifier(
        n_estimators=400,
        num_leaves=12,
        max_depth=4,
        learning_rate=0.02,
        colsample_bytree=0.5,
    )),
])


def parse_args():
    parser = argparse.ArgumentParser(description="Training production model")
    parser.add_argument(
        "-i",
        "--input-csv",
        required=True,
        help="Path to the CSV file contains training data. e.g. /home/data/train.csv",
    )
    parser.add_argument(
        "-om",
        "--output-model",
        required=True,
        help="Path to the file where trained model will be stored. e.g. /home/models/classifier.joblib",
    )
    parser.add_argument(
        "-ot",
        "--output-test-pred",
        required=True,
        help=(
            "Path to the file where predictions for the test data will be stored. "
            "e.g. /home/models/data/test_predictions.csv"
        ),
    )
    return parser.parse_args()


def run_cross_validation(df_train):
    kfold = KFold(n_splits=10)

    X = df_train
    y = df_train.default

    results = []

    for index, (train_index, test_index) in enumerate(kfold.split(X), start=1):
        X_train, X_val = X.iloc[train_index], X.iloc[test_index]
        y_train, y_val = y[train_index], y[test_index]

        model.fit(X_train, y_train)
        probas = model.predict_proba(X_val)
        positive_label_proba = probas[:, 1]

        auc_score = roc_auc_score(y_val, positive_label_proba)
        print(f"[Fold #{index}] ROC AUC Score: {auc_score:.3f}")
        results.append(auc_score)

    print(f"ROC AUC Score: {np.mean(results):.3f} (+/-{2 * np.std(results):.3f})")


if __name__ == "__main__":
    args = parse_args()

    print(f"Reading CSV data from {args.input_csv}")
    df = pd.read_csv(args.input_csv, sep=";")
    df_train = df[~df.default.isnull()]
    df_test = df[df.default.isnull()]

    print("Running cross validation...")
    run_cross_validation(df_train)

    print("Training production model...")
    model.fit(df_train, df_train.default)

    print("Generating predictions for the test data...")
    probas = model.predict_proba(df_test)
    df_test_results = pd.DataFrame({"uuid": df_test.uuid, "pd": probas[:, 1]})
    df_test_results.to_csv(args.output_test_pred, sep=";", index=None)
    print(f"Saved in {args.output_test_pred}")

    print("Saving trained production model...")
    dump(model, args.output_model)
    print(f"Saved in {args.output_model}")

    print("Done")
