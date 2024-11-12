# Use a Python 3.11 slim base image
FROM python:3.11-slim

# Install Poetry
RUN pip install poetry

# Set the working directory
WORKDIR /app

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock /app/

# Install dependencies without creating a virtual environment inside the container
RUN poetry config virtualenvs.create false && poetry install --no-root

# Copy the rest of the application to the container
COPY . /app

# Copy the .env file
#COPY .env /app/.env

# Expose the port that the application will use
EXPOSE 8100

# Set the PORT environment variable
ENV PORT=8100

# Command to start the application
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]



