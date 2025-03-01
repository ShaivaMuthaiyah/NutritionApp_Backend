# Use an official Python runtime as a parent image
FROM python:3.9.21-alpine3.21


# Install any needed system dependencies (if required) using `apk`
RUN apk add --no-cache --update \
    bash

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
RUN mkdir -p /app/reports


RUN pip install --upgrade pip --index-url=https://pypi.org/simple --timeout=100

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# atlas URI to connect
ARG MONGO_URI
ENV MONGO_URI=$MONGO_URI

# the name of the bucket being connected to
ARG BUCKET_NAME
ENV BUCKET_NAME=$BUCKET_NAME

# the default region set up for the project
ARG REGION
ENV REGION=$REGION

# url of 3 bucket
ARG BUCKET_URL
ENV BUCKET_URL=$BUCKET_URL

# aws credentials
ARG AWS_ACCESS_KEY
ENV AWS_ACCESS_KEY=$AWS_ACCESS_KEY
ARG AWS_SECRET_KEY
ENV AWS_SECRET_KEY=$AWS_SECRET_KEY


# backend URL
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL


# Expose the port the Flask app runs on
EXPOSE 5000

# Define the command to run the app
CMD ["python", "app.py"]
