# Step 1: Use an official Python runtime as a parent image
FROM python:3.10-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the requirements file to the container
COPY requirements.txt .

# Step 4: Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the application code to the container
COPY . .

# Step 6: Set the default entry point for the container
# Use the `cli.py` script as the entry point for the container
ENTRYPOINT ["python", "weaviatest.py"]

# Optionally, provide a default command to the entrypoint
# CMD ["--help"]


