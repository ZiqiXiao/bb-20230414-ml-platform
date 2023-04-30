"""
Configuration file for the app.

This file contains the configuration for the app.

BASE_DIR: The base directory of the app.
Config: The configuration class for the app.
"""
import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Config class for the app.

    This class contains the configuration for the app.
    """
    SECRET_KEY = secrets.token_hex(16)
    """The secret key for the app."""

    # Sqlite database
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + os.path.join(BASE_DIR, 'data', 'app.db')
    """The database URI for the app."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """The database track modification for the app."""

    # Upload folder
    UPLOAD_TRAIN_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads', 'train')
    """The upload folder for training data."""
    UPLOAD_PREDICT_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads', 'predict')
    """The upload folder for prediction data."""
    ALLOWED_EXTENSIONS = {'csv'}
    """The allowed extensions for the uploading files."""

    
    """A dictionary stores all the name of model and its package to be imported."""

    # Model Storage folder
    MODEL_FOLDER = os.path.join(BASE_DIR, 'data', 'models')
    """The folder to store the model."""

    # Template Storage folder
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'data', 'model_templates')
    """The folder to store the data template, such that can be downloaded to be used to fill."""

    # Predict result folder
    PREDICT_RESULT_FOLDER = os.path.join(BASE_DIR, 'data', 'predict_result')
    """The folder to store the prediction result."""

    # Log folder
    LOG_FOLDER = os.path.join(BASE_DIR, 'data', 'logs')
    """The folder to store the log."""

    # Default Values
    # Default Tolerance
    DEFAULT_TOLERANCE = 0.15
    """The default tolerance to consider a prediction as correct."""

    # Model Structure files
    MODEL_STRUCTURE = {
        'xgboost': 'app.models.xgb',
        'mlp': 'app.models.mlp',
        'svr': 'app.models.svr',
        'lr': 'app.models.lr',
        'rf': 'app.models.rf',

    }

    DEFAULT_PARAMS = {
        'xgboost': {'num_boost_round': 20,},
                    
        'mlp': {'num_epochs': 50,},

        'svr': {},

        'lr': {},

        'rf': {},
    }
    """The default parameters(hyperparameter) for the models that is showed on the frontpage."""

    DEFAULT_PARAMS_UNDER = {
        'xgboost': {'eta': 0.1,
                    'max_depth': 6,
                    'subsample': 0.8,
                    'colsample_bytree': 0.8,
                    'objective': 'reg:squarederror',},
                    
        'mlp': {'hidden_size': 4,
                'lr': 0.01,},

        'svr': {'kernel': 'rbf',
                'gamma': 'scale',
                'C': 1.0,
                },

        'lr': {},

        'rf': {'n_estimators': 100,
                'max_depth': 4,
                'random_state': 42
            },
    }
    """The default parameters(hyperparameter) for the models that is not showed on the frontpage."""

    DEFAULT_PARAMS_PREPROCESSING = {
        'train_size': 0.8,
    }