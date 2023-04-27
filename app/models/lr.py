from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from app.models.utils import cal_metrics
import os
import joblib
import pandas as pd
import numpy as np
from config import Config


class Model:
    """
    Linear Regression模型
    """
    def __init__(self, model=None, app=None, socketio=None):
        self.model = model
        self.app = app
        self.socketio = socketio
        self.default_params = Config.DEFAULT_PARAMS['lr']
        self.default_params.update(Config.DEFAULT_PARAMS_UNDER['lr'])

    def log_message(self, message):
        if self.socketio is not None:
            self.socketio.emit('training_log', {'message': message})

    def load_dataset(self, dataset_path):
        return pd.read_csv(dataset_path)

    def train(self, dataset_path, label, custom_params={}):
        # 加载数据集
        dataset = self.load_dataset(dataset_path)
        self.app.logger.info('dataset loaded')

        # 对数据集进行预处理，例如划分训练集和验证集
        train_X, valid_X, train_y, valid_y = train_test_split(dataset.drop(label , axis=1), dataset[label], test_size=0.2, random_state=42)
        self.app.logger.info('dataset split')

        # 设置模型参数
        self.default_params.update(custom_params)

        # 训练模型
        self.app.logger.info('training model ... ')
        self.model = LinearRegression(**self.default_params)
        self.model.fit(train_X, train_y)

        train_metrics = cal_metrics(train_y, self.model.predict(train_X), type='train')
        valid_metrics = cal_metrics(valid_y, self.model.predict(valid_X), type='valid')
        valid_metrics.update(train_metrics)

        self.socketio.emit('model_evaluation', 
                               {'modelName': 'lr',
                                'metrics': valid_metrics
                                })

        self.socketio.emit('training_progress', {'modelName': 'lr', 'progress': 100})
        self.app.logger.info('training successfully')
        return self.model

    def predict(self, dataset_path):
        if self.model is None:
            self.app.logger.info("Model not trained yet. Train the model before making predictions.")
        self.app.logger.info('predicting ... ')
        data = self.load_dataset(dataset_path)
        predicted = self.model.predict(data)
        return predicted

    def save_model(self, model_path):
        if self.model is None:
            self.app.logger.warning("Model not trained yet. Train the model before saving.")
        joblib.dump(self.model, model_path)
        self.app.logger.info('model saved')

    def load_model(self, model_path):
        self.model = joblib.load(model_path)
        self.app.logger.info('model loaded')
