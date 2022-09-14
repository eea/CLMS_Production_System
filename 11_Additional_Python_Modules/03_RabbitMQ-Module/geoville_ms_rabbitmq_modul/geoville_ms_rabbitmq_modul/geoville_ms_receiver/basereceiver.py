"""
The geoville_ms_receiver module.

Author:
Samuel Carraro
date:2019-10-07
Version V 19.10
"""

# imports
import time
import pika
import json
import abc
import os

from cryptography.fernet import Fernet
from geoville_ms_rabbitmqconfig.db_utils import *

# constants
DB_INI_FILE = "DATABASE_CONFIG_FILE"
DB_INI_SECTION = "DATABASE_CONFIG_FILE_SECTION"
RABBIT_MQ_USER = "RABBIT_MQ_USER"
RABBIT_MQ_PASSWORD = "RABBIT_MQ_PASSWORD"
RABBIT_MQ_VHOST = "RABBIT_MQ_VHOST"


# logic
class BaseReceiver(object, metaclass=abc.ABCMeta):
    """
    BaseReceiver must be implemented to receive Data from RabbitMQ
    Following parameters have to be initialized:
        service: Name of the service
    Following parameters are optional:
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

    def __init__(self,
                 service,
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

    @abc.abstractmethod
    def callback(self, ch, method, properties, body):
        """
        Abstract function that needs to be extended to process the message.
        Decodes and returns the message retrieved.

        :param ch: channel
        :param method: meta information regarding the message delivery
        :param properties: user-defined properties on the message
        :param body: crypted message
        """
        print(type(body))
        print(" [x] Received %r" % body)

        cipher_suite = Fernet(self._queue_crypto_key)

        plain_text = cipher_suite.decrypt(body)
        print(" [x] decrytped %r" % str(plain_text, 'utf-8'))

        geoville_message = json.loads(plain_text)
        return geoville_message

    def listen(self):
        """
        listens to the rabbitMQ channel given by the initialization of the
        BaseReceiver-class.
        """
        while True:
            connection = self._connecting()

            channel = connection.channel()
            channel.queue_declare(queue=self._queue_config_name)
            channel.basic_consume(queue=self._queue_config_name,
                                  on_message_callback=self.callback,
                                  auto_ack=True)
            print(' [*] Waiting for messages. To exit press CTRL+C')
            try:
                channel.start_consuming()
            except pika.exceptions.ConnectionClosed:
                print('Connection closed. Recovering...')
                continue
            except KeyboardInterrupt:
                channel.stop_consuming()

            connection.close()
            break

    def _connecting(self):
        connection = None
        while connection is None or connection.is_closed:
            credentials = pika.PlainCredentials(self._rabbit_mq_user,
                                                self._rabbit_mq_pwd)

            try:
                if self._rabbit_mq_user is None:
                    connection = pika.BlockingConnection(
                        pika.ConnectionParameters(self._queue_config_host,
                                                  self._queue_config_port,
                                                  self._rabbit_mq_vhost))
                else:
                    print(
                        "Connecting to " + self._queue_config_host +
                        " on port " + str(self._queue_config_port))
                    connection = pika.BlockingConnection(
                        pika.ConnectionParameters(self._queue_config_host,
                                                  self._queue_config_port,
                                                  self._rabbit_mq_vhost,
                                                  credentials))
            except pika.exceptions.AMQPConnectionError:
                print('Connection closed. Recovering...')
                time.sleep(10)
                continue
        return connection
