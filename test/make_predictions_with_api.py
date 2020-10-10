import argparse

import requests
import pandas as pd
from joblib import Parallel, delayed
from sklearn.metrics import roc_auc_score


URL_TEMPLATE = "http://{host}/estimate-default-probability"


def parse_args():
    parser = argparse.ArgumentParser(description="Make predictions using REST API")
    parser.add_argument(
        "--host",
        required=True,
        help="Domain name or IP address of the REST API",
    )
    parser.add_argument(
        "-i",
        "--input-csv",
        required=True,
        help="Path to the CSV file contains data. e.g. /home/data/train.csv",
    )
    parser.add_argument(
        "-n",
        "--n-samples",
        type=int,
        default=1000,
        help="Number of random samples that will be used to test API",
    )
    parser.add_argument(
        "-j",
        "--n-jobs",
        type=int,
        default=2,
        help="Number of parallel processes that will be used to query estimates of the default probabilities",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Output intermediate progress of the script",
    )
    return parser.parse_args()


def estimate_default_probability(sample):
    response = requests.post(url, json=sample.to_dict())
    response_json = response.json()

    if response_json["status"] != "success":
        raise Exception(f"Request failed with the following error message: {response_json['message']}")

    return {
        "uuid": sample["uuid"],
        "proba": response_json["default_probability"],
        "request_eta": response.elapsed.total_seconds(),
        "prediction_eta": response_json["prediction_eta"],
        "default": sample["default"],  # ground truth
    }


if __name__ == "__main__":
    args = parse_args()
    url = URL_TEMPLATE.format(host=args.host)

    print(f"Reading CSV data from {args.input_csv}")
    df = pd.read_csv(args.input_csv, sep=";")
    df_train = df[~df.default.isnull()]

    if args.n_samples is not None:
        df_train = df_train.sample(args.n_samples)

    parallel = Parallel(n_jobs=args.n_jobs, verbose=args.verbose)
    responses = parallel(delayed(estimate_default_probability)(sample) for _, sample in df_train.iterrows())
    df_responses = pd.DataFrame(responses)

    print(
        f"Average request ETA: {df_responses.request_eta.mean():.3f} sec "
        f"(+/-{2 * df_responses.request_eta.std():.3f} sec)"
    )
    print(
        f"Average prediction ETA: {df_responses.prediction_eta.mean():.3f} sec "
        f"(+/-{2 * df_responses.prediction_eta.std():.3f} sec)"
    )

    if len(df_responses.default.unique()) == 1:
        print(
            "[WARNING] Only one type of ground truth label appears in the data, try "
            "increasing number of samples in order to get meaningful prediction"
        )
    else:
        # Note: Quite likely that the training data will be used to make the estimate
        print(f"ROC AUC Score: {roc_auc_score(df_responses.default, df_responses.proba)}")
