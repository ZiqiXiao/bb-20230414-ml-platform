import numpy as np
from config import Config

def within_tolerance(a, b, tolerance=Config.DEFAULT_TOLERANCE):
    return np.abs((a - b) / a) <= tolerance

def cal_acc(pred, label):
    return np.mean(within_tolerance(label, pred)) * 100