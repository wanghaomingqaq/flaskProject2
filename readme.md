# 触觉生成仿真平台

这是一个基于Flask的Web应用，提供了用户注册和登录功能。

## 功能特性

1. 用户注册页面
2. 用户登录界面
3. 登录和注册页面之间可以相互切换
4. 网站标题为"触觉生成仿真平台"

## 项目结构

```
flaskProject2/
├── app.py                 # Flask应用主文件
├── static/                # 静态资源文件夹
│   └── css/
│       └── style.css      # 自定义CSS样式
├── templates/             # HTML模板文件夹
│   ├── layout.html        # 基础布局模板
│   ├── login.html         # 登录页面
│   ├── register.html      # 注册页面
│   └── dashboard.html     # 仪表盘页面
└── README.md              # 项目说明文档
```

## 安装和运行

1. 确保您已安装Python 3.7+和pip

2. 安装所需的依赖：
   ```
   pip install flask
   ```

3. 运行应用：
   ```
   python app.py
   ```

4. 在浏览器中访问：
   ```
   http://127.0.0.1:5000/
   ```

## 注意事项

- 本项目使用内存存储用户信息，重启应用后所有数据将丢失。实际项目中应使用数据库来存储用户信息。
- 为了安全起见，在生产环境中应更改secret_key，并使用更安全的会话管理方式。