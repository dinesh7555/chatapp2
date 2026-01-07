# 1️⃣ Base image: Python
FROM python:3.11-slim

# 2️⃣ Set working directory inside container
WORKDIR /app

# 3️⃣ Copy requirements first (for caching)
COPY requirements.txt .

# 4️⃣ Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copy backend code
COPY . .

# 6️⃣ Expose FastAPI port
EXPOSE 8000

# 7️⃣ Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
