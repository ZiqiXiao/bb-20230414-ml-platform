# Use the official Python 3.9 image
FROM python:3.9-slim

EXPOSE 3030

# Set the working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

# # Copy the requirements.txt file into the container
# COPY requirements.txt .

COPY requirements.txt.template .
RUN echo "$(uname -m)" && \
    if [ "$(uname -m)" = "aarch64" ]; then \
        sed 's|{torch_package}|torch==2.0.0|' requirements.txt.template > requirements.txt; \
    elif [ "$(uname -m)" = "x86_64" ]; then \
        sed 's|{torch_package}|--find-links https://download.pytorch.org/whl/torch_stable.html \n torch==2.0.0+cpu|' requirements.txt.template > requirements.txt; \
    fi

# # Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:3030", "-w", "1", "-k", "eventlet", "ml:app", "-t", "60"]