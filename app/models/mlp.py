import copy
import random
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch import optim
import pandas as pd
from sklearn.model_selection import train_test_split
from app.models.utils import cal_metrics, data_preprocess, load_dataset
import numpy as np
from config import Config


class MLP(nn.Module):
    """
    PyTorch MLP模型
    """
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, 12)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(12, output_size)


    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        out = self.relu2(out)
        out = self.fc3(out)
        return out
    
class MyDataset(Dataset):
    """
    数据集类
    """
    def __init__(self, data, label):
        self.data = torch.tensor(data.values, dtype=torch.float32)
        self.label = torch.tensor(label.values, dtype=torch.float32).view(-1, 1)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index], self.label[index]

class Model:
    """
    PyTorch MLP模型
    """
    def __init__(self, model=None, app=None, socketio=None):
        self.model = model
        self.app = app
        self.socketio = socketio
        self.default_params = Config.DEFAULT_PARAMS['mlp'].copy()
        self.default_params.update(Config.DEFAULT_PARAMS_UNDER['mlp'])

    def log_message(self, message):
        if self.socketio is not None:
            self.socketio.emit('training_log', {'message': message})
    

    def train(self, dataset_path, label, custom_params={}):
        # 加载数据集
        dataset = load_dataset(dataset_path)
        self.app.logger.info('dataset loaded')

       # 设置模型参数
        self.default_params.update(custom_params)
        train_size = self.default_params.get('train_size', Config.DEFAULT_PARAMS_PREPROCESSING['train_size'])
        self.default_params.pop('train_size')
        print(train_size)

        # 对数据集进行预处理，例如划分训练集和验证集
        train_X, valid_X, train_y, valid_y = data_preprocess(dataset, label, train_size=train_size)
        self.app.logger.info('dataset split')
        train_dataset = MyDataset(train_X, train_y)
        valid_dataset = MyDataset(valid_X, valid_y)

        def seed_worker(worker_id):
            worker_seed = torch.initial_seed() % 2**32
            np.random.seed(worker_seed)
            random.seed(worker_seed)

        # 创建DataLoader
        train_dataloader = DataLoader(train_dataset, 
                                      batch_size=64, 
                                      shuffle=True, 
                                      worker_init_fn=seed_worker, 
                                      generator=torch.Generator().manual_seed(0))
        valid_dataloader = DataLoader(valid_dataset, 
                                      batch_size=64, 
                                      shuffle=False, 
                                      worker_init_fn=seed_worker, 
                                      generator=torch.Generator().manual_seed(0))
        self.app.logger.info('dataset preprocessed')

        # 设置模型参数
        input_size = train_X.shape[1]
        output_size = 1

        hidden_size = custom_params.get('hidden_size', self.default_params['hidden_size'])
        lr = custom_params.get('lr', self.default_params['lr'])
        num_epochs = custom_params.get('num_epochs', self.default_params['num_epochs'])

        # 初始化模型
        self.model = MLP(input_size, hidden_size, output_size)

        # 定义损失函数和优化器
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)

        def eval_model(model, dataloader, type='train'):
            """
            评估模型
            """
            model.eval()
            y_true = np.array([])
            y_pred = np.array([])
            with torch.no_grad():
                for inputs, targets in dataloader:
                    outputs = model(inputs)
                    y_true = np.append(y_true, targets.numpy().flatten())
                    y_pred = np.append(y_pred, outputs.numpy().flatten())
                    
            metrics = cal_metrics(y_true, y_pred, type=type)
            return metrics

        self.app.logger.info('training started')
        # 训练模型
        self.model.train()
        best_acc = 0.0
        best_train_metrics = {}
        best_valid_metrics = {}
        torch.manual_seed(42)
        for epoch in range(num_epochs):
            for i, (inputs, targets) in enumerate(train_dataloader):
                # 向前传播
                outputs = self.model(inputs)
                loss = criterion(outputs, targets)

                # 反向传播和优化
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            # 计算训练集和验证集的指标
            train_metrics = eval_model(self.model, train_dataloader, type='train')
            valid_metrics = eval_model(self.model, valid_dataloader, type='valid')
            best_acc = max(best_acc, valid_metrics['valid_acc'])
            
            if best_acc == valid_metrics['valid_acc']:
                best_train_metrics = train_metrics
                best_valid_metrics = valid_metrics
                best_model = copy.deepcopy(self.model)
            
            progress =  (epoch+1) / num_epochs * 100
            self.socketio.emit('training_progress', {'modelName': 'mlp', 'progress': progress})
            # print(f'Epoch [{epoch}/{num_epochs}]')

        best_valid_metrics.update(best_train_metrics)
        self.socketio.emit('model_evaluation', 
                            {'modelName': 'mlp',
                            'metrics': best_valid_metrics
                            })
        # 返回best_iter模型
        return best_model
            


    def save_model(self, model_path):
        torch.save(self.model, model_path)
        self.app.logger.info('model saved')

    def load_model(self, model_path):
        self.model = torch.load(model_path)
        self.app.logger.info('model loaded')

    def predict(self, dataset_path):
        if self.model is None:
            self.app.logger.warning("Model not trained yet. Train the model before making predictions.")
        self.app.logger.info('predicting ... ')
        data = load_dataset(dataset_path)
        data = torch.tensor(data.values, dtype=torch.float32)
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(data)
            # _, predicted = torch.max(outputs.data, 1)
            return outputs