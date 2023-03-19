# Use an official Conda runtime as a parent image
FROM continuumio/miniconda3

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Create the environment using environment.yml
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && conda clean -a

# Activate the Conda environment
SHELL ["conda", "run", "-n", "ProgramareConcurentaSiDistribuita", "/bin/bash", "-c"]

# Make port 5001 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV GOOGLE_CLOUD_PROJECT voting-app-381012
ENV PORT 8080

# Run app.py when the container launches
CMD ["conda", "run", "-n", "ProgramareConcurentaSiDistribuita", "python", "app.py"]
