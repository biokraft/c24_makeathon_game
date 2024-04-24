# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Add the current directory contents into the container at /app
ADD ./shutup_gpt /app
ADD ./.streamlit /app/.streamlit

# Set the working directory in the container to /app
WORKDIR /app

# Install required packages
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run the command to start the Streamlit server
CMD ["poetry", "run", "streamlit", "run", "app.py"]