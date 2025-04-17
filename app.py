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

# 获取生成频谱图片列表
def get_generated_spectrum_images():
    spectrum_dir = os.path.join(app.root_path, 'data', 'spec', 'gene')
    if not os.path.exists(spectrum_dir):
        os.makedirs(spectrum_dir, exist_ok=True)
    return sorted([f for f in os.listdir(spectrum_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))])

# 获取真实频谱图片列表
def get_real_spectrum_images():
    spectrum_dir = os.path.join(app.root_path, 'data', 'spec', 'real')
    if not os.path.exists(spectrum_dir):
        os.makedirs(spectrum_dir, exist_ok=True)
    return sorted([f for f in os.listdir(spectrum_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))])

@app.route('/spectrum', methods=['GET'])
def spectrum():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # 获取频谱图片列表
    generated_images = get_generated_spectrum_images()
    real_images = get_real_spectrum_images()
    
    # 获取当前显示的图片索引
    generated_index = request.args.get('gen_idx', 0, type=int)
    real_index = request.args.get('real_idx', 0, type=int)
    
    # 获取要显示的频谱类型（生成频谱或真实频谱）
    spectrum_type = request.args.get('type', 'generated')
    if spectrum_type not in ['generated', 'real']:
        spectrum_type = 'generated'
    
    # 确保索引在有效范围内
    if generated_images:
        generated_index = max(0, min(generated_index, len(generated_images) - 1))
        current_generated = generated_images[generated_index]
    else:
        current_generated = None
    
    if real_images:
        real_index = max(0, min(real_index, len(real_images) - 1))
        current_real = real_images[real_index]
    else:
        current_real = None
    
    return render_template('spectrum.html', 
                          title='触觉生成仿真平台',
                          generated_images=generated_images,
                          real_images=real_images,
                          generated_index=generated_index,
                          real_index=real_index,
                          current_generated=current_generated,
                          current_real=current_real,
                          spectrum_type=spectrum_type)

@app.route('/spectrum/image/<path:directory>/<filename>')
def get_spectrum_image(directory, filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return send_from_directory(os.path.join(app.root_path, 'data', 'spec', directory), filename)

# 获取生成信号图片列表
def get_generated_signal_images():
    signal_dir = os.path.join(app.root_path, 'data', 'signal', 'gene')
    if not os.path.exists(signal_dir):
        os.makedirs(signal_dir, exist_ok=True)
    return sorted([f for f in os.listdir(signal_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))])

# 获取真实信号图片列表
def get_real_signal_images():
    signal_dir = os.path.join(app.root_path, 'data', 'signal', 'real')
    if not os.path.exists(signal_dir):
        os.makedirs(signal_dir, exist_ok=True)
    return sorted([f for f in os.listdir(signal_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))])

# 获取信号对比图片列表
def get_compare_signal_images():
    signal_dir = os.path.join(app.root_path, 'data', 'signal', 'compare')
    if not os.path.exists(signal_dir):
        os.makedirs(signal_dir, exist_ok=True)
    return sorted([f for f in os.listdir(signal_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))])

@app.route('/signal_conversion', methods=['GET'])
def signal_conversion():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # 获取信号图片列表
    generated_images = get_generated_signal_images()
    real_images = get_real_signal_images()
    compare_images = get_compare_signal_images()
    
    # 获取当前显示的图片索引
    generated_index = request.args.get('gen_idx', 0, type=int)
    real_index = request.args.get('real_idx', 0, type=int)
    compare_index = request.args.get('comp_idx', 0, type=int)
    
    # 获取要显示的信号类型
    signal_type = request.args.get('type', 'generated')
    if signal_type not in ['generated', 'real', 'compare']:
        signal_type = 'generated'
    
    # 确保索引在有效范围内
    if generated_images:
        generated_index = max(0, min(generated_index, len(generated_images) - 1))
        current_generated = generated_images[generated_index]
    else:
        current_generated = None
    
    if real_images:
        real_index = max(0, min(real_index, len(real_images) - 1))
        current_real = real_images[real_index]
    else:
        current_real = None
        
    if compare_images:
        compare_index = max(0, min(compare_index, len(compare_images) - 1))
        current_compare = compare_images[compare_index]
    else:
        current_compare = None
    
    return render_template('signal_conversion.html', 
                          title='触觉生成仿真平台',
                          generated_images=generated_images,
                          real_images=real_images,
                          compare_images=compare_images,
                          generated_index=generated_index,
                          real_index=real_index,
                          compare_index=compare_index,
                          current_generated=current_generated,
                          current_real=current_real,
                          current_compare=current_compare,
                          signal_type=signal_type)

@app.route('/signal/image/<path:directory>/<filename>')
def get_signal_image(directory, filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return send_from_directory(os.path.join(app.root_path, 'data', 'signal', directory), filename)

if __name__ == '__main__':
    app.run(debug=True)
