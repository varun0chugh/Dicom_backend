# Use Python's official image as a base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt to the container
COPY requirements.txt ./

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose the port that the Flask app will run on
EXPOSE 5000

# Set the entry point to run the Flask app
CMD ["python", "app.py"]
