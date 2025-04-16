from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import os
from os.path import isfile, join

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 简单的用户数据存储，实际项目中应该使用数据库
users = {}

# 获取data目录下的所有图片文件
def get_image_files():
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    image_files = [f for f in os.listdir(data_dir) if isfile(join(data_dir, f)) and 
                 f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    return sorted(image_files)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            flash('登录成功！')
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误！')
    
    return render_template('login.html', title='触觉生成仿真平台')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if username in users:
            flash('用户名已存在！')
        elif password != confirm_password:
            flash('两次输入的密码不一致！')
        else:
            users[username] = generate_password_hash(password)
            flash('注册成功，请登录！')
            return redirect(url_for('login'))
    
    return render_template('register.html', title='触觉生成仿真平台')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', title='触觉生成仿真平台', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# 新增功能路由
@app.route('/data_view')
def data_view():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    image_files = get_image_files()
    
    return render_template('data_view.html', 
                          title='数据查看 - 触觉生成仿真平台', 
                          username=session['username'],
                          image_files=image_files,
                          total_images=len(image_files))

@app.route('/get_image/<int:index>')
def get_image(index):
    if 'username' not in session:
        return jsonify({'error': '未登录'}), 401
    
    image_files = get_image_files()
    
    if not image_files:
        return jsonify({'error': '没有图片'}), 404
    
    total_images = len(image_files)
    
    # 确保索引在有效范围内
    index = index % total_images if total_images > 0 else 0
    
    return jsonify({
        'image_url': url_for('data_image', filename=image_files[index]),
        'current_index': index,
        'total_images': total_images,
        'filename': image_files[index]
    })

# 为data目录中的图片提供静态文件服务
@app.route('/data_image/<path:filename>')
def data_image(filename):
    return send_from_directory(os.path.join(app.root_path, 'data'), filename)

@app.route('/training', methods=['GET', 'POST'])
def training():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # 获取表单数据
        dataset = request.form.get('dataset')
        model_type = request.form.get('model_type')
        epochs = request.form.get('epochs')
        learning_rate = request.form.get('learning_rate')
        batch_size = request.form.get('batch_size')
        optimizer = request.form.get('optimizer')
        use_gpu = 'use_gpu' in request.form
        validation_split = request.form.get('validation_split')
        early_stopping = request.form.get('early_stopping')
        
        # 显示训练配置信息
        flash(f'开始训练模型: 数据集={dataset}, 模型={model_type}, 轮次={epochs}, 学习率={learning_rate}')
        flash('训练已提交，请稍后查看结果')
        
        # 实际项目中，这里会将任务提交到后台进行训练
        # 这里仅作演示，直接返回成功消息
        
        return render_template('training.html', title='触觉生成仿真平台', 
                               training_submitted=True,
                               training_config={
                                   'dataset': dataset,
                                   'model_type': model_type,
                                   'epochs': epochs,
                                   'learning_rate': learning_rate,
                                   'batch_size': batch_size,
                                   'optimizer': optimizer,
                                   'use_gpu': use_gpu,
                                   'validation_split': validation_split,
                                   'early_stopping': early_stopping
                               })
    
    return render_template('training.html', title='触觉生成仿真平台')

@app.route('/spectrum')
def spectrum():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('spectrum.html', title='频谱生成 - 触觉生成仿真平台', username=session['username'])

@app.route('/signal_conversion')
def signal_conversion():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('signal_conversion.html', title='信号转换 - 触觉生成仿真平台', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)
