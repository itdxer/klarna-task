## ML Case Study for Klarna

> This case consists of a supervised learning example, similar to what we are working with on a daily basis in Klarna . Your task is to predict the probability of default for the datapoints where the ​default ​variable is not set. The answer should contain the resulting predictions in a csv file with two columns, uuid ​and ​pd ​(probability of ​default==1​). Once done expose this model with an API Endpoint on a cloud provider of your choice. Bonus points if you use AWS. Send us the details on how to query the endpoint, attach code used for modelling, a short (max one page) explanation of your model and how you validated it.

## Workflow

1. Create and ECR repository on AWS

**Note**: You need to do this step only once. There is no need to run this step during the subsequent releases

```bash
$ aws ecr create-repository --repository-name klarna-task
```

Set environmental variable which will indicate the registry that should be used. For example

```bash
export DOCKER_REGISTRY=424261332927.dkr.ecr.eu-central-1.amazonaws.com
```

2. Build docker image

```bash
$ docker-compose build
```

3. Train the prediction model

```bash
$ docker-compose run train-model
```

In addition to training the model and storing it in the `models/` folder this script will create a `data/test_predictions.csv` file which contains predictions for the test data. Quality of the model could be assessed from the cross validation scores.

4. Test REST API server

```bash
$ docker-compose up rest-api
```

Send test request in order to make sure that API works (sends to localhost:5000)

```bash
$ ./test/send_valid_request.sh
{
  "default_probability": 0.004957802768308741,
  "status": "success"
}
```

**Note**: You can also check that the `docker-compose up rest-api-prod` command works as well

5. Push docker model to ECR

**Note**: Image needs to be rebuild because of the pre-trained model.

```bash
$ $(aws ecr get-login --no-include-email --region eu-central-1)
$ docker-compose build
$ docker-compose push
```

6. Deploy REST API with Terraform on EC2

First, you need to specify `*.pem` key that could be used to SSH to the machine. By default, the terraform script will be looking for the `klarna-task-key` in the `~/.ssh/klarna-task-key.pem`, but the name of the key could be changed.

```bash
$ export TF_VAR_docker_registry=$DOCKER_REGISTRY
$ export TF_VAR_key_pair_name="klarna-task-key"  # or some other name of the key
$ terraform init
$ terraform apply
```

7. In the terraform logs check IP address of the machine and checks the API

## Run jupyter notebook

```bash
$ docker-compose up notebook
```

## Example on how to use the API

```python
import requests

# All features from the dataset.csv file with the same names (API will select important features)
features = {"age": 59, "merchant_group": "Entertainment", ...}
response = requests.post("http://ip-address/estimate-default-probability", json=features)
response_json = response.json()
```

## Model

The final model is a gradient boosted trees based lightgbm package. Among other models it had the largest cross validation score. Most of the available features has been used except a few which has been eliminated because of their low feature importance. Final models has an average 0.912 ROC AUC score on 10-fold cross validation. Most of the features are being used without any pre-processing, except categorical features, which has been transformed with an ordinal encoding. Parameters of the gradient boosted trees has been tuned in order to reduce effect of the overfitting.

## TODO: Stuff that could be added in order to improve the project

* After the training deploy model to S3 rather than storing it within the docker image. Afterwards, during the deployment, the model could be downloaded on EC2 and attached to the docker image
* Project should be unit tested automatically rather than manually running a script
