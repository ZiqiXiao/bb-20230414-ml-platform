import os
from datetime import datetime
import pandas as pd
import importlib
from config import Config
import time
import traceback

def train_scheduler(
        app: object, 
        filename:str,
        model_class:list[str], 
        model_dict:dict[str], 
        label: str = None, 
        param: dict = {}, 
        socketio: object = None):
    """Schedule the training process for the given model class and customized parameters 
    and return the trained model in a dictionary which also includes the headers of the 
    uploaded data as the templates for further usage. 

    Args:
        app (object):  The instance of the Flask App.
        filename (str): The name of uploaded file.
        model_class (list[str]): The class of chosen model.
        model_dict (dict[str]): The dictionary of models.
        label (str, optional): The name of target column. Defaults to None.
        param (dict, optional): The customized parameters. Defaults to empty dictionary {}.
        socketio (object, optional): The instance of socketio. Defaults to None.

    Returns:
        _type_: _description_
    """        
    # 将表中的表头读取下来作为模板，用于后续的预测。不包含label
    header = pd.read_csv(os.path.join(Config.UPLOAD_TRAIN_FOLDER, filename), nrows=0).drop(label, axis=1)
    model_dict['template'] = header
    # 训练模型
    for m in model_class:
        socketio.emit('start-training', {'modelName': m})
        # time.sleep(1)
        custom_param = param.get(m, {})
        model = training(app, filename, m, label, custom_param, socketio)

        model_dict[m] = model

    socketio.emit('training-finished')
    return model_dict


def training(app, filename, model_class, label='label', param={}, socketio=None):
    app.logger.info(f"Training {model_class} model with {filename} dataset and label {label}")
    # Load the dataset from the uploaded file
    dataset_path = os.path.join(Config.UPLOAD_TRAIN_FOLDER, filename)

    # Load the specified model module
    model_module_name = Config.MODEL_STRUCTURE[model_class]
    model_module = importlib.import_module(model_module_name)

    # Initialize the model
    model = model_module.Model(app=app, socketio=socketio)

    # Train the model
    try:
        model_file = model.train(dataset_path, label, custom_params=param)
    except Exception as e:
        app.logger.error(f"Training Error: {str(e)}\n{traceback.format_exc()}")
        socketio.emit('training_log', {'message': f'Error: {str(e)}\n{traceback.format_exc()}'})
        return

    app.logger.info(f"Training Success")
    return model_file


def predict(app, filename, model_class, model_name, model_path, socketio=None):
    # Load the dataset from the uploaded file
    dataset_path = os.path.join(Config.UPLOAD_PREDICT_FOLDER, filename)

    # Load the specified model module
    model_module_name = Config.MODEL_STRUCTURE[model_class]
    model_module = importlib.import_module(model_module_name)

    # Initialize the model
    model = model_module.Model(app=app, socketio=socketio)
    # Load the trained model
    model.load_model(model_path)
    # Predict
    try:
        result = model.predict(dataset_path)
    except Exception as e:
        app.logger.error(f"Predict Error: {str(e)}\n{traceback.format_exc()}")
        socketio.emit('training_log', {'message': f'Error: {str(e)}\n{traceback.format_exc()}'})
        return
    
    app.logger.info(f"Predict Success")

    result = pd.DataFrame(result, columns=['prediction'])
    # Save the result to the server
    save_filename = f'{datetime.now().strftime("%Y%m%d%H%M%S")}-{filename.split(".")[0]}.csv'
    result_path = os.path.join(Config.PREDICT_RESULT_FOLDER, save_filename)
    result.to_csv(result_path, index=False)

    socketio.emit('training_log', {'message': '预测成功', 'result_path': save_filename})