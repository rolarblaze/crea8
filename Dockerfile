# Stage 1: Build Stage
FROM python:3.12-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies including Uvicorn
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the rest of the application code and .env file
COPY . .

# Stage 2: Production Stage
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the necessary files from the builder stage
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# Ensure the app can access the installed packages
ENV PATH=/root/.local/bin:$PATH

# Copy the .env file from the builder stage
COPY --from=builder /app/.env .env

# Expose the port that the FastAPI app runs on
EXPOSE 8000

# Command to run the FastAPI app using Uvicorn as the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
