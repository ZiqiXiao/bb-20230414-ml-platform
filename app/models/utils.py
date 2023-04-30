import numpy as np
import pandas as pd
from config import Config
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

def within_tolerance(a, b, tolerance=Config.DEFAULT_TOLERANCE):
    return np.abs((a - b) / a) <= tolerance

def cal_acc(pred, label):
    return np.mean(within_tolerance(label, pred)) * 100

def cal_metrics(y_true, y_pred, type='train'):
    acc = cal_acc(y_true, y_pred)

    mse = mean_squared_error(y_true, y_pred)

    rmse = mean_squared_error(y_true, y_pred, squared=False)

    mae = mean_absolute_error(y_true, y_pred)

    r2 = r2_score(y_true, y_pred)
    return {
            f'{type}_acc': float(acc),
            f'{type}_mse': float(mse),
            f'{type}_mae': float(mae),
            f'{type}_rmse': float(rmse),
            f'{type}_r2': float(r2)
        }

def log_message(socketio, message):
    if socketio is not None:
        socketio.emit('training_log', {'message': message})

def load_dataset(dataset_path):
    # 加载数据集
    dataset = pd.read_csv(dataset_path)
    return dataset

def data_preprocess(dataset, label, train_size):
    # 对数据集进行预处理，例如划分训练集和验证集，并转换为xgboost需要的数据格式
    train_X, valid_X, train_y, valid_y = train_test_split(dataset.drop(label , axis=1), dataset[label], train_size=train_size, random_state=42)
    return train_X, valid_X, train_y, valid_y