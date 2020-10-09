## ML Case Study for Klarna

> This case consists of a supervised learning example, similar to what we are working with on a daily basis in Klarna . Your task is to predict the probability of default for the datapoints where the ​default ​variable is not set. The answer should contain the resulting predictions in a csv file with two columns, uuid ​and ​pd ​(probability of ​default==1​). Once done expose this model with an API Endpoint on a cloud provider of your choice. Bonus points if you use AWS. Send us the details on how to query the endpoint, attach code used for modelling, a short (max one page) explanation of your model and how you validated it.

## Workflow

1. Train the prediction model

```bash
$ docker-compose run train-model
```

In addition to training the model and storing it in the `models/` folder this script will create a `data/test_predictions.csv` file which contains predictions for the test data. Quality of the model could be assessed from the cross validation scores.

2. Start REST API server

```bash
$ docker-compose up rest-api
```

3. Send test request in order to make sure that API works

```bash
$ ./test/send_valid_request.sh
```

## Run jupyter notebook

```bash
$ docker-compose up notebook
```
