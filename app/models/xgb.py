import xgboost as xgb
from xgboost.callback import TrainingCallback
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import os
import joblib
import pandas as pd
from app.models.utils import cal_acc
import numpy as np
from config import Config


class TrainingProgressCallback(TrainingCallback):
    """
    计算训练进度的回调函数
    """
    def __init__(self, total_rounds, socketio=None):
        self.count = 0
        self.total_rounds = total_rounds
        self.socketio = socketio

    def after_iteration(self, model, epoch, evals_log):
        self.count += 1
        progress = self.count / self.total_rounds * 100
        if self.socketio is not None:
            self.socketio.emit('training_progress', {'modelName': 'xgboost', 'progress': progress})
        else:
            print(f'training progress: {progress}%')

class Model:
    """
    XGBoost模型
    """
    def __init__(self, model=None, app=None, socketio=None):
        self.model = model
        self.app = app
        self.socketio = socketio
        self.default_params = Config.DEFAULT_PARAMS['xgboost']
        self.default_params.update(Config.DEFAULT_PARAMS_UNDER['xgboost'])

    def log_message(self, message):
        if self.socketio is not None:
            self.socketio.emit('training_log', {'message': message})

    def load_dataset(self, dataset_path):
        return pd.read_csv(dataset_path)

    def train(self, dataset_path, label, custom_params={}):
        # 加载数据集
        dataset = self.load_dataset(dataset_path)
        # print('dataset loaded')
        self.app.logger.info('dataset loaded')

        # 对数据集进行预处理，例如划分训练集和验证集，并转换为xgboost需要的数据格式
        train_X, valid_X, train_y, valid_y = train_test_split(dataset.drop(label , axis=1), dataset[label], test_size=0.2, random_state=42)
        # print('dataset split')
        self.app.logger.info('dataset split')

        dtrain = xgb.DMatrix(train_X, label=train_y)
        dvalid = xgb.DMatrix(valid_X, label=valid_y)

        # 设置模型参数
        self.default_params.update(custom_params)
        num_boost_round = self.default_params.pop('num_boost_round')

        # 训练模型
        # print('training model ... ')
        self.app.logger.info('training model ... ')
        
        progress_callback = TrainingProgressCallback(num_boost_round, self.socketio)
        self.model = xgb.train(
            self.default_params, 
            dtrain, 
            num_boost_round=num_boost_round, 
            evals=[(dtrain, 'train'), (dvalid, 'valid')], 
            early_stopping_rounds=5, 
            verbose_eval=0,
            callbacks=[progress_callback]
            )

        train_acc = cal_acc(np.array(self.model.predict(dtrain)), np.array(train_y))
        valid_acc = cal_acc(np.array(self.model.predict(dvalid)), np.array(valid_y))

        self.socketio.emit('model_evaluation', 
                               {'modelName': 'xgboost',
                                'metrics': {
                                    'train_acc': train_acc,
                                    'valid_acc': valid_acc,
                                }
                                })
        

        # print('training successfully')
        self.app.logger.info('training successfully')
        return self.model

    def predict(self, dataset_path):
        if self.model is None:
            self.app.logger.info("Model not trained yet. Train the model before making predictions.")
        self.app.logger.info('predicting ... ')
        data = self.load_dataset(dataset_path)
        dtest = xgb.DMatrix(data)
        predicted = self.model.predict(dtest)
        return predicted

    def save_model(self, model_path):
        if self.model is None:
            self.app.logger.warning("Model not trained yet. Train the model before saving.")
        joblib.dump(self.model, model_path)
        self.app.logger.info('model saved')

    def load_model(self, model_path):
        self.model = joblib.load(model_path)
        self.app.logger.info('model loaded')