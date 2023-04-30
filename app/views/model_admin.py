from .utils import *

def init_model_admin_routes(app: object, socketio: object):
    """Initiation of model management page routes.

    Args:
        app (object): The instance of flask app.
        socketio (object): The instance of socket.
    """    
    @app.route('/model-admin', methods=['POST', 'GET'])
    def model_admin():
        return model_admin_route()    
    
    @app.route('/delete-model', methods=['POST'])
    def delete_model():
        return delete_model_route(app, socketio)

    @app.route('/rename-model', methods=['POST'])
    def rename_model():
        return rename_model_route()
    
    @app.route('/download-template', methods=['GET'])
    def download_template():
        return download_template_route()
    

def model_admin_route():
    """Query all the data in the model database then pass to the model management template.

    Route:
        - GET, POST: /model-admin

    Returns:
        Return the template of the model management page.
    """        
    from app.database import ModelTable
    model_data = ModelTable.query.all()
    return render_template('model_admin.html', model_data=model_data)

def delete_model_route(app: object, socketio: object):
    """The function of delete the model from both the database and the directory.
    And return the status of the operation to the frontend.

    Route:
        - POST: /delete-model

    Args:
        app (object): The instance of flask app.
        socketio (object): The instance of socket.

    Returns:
        json: Return the json of the status if operation is success or failure.
    """
    try:
        model_id = request.form['model_id']
        from app.database import ModelTable
        from app import db
        model = ModelTable.query.filter_by(id=model_id).first()

        # 删除文件
        os.remove(model.model_path)
        os.remove(model.template_path)

        # 从数据库中删除记录
        db.session.delete(model)
        db.session.commit()

        return jsonify(status='success')
    except Exception as e:
        app.logger.warning(f"Warning: {str(e)}\n{traceback.format_exc()}")
        return jsonify(status='failure')
    
def rename_model_route():
    """The function of rename the model in both the database and the directory.
    And return the status of the operation to the frontend.

    Route:
        - POST: /rename-model

    Returns:
        json: Return the json of the status if operation is success or failure.
    """        
    model_id = request.form['model_id']
    new_name = request.form['new_name']

    from app.database import ModelTable
    from app import db
    model = ModelTable.query.filter_by(id=model_id).first()

    # 检查新名称是否已经存在
    existing_model = ModelTable.query.filter_by(model_name=new_name).first()
    if existing_model:
        # 如果存在重名模型，返回错误消息
        return jsonify(status='failure', message='Model name already exists.')

    # 更改实际文件的名称
    old_path = model.model_path
    directory, filename = os.path.split(old_path)
    file_ext = os.path.splitext(filename)[1]
    new_path = os.path.join(directory, f"{new_name}{file_ext}")
    os.rename(old_path, new_path)

    # 更新数据库中的记录
    model.model_name = new_name
    model.model_path = new_path
    db.session.commit()

    return jsonify(status='success')

def download_template_route():
    """The function of download the template file.

    Route:
        - GET: /download-template

    Returns:
        file: Return the template file.
    """        
    model_id = request.args.get('model_id')
    from app.database import ModelTable
    model = ModelTable.query.filter_by(id=model_id).first()
    print(model.template_name)
    print(Config.TEMPLATE_FOLDER)
    return send_from_directory(Config.TEMPLATE_FOLDER, model.template_name + '.csv', as_attachment=True)
