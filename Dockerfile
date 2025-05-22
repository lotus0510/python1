# 使用官方 Python 3.10 映像
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製必要檔案
COPY requirements.txt requirements.txt
COPY . .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 設定執行 port
ENV PORT=8080

# 啟動 Flask 伺服器
CMD ["python", "app.py"]
