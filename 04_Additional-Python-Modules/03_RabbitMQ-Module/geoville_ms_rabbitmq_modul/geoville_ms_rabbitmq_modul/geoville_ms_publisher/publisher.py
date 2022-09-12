"""
Provides the send-function.

Author:
Samuel Carraro
date:2019-09-12
Version V 19.09
"""

import os
import pika
import json

from cryptography.fernet import Fernet
from geoville_ms_rabbitmqconfig.db_utils import *

# constants
DB_INI_FILE = "DATABASE_CONFIG_FILE"
DB_INI_SECTION = "DATABASE_CONFIG_FILE_SECTION"
RABBIT_MQ_USER = "RABBIT_MQ_USER"
RABBIT_MQ_PASSWORD = "RABBIT_MQ_PASSWORD"
RABBIT_MQ_VHOST = "RABBIT_MQ_VHOST"
PUBLISH_TRIES = 5


class Publisher:
    """
    BaseReceiver must be implemented to receive Data from RabbitMQ
    Following parameters have to be initialized:
        service: Name of the service
    Following parameters are optional:
        delivery_confirmation: flag if the message has to be published
        db_ini_file: pathlocation + name of the database.ini-file
        db_ini_section: the section in the ini-file that has to be used
        rabbit_mq_user: username to logon to the rabbit_mq
        rabbit_mq_pwd: password to logon to the rabbit_mq
        rabbit_mq_vhost: vhost for the rabbit_mq
    """
    _queue_config_name = None
    _queue_config_port = None
    _queue_config_host = None
    _queue_crypto_key = None
    _rabbit_mq_user = None
    _rabbit_mq_pwd = None
    _rabbit_mq_vhost = None
    _channel = None
    _delivery_confirmation = None

    def __init__(self,
                 service,
                 delivery_confirmation=True,
                 db_ini_file=os.environ.get(DB_INI_FILE),
                 db_ini_section=os.environ.get(DB_INI_SECTION),
                 rabbit_mq_user=os.environ.get(RABBIT_MQ_USER),
                 rabbit_mq_pwd=os.environ.get(RABBIT_MQ_PASSWORD),
                 rabbit_mq_vhost=os.environ.get(RABBIT_MQ_VHOST)):
        self._queue_config_name = queue_config(service,
                                               db_ini_file,
                                               db_ini_section).queue_name
        self._queue_config_port = queue_config(service,
                                               db_ini_file,
                                               db_ini_section).queue_port
        self._queue_config_host = queue_config(service,
                                               db_ini_file,
                                               db_ini_section).queue_host
        self._queue_crypto_key = queue_config(service,
                                              db_ini_file,
                                              db_ini_section).message_key
        self._rabbit_mq_user = rabbit_mq_user
        self._rabbit_mq_pwd = rabbit_mq_pwd
        self._rabbit_mq_vhost = rabbit_mq_vhost
        self._delivery_confirmation = delivery_confirmation
        self._channel = self._connect()

    def publish(self, data):
        """
        This function sends a encrypted json to the GeoVille RabbitMQ.

        :param service: The service, which should be used.
        :param data: The json that should be send.
        """

        cipher_suite = Fernet(self._queue_crypto_key)
        cipher_text = cipher_suite.encrypt(bytes(json.dumps(data), "utf-8"))

        if self._delivery_confirmation:
            self._publish(cipher_text, 0)
        else:
            self._channel.basic_publish(exchange="",
                                        routing_key=self._queue_config_name,
                                        body=cipher_text)

    def _publish(self, cipher_text, counter):
        """
        Publishes the message to the queue
        :param cipher_text: data (json)
        :param counter: how many tries of publishing this message
        :return:
        """
        if counter == PUBLISH_TRIES:
            print("'Giving up...")
            # TODO Logging
            return
        try:
            self._channel.basic_publish(exchange="",
                                        routing_key=self._queue_config_name,
                                        body=cipher_text)
        except pika.exceptions.UnroutableError as exc:
            print('ERROR')
            # TODO Logging
            self._publish(cipher_text, counter + 1)

    def _connect(self):
        """
        Connects to the queue and returns the channel
        :return: channel
        """
        credentials = pika.PlainCredentials(self._rabbit_mq_user,
                                            self._rabbit_mq_pwd)

        if self._rabbit_mq_user is None:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(self._queue_config_host,
                                          self._queue_config_port,
                                          self._rabbit_mq_vhost))
        else:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(self._queue_config_host,
                                          self._queue_config_port,
                                          self._rabbit_mq_vhost,
                                          credentials))
        channel = connection.channel()
        channel.queue_declare(queue=self._queue_config_name)

        if self._delivery_confirmation:
            channel.confirm_delivery()

        return channel
