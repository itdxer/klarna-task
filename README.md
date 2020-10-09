## ML Case Study for Klarna

> This case consists of a supervised learning example, similar to what we are working with on a daily basis in Klarna . Your task is to predict the probability of default for the datapoints where the ​default ​variable is not set. The answer should contain the resulting predictions in a csv file with two columns, uuid ​and ​pd ​(probability of ​default==1​). Once done expose this model with an API Endpoint on a cloud provider of your choice. Bonus points if you use AWS. Send us the details on how to query the endpoint, attach code used for modelling, a short (max one page) explanation of your model and how you validated it.

## Workflow

1. Build docker image

```bash
$ docker-compose build
```

2. Train the prediction model

```bash
$ docker-compose run train-model
```

In addition to training the model and storing it in the `models/` folder this script will create a `data/test_predictions.csv` file which contains predictions for the test data. Quality of the model could be assessed from the cross validation scores.

2. Test REST API server

```bash
$ docker-compose up rest-api
```

Send test request in order to make sure that API works

```bash
$ ./test/send_valid_request.sh
{
  "default_probability": 0.004957802768308741,
  "status": "success"
}
```

3. Create and ECR repository on AWS

**Note**: You need to do this step only once. There is no need to run this step during the subsequent releases

```bash
$ aws ecr create-repository --repository-name klarna-task
```

4. Push docker model to ECR

**Note**: Image needs to be rebuild because of the pre-trained model.

```bash
$ $(aws ecr get-login --no-include-email --region eu-central-1)
$ docker-compose build
$ docker-compose push
```

5. Deploy REST API with Terraform on EC2

```bash
$ terraform init
$ terraform apply
```

6. In the terraform logs check IP address of the machine and checks the API

## Run jupyter notebook

```bash
$ docker-compose up notebook
```

## TODO: Stuff that could be added in order to improve the project

* After the training deploy model to S3 rather than storing it within the docker image. Afterwards, during the deployment, the model could be downloaded on EC2 and attached to the docker image
* Project should be unit tested automatically rather than manually running a script
