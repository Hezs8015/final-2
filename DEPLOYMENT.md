# GitHub 部署指南

本指南将帮助您将时间序列预测Web应用部署到GitHub Pages或其他平台。

## 方法一：GitHub Pages (静态部署)

由于GitHub Pages主要支持静态网站，而我们的应用包含Flask后端，推荐使用以下方法：

### 选项A：使用Render.com部署（推荐）

1. **准备代码仓库**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **创建GitHub仓库**
   - 访问 https://github.com/new
   - 创建新仓库
   - 按照GitHub提示推送代码

3. **部署到Render**
   - 访问 https://render.com
   - 注册/登录账号
   - 点击 "New +" -> "Web Service"
   - 连接你的GitHub仓库
   - 配置如下：
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Runtime**: Python 3

4. **获取部署URL**
   - 部署完成后，Render会提供一个公网URL
   - 可以通过这个URL访问你的应用

### 选项B：使用Railway.app部署

1. **准备代码仓库**（同上）

2. **部署到Railway**
   - 访问 https://railway.app
   - 注册/登录账号
   - 点击 "New Project" -> "Deploy from GitHub repo"
   - 选择你的仓库
   - Railway会自动检测Python项目并配置

3. **获取部署URL**
   - 部署完成后，Railway会提供一个公网URL

### 选项C：使用PythonAnywhere部署

1. **注册PythonAnywhere账号**
   - 访问 https://www.pythonanywhere.com
   - 注册免费账号

2. **上传代码**
   - 使用Git或Web界面上传代码
   - 在Bash中运行：
     ```bash
     git clone https://github.com/你的用户名/你的仓库名.git
     cd 你的仓库名
     ```

3. **配置虚拟环境**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.13 myenv
   pip install -r requirements.txt
   ```

4. **配置Web应用**
   - 在PythonAnywhere控制台选择 "Web"
   - 点击 "Add a new web app"
   - 选择 "Flask" 和 "Python 3.13"
   - 配置路径到你的项目目录
   - WSGI配置文件指向 `app.py`

5. **获取部署URL**
   - PythonAnywhere会提供一个类似 `yourname.pythonanywhere.com` 的URL

## 方法二：本地运行 + GitHub代码托管

如果你只需要在GitHub上托管代码，本地运行应用：

1. **推送代码到GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的用户名/你的仓库名.git
   git push -u origin main
   ```

2. **本地运行应用**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

3. **访问应用**
   - 打开浏览器访问 http://localhost:5000

## 方法三：使用Docker部署

### 1. 创建Dockerfile

在项目根目录创建 `Dockerfile`：

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

### 2. 构建Docker镜像

```bash
docker build -t timeseries-prediction .
```

### 3. 运行Docker容器

```bash
docker run -p 5000:5000 timeseries-prediction
```

### 4. 部署到Docker Hub

```bash
docker tag timeseries-prediction 你的用户名/timeseries-prediction
docker push 你的用户名/timeseries-prediction
```

## 环境变量配置

如果需要配置环境变量，在部署平台中设置：

- `FLASK_ENV`: `production`
- `SECRET_KEY`: 你的密钥

## 常见问题

### 1. 端口问题
- 大多数云平台会自动分配端口
- 确保应用监听 `0.0.0.0` 而不是 `127.0.0.1`
- 在 `app.py` 中修改：
  ```python
  if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5000, debug=False)
  ```

### 2. 依赖问题
- 确保 `requirements.txt` 包含所有依赖
- 某些平台可能需要调整依赖版本

### 3. 文件上传大小限制
- 默认限制为16MB
- 如需修改，在 `app.py` 中调整：
  ```python
  app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
  ```

## 推荐部署方案

对于学生作业，推荐使用 **Render.com** 或 **Railway.app**：

✅ **优点**：
- 免费套餐足够使用
- 部署简单，支持GitHub集成
- 提供公网访问URL
- 自动SSL证书

✅ **步骤简单**：
1. 推送代码到GitHub
2. 在部署平台连接GitHub仓库
3. 自动部署完成

## 项目结构检查

确保你的项目包含以下文件：

```
finalexam/
├── app.py                 # Flask应用
├── requirements.txt       # Python依赖
├── Procfile              # 部署配置（可选）
├── runtime.txt           # Python版本（可选）
├── .gitignore            # Git忽略文件
├── README.md             # 项目说明
├── templates/
│   └── index.html        # 前端页面
└── dataset.xlsx          # 示例数据（可选）
```

## 部署检查清单

- [ ] 代码已推送到GitHub
- [ ] requirements.txt 包含所有依赖
- [ ] 应用可以本地运行
- [ ] 没有硬编码的本地路径
- [ ] 端口配置正确（0.0.0.0）
- [ ] 文件上传大小限制合理
- [ ] 已配置.gitignore文件
- [ ] README.md 包含使用说明

## 获取帮助

如果遇到部署问题：

1. 查看部署平台的日志
2. 检查依赖是否正确安装
3. 确认端口配置正确
4. 查看Flask错误信息

祝你部署顺利！🚀