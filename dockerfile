# Use official slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Expose Streamlit default port
EXPOSE 8080

# Streamlit launch command
CMD ["streamlit", "run", "src/app.py", "--server.port=8080", "--server.address=0.0.0.0"]
