FROM python:3.7

# Set build environment variables coming from the docker-compose env file
ARG GIT_USER
ARG GIT_PW

# Upgrade pip version
RUN /usr/local/bin/python -m pip install --upgrade pip

# Install GEMS modules stored in BitBucket
RUN pip install --upgrade --no-cache-dir https://$GIT_USER:$GIT_PW@bitbucket.org/geoville/geoville_ms_request_check_modul/get/master.zip
RUN pip install --upgrade --no-cache-dir https://$GIT_USER:$GIT_PW@bitbucket.org/geoville/geoville_ms_database_modul/get/master.zip
RUN pip install --upgrade --no-cache-dir https://$GIT_USER:$GIT_PW@bitbucket.org/geoville/geoville_ms_logging_modul/get/master.zip
RUN pip install --upgrade --no-cache-dir https://$GIT_USER:$GIT_PW@bitbucket.org/geoville/geoville_ms_rabbitmq_modul/get/master.zip
RUN pip install --upgrade --no-cache-dir https://$GIT_USER:$GIT_PW@bitbucket.org/geoville/geoville_ms_utils_modul/get/master.zip
RUN pip install --upgrade --no-cache-dir https://$GIT_USER:$GIT_PW@bitbucket.org/geoville/geoville_ms_request_check_modul/get/master.zip

# Copies the requirements file to the Docker image
COPY requirements.txt .

# Install the remaining Python package required
RUN pip install --no-cache-dir -r requirements.txt

# Sets current working directory
WORKDIR /app

# Copies the application code to the current working directory
COPY src/ /app
