# ---- Builder Stage ----
# This stage installs dependencies into a virtual environment.
FROM python:3.12-slim AS builder

# Prevent pip from complaining about being run as root
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

# Create a virtual environment to isolate dependencies
RUN python -m venv /opt/venv

# Activate the virtual environment for subsequent commands
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the requirements file to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies into the virtual environment
RUN pip install --no-cache-dir -r requirements.txt


# ---- Final Stage ----
# This stage creates the final, lean production image.
FROM python:3.12-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code
COPY serve_retrieve_github_stars.py .

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Set environment variables for the application
ENV PYTHONUNBUFFERED=1 \
    PREFECT_LOGGING_LEVEL=INFO

# The command to run the application, pointing to the correct file
CMD ["python", "serve_retrieve_github_stars.py"]
