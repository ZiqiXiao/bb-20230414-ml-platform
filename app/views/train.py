from .utils import *


def init_train_routes(app, socketio):
    init_utils(app, socketio)

    # Page for uploading the training data， and selecting the model
    @app.route('/train-prepare', methods=['GET', 'POST'])
    def train_prepare():
        if request.method == 'POST':
            # 获取上传的文件名称、模型类别、标签
            filename = request.form['filename']
            modelClass = request.form['modelClass']
            label = request.form['label']
            param = request.form['param']

            redirect_url = url_for('train_progress', filename=filename, modelClass=modelClass, label=label, param=param)
            return jsonify({"redirect_url": redirect_url})
        return render_template('train_prepare.html')
    
    @app.route('/check_label', methods=['POST'])
    def check_label():
        filename = request.form['filename']
        label = request.form['label']

        file_path = os.path.join(Config.UPLOAD_TRAIN_FOLDER, filename)
        df = pd.read_csv(file_path)

        if label in df.columns:
            app.logger.info(f"Label check passed: {label}")
            return jsonify(status='success')
        else:
            app.logger.warning(f"Label check failed: {label}")
            return jsonify(status='failure')
        
    # Page for monitoring the training progress
    @app.route('/train-progress', methods=['POST', 'GET'])
    def train_progress():
        try:
            if request.method == 'POST':
                # Check if the uploaded file is allowed
                filename = secure_filename(request.files['file'].filename)
                modelClass = request.form['modelClass']
                label = request.form['label']
                param = request.form['param']
            elif request.method == 'GET':
                filename = request.args.get('filename')
                modelClass = request.args.get('modelClass')
                label = request.args.get('label')
                param = request.args.get('param')
            return render_template('train_progress.html', filename=filename, modelClass=modelClass, label=label, param=param)
        except Exception as e:
            app.logger.error(f"Exception occurred: {str(e)}\n{traceback.format_exc()}")
    
    # socketio event handler for starting the training process
    @socketio.on('start-training')
    def handle_start_training(data):
        try:
            global trained_models
            trained_models = {}

            app.logger.info(f"Received training request: {data}")

            filename = data['filename']
            modelClass = data['modelClass'].split(',')
            label = data['label']
            param = json.loads(data['param'].replace('&#34;', '\"'))
            print(type(param))
            print(param)

            thread = threading.Thread(target=train_scheduler, args=(app, filename, modelClass, trained_models, label, param, socketio))
            thread.start()
            thread.join()
        except Exception as e:
            app.logger.error(f"Exception occurred: {str(e)}\n{traceback.format_exc()}")

    @app.route('/save_model', methods=['POST'])
    def save_model():
        try:
            selected_model = request.form['selectedModel']
            model_name = request.form['modelName']
            template_name = request.form['templateName']

            # 从已训练的模型中获取选择的模型
            model_module = importlib.import_module(Config.MODEL_STRUCTURE[selected_model])
            trained_model = trained_models[selected_model]
            # Initialize the model
            model = model_module.Model(model=trained_model, app=app, socketio=socketio)

            if model:
                # 保存模型
                save_path = os.path.join(Config.MODEL_FOLDER, selected_model, f'{model_name}.model')
                model.save_model(save_path)
                # 保存模板
                template_path = os.path.join(Config.TEMPLATE_FOLDER, f'{template_name}.csv')
                trained_models['template'].to_csv(template_path, index=False)

                with app.app_context():
                    # Save the model to the database
                    from app.database import ModelTable
                    from app import db
                    model_table = ModelTable(
                        model_class=selected_model, 
                        model_name=model_name,
                        model_path=save_path,
                        template_name=template_name,
                        template_path=template_path
                        )
                    db.session.add(model_table)
                    db.session.commit()
                return jsonify(status='success')
            else:
                return jsonify(status='failure')
        except Exception as e:
            app.logger.error(f"Exception occurred: {str(e)}\n{traceback.format_exc()}")
        
    # 检查模型名称和模板名称是否已存在
    @app.route('/check_name', methods=['POST'])
    def check_name():
        if request.form['modelName']:
            model_name = request.form['modelName']
            with app.app_context():
                from app.database import ModelTable
                model_table = ModelTable.query.filter_by(model_name=model_name).first()
                if model_table:
                    return jsonify(status='failure')
                else:
                    return jsonify(status='success')
                
        elif request.form['templateName']:
            template_name = request.form['templateName']
            with app.app_context():
                from app.database import ModelTable
                template_table = ModelTable.query.filter_by(template_name=template_name).first()
                if template_table:
                    return jsonify(status='failure')
                else:
                    return jsonify(status='success')
                

    @app.route('/model-params-default', methods=['GET'])
    def model_params_default():
        try:
            return jsonify(Config.DEFAULT_PARAMS)
        except Exception as e:
            app.logger.error(f"Exception occurred: {str(e)}\n{traceback.format_exc()}")