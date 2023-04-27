import numpy as np
from config import Config
from sklearn.metrics import mean_squared_error, mean_absolute_error

def within_tolerance(a, b, tolerance=Config.DEFAULT_TOLERANCE):
    return np.abs((a - b) / a) <= tolerance

def cal_acc(pred, label):
    return np.mean(within_tolerance(label, pred)) * 100

def cal_metrics(y_true, y_pred, type='train'):
    acc = cal_acc(y_true, y_pred)

    mse = mean_squared_error(y_true, y_pred)

    mae = mean_absolute_error(y_true, y_pred)
    return {
            f'{type}_acc': float(acc),
            f'{type}_mse': float(mse),
            f'{type}_mae': float(mae),
        }