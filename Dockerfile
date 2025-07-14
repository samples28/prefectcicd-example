# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com  -r requirements.txt

# Copy the rest of the application code
COPY serve_retrieve_github_stars.py .

# Set the command to run your application
CMD ["python", "serve_retrieve_github_stars.py"]
