FROM python:3.7
MAINTAINER Yurii Shevchuk

COPY . /home/project
WORKDIR /home/project

# Install dependencies for matplotlib
RUN apt-get update && apt-get install -y libxft-dev libfreetype6 libfreetype6-dev
RUN pip install --ignore-installed certifi -r ops/requirements.txt
# Activate extentions for the jupyter notebook
RUN jupyter contrib nbextension install --user
