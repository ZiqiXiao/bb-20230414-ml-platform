from .utils import *

def init_model_admin_routes(app, socketio):
    @app.route('/model-admin', methods=['POST', 'GET'])
    def model_admin():
        from app.database import ModelTable
        model_data = ModelTable.query.all()
        return render_template('model_admin.html', model_data=model_data)
    
    @app.route('/delete_model', methods=['POST'])
    def delete_model():
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

    @app.route('/rename_model', methods=['POST'])
    def rename_model():
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
    
    @app.route('/download_template')
    def download_template():
        model_id = request.args.get('model_id')
        from app.database import ModelTable
        model = ModelTable.query.filter_by(id=model_id).first()
        print(model.template_name)
        print(Config.TEMPLATE_FOLDER)
        return send_from_directory(Config.TEMPLATE_FOLDER, model.template_name + '.csv', as_attachment=True)