"""
The geoville_ms_receiver module.

Author:
Samuel Carraro
date:2019-22-08
Version V 19.08.1
"""


class Configuration:
    def __init__(self, queue_host, queue_port, queue_name, message_key):
        self.queue_host = queue_host
        self.queue_port = queue_port
        self.queue_name = queue_name
        self.message_key = message_key
