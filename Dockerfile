# Use an official Python runtime as a parent image
FROM python:3.9.21-alpine3.21


# Install any needed system dependencies (if required) using `apk`
RUN apk add --no-cache --update \
    bash

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install --upgrade pip --index-url=https://pypi.org/simple --timeout=100

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt



ARG MONGO_URI
ENV MONGO_URI=$MONGO_URI

# Expose the port the Flask app runs on
EXPOSE 5000

# Define the command to run the app
CMD ["python", "app.py"]
