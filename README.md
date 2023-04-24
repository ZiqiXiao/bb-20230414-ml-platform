# Machine Learning Platform

## Table of Contents


- [Machine Learning Platform](#machine-learning-platform)
  - [Table of Contents](#table-of-contents)
  - [Authors Ziqi Xiao](#authors-ziqi-xiao)
  - [About ](#about-)
  - [Getting Started ](#getting-started-)
    - [Prerequisites](#prerequisites)
  - [Future Work](#future-work)

## Authors <a name = "authors">Ziqi Xiao</a>

## About <a name = "about"></a>

This project builds up a Flask application which is a Machine Learning Platform. This platform provides the following features:
- **/main**: The main page of the platform, giving the access of the following pages.
- **/train-prepare**: Uploading a dataset in CSV format with all features and a target column and choose one or more from five different models including **Linear Regressing, Random Forest, XGBoost, Multi Layers Perception and Support Vectior Regressor**
- **/train-progress**: Showing the progress of training; as training ends all the metrics(Accuracy) will be diplayed; you can choose the one as you you wish to save along with the dataset headers which will be used as a template for further usage.
- **/predict-prepare**: Uploading a dataset in CSV format; choose one model to predict the target;  *noticed: the dataset should have all the feature columns as the model trained*
- **/predict-progress**: When the prediction is done, a link of downloading the result will be provided.
- **/model-admin**: Showing all the models and dataset templates. You can change the name of models or delete them. You can also download the dataset template for further usage.

## Getting Started <a name = "getting_started"></a>

You can use docker compose to run the application. The docker-compose.yml file is provided in the project. You can run the following command to start the application.

```
docker compose up
```

### Prerequisites

This project use **python 3.9**, all the required packages are listed in the requirements.txt.template. It will change to requirements.txt when you run the docker-compose command, since it will be accomodated to the amd64 or arm64 architecture.

## Future Work
Right now this platform only can handle the linear regression problem. The models has very limited hyperparameters can be set.
More models will be added in the future. More hyperparameters will be added to the models. The platform will be more user friendly.