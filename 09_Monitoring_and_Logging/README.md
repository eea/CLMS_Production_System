# Monitoring and Logging
CLC+ Logger based on Python

---

## Contributors
* Patrick Wolf
* Rafael Reder

## Logging

* Saving log messages to a database
* Reading log messages from a RabbitMQ

### Module description
The geoville_ms_logging_sever reads messages from the logging queue and stores the messages periodically into
a database. In order to interrupt the program, please press CTRL+C. Since the program send data periodically to the
database, the duration_in_sec parameter is required. This parameter specifies how often (in seconds) the saver
sends the data to the database. (e.g. A value of DURATION=60 stores the messages every 60 seconds to the database.)

Please note that the environment variable listed below are required:

    - LOGGER_QUEUE_NAME: Addresses the configuration parameter fields in the database
    - DATABASE_CONFIG_FILE: The filename to the database.ini file
    - DATABASE_CONFIG_FILE_SECTION: The section in the database.ini file which stores the actual configuration parameters
    - RABBIT_MQ_USER: RabbitMQ username
    - RABBIT_MQ_PASSWORD: RabbitMQ username
    - RABBIT_MQ_VHOST: RabbitMQ virtual host

### Dependencies
* GeoVille_MS_RabbitMQ_Modul
* GeoVille_MS_Database_Modul

## Grafana monitoring system configuration
The grafana monitoring configuration files can be imported into a fresh grafana instance to monitor a processing system. A working datasource configuration is required.
