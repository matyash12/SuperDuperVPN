# Use the official Python image as the base image
FROM python:3.11.4-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY docker/django/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project code into the container
COPY . /app/

# Expose the port your Django app will run on
EXPOSE 8000

ADD docker/django/start.sh /
RUN chmod +x /start.sh
CMD ["/start.sh"]

#Makemigrations
#RUN python mysite/manage.py makemigrations
#migrate
#RUN python mysite/manage.py migrate

# Start the Django development server
#CMD ["python", "mysite/manage.py", "runserver", "0.0.0.0:8000"]