# Use standard official slim Python runtime
FROM python:3.11-slim

# Set up operational variables
WORKDIR /workspace

# Copy requirements list
COPY requirements.txt .

# Install python package binaries
RUN pip install --no-cache-dir -r requirements.txt

# Copy source folder structures
COPY . .

# Expose FastAPI listening port
EXPOSE 8000

# Start Uvicorn engine
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
