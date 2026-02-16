#!/bin/bash

# 安装依赖
pip install -r requirements_web.txt

# 开发环境运行（可从任何IP访问）
python app.py

# 生产环境运行（使用gunicorn）
# gunicorn -w 4 -b 0.0.0.0:5000 app:app
