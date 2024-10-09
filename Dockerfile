# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /code

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    pkg-config \
    libmariadb-dev-compat \
    libmariadb-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /code
COPY . /code

# Upgrade pip before installing requirements
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Collect static files
RUN python manage.py collectstatic --noinput

# Copy entrypoint script into the image
COPY entrypoint.sh /code/entrypoint.sh


RUN chmod +x /code/entrypoint.sh
RUN chown -R www-data:www-data /code/staticfiles && \
    chmod -R 755 /code/staticfiles
# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define the entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]

# Define the command to run your Django project
CMD ["gunicorn", "the_pretoria_local.wsgi:application", "--bind", "0.0.0.0:8000"]
