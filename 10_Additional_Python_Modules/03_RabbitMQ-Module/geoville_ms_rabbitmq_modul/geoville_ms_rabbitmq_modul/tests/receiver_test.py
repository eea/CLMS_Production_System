"""
The geoville_ms_receiver test.

Author:
Samuel Carraro
date:2019-28-08
Version V 19.08.2
"""
import unittest

from geoville_ms_rabbitmq_modul.geoville_ms_receiver.basereceiver import *
from geoville_ms_rabbitmq_modul.geoville_ms_publisher.publisher \
    import Publisher

msg = None


class Receiver(BaseReceiver):
    _service = None

    def __init__(self,
                 service):
        super().__init__(service)
        self._service = service

    def callback(self, ch, method, properties, body):
        message = super().callback(ch, method, properties, body)
        print(message)
        global msg
        msg = message
        ch.close()


class TestReceiver(unittest.TestCase):

    receiver = None

    def setUp(self):

        service = "test_receiver"
        with open('test.json') as f:
            data = json.load(f)
        publisher = Publisher(service)
        publisher.publish(data)

        self.receiver = Receiver(service)

    def test_receive(self):
        self.receiver.listen()
        ctrl_msg = r"{'fruit': 'Apple', 'size': 'Large', 'color': 'Red'}"
        self.assertEqual(str(msg), ctrl_msg)
