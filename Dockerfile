FROM tiangolo/python-machine-learning:python3.7 as klarna-task-base
MAINTAINER Yurii Shevchuk

COPY . /home/project
WORKDIR /home/project

# Install dependencies for matplotlib
RUN apt-get update && apt-get install -y libxft-dev libfreetype6 libfreetype6-dev
RUN pip install --ignore-installed certifi -r requirements.txt
# Activate extentions for the jupyter notebook
RUN jupyter contrib nbextension install --user

# Production build which is easy to run (especially on AWS)
FROM klarna-task-base as klarna-task-prod

EXPOSE 5000
CMD python src/server.py
