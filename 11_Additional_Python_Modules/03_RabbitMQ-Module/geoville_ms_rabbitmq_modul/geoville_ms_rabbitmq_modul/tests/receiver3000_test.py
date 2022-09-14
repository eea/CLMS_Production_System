"""
The geoville_ms_receiver test.

Author:
Samuel Carraro
date:2019-28-08
Version V 19.08.2
"""

from geoville_ms_rabbitmq_modul.geoville_ms_receiver.basereceiver import *


class Receiver(BaseReceiver):
    _service = None
    counter = 0

    def __init__(self,
                 service, db_ini_file='database.ini',
                 db_ini_section='postgresql'):
        super().__init__(service, db_ini_file='database.ini',
                 db_ini_section='postgresql',rabbit_mq_user=None)
        self._service = service

    def callback(self, ch, method, properties, body):
        print(self.counter)
        self.counter += 1
        message = super().callback(ch, method, properties, body)
        print(message)



receiver = Receiver("test")
receiver.listen()
