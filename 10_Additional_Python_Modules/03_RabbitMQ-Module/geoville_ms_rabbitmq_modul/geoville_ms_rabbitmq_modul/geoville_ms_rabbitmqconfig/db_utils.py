"""
The geoville_ms_receiver module.

Author:
Samuel Carraro
date:2019-30-10
Version V 19.10.1
"""

import re

from geoville_ms_rabbitmqconfig.config import *
from geoville_ms_database.geoville_ms_database import *


def _msg_key_db(db_ini_file, db_ini_section):
    sql = "SELECT \"name\", \"key\" FROM msgeovilleconfig.message_key"
    result = read_from_database_one_row(sql,
                                        None,
                                        db_ini_file,
                                        db_ini_section,
                                        False)
    key_store = {result[0]: result[1]}

    return key_store


def _msg_queue_db(service, db_ini_file, db_ini_section):
    sql = "SELECT  queue_name, port, host " \
          "FROM msgeovilleconfig.message_queue_config  as a, " \
          "customer.services as b " \
          "WHERE service_name = '" + service + "' and a.service_id " \
                                               "= b.service_id"
    result = read_from_database_one_row(sql,
                                        None,
                                        db_ini_file,
                                        db_ini_section, False)

    return result


def queue_config(service, db_ini_file, db_ini_section):
    key = _msg_key_db(db_ini_file, db_ini_section)
    message_queue_config = _msg_queue_db(service, db_ini_file, db_ini_section)

    host = message_queue_config[2]
    port = str(message_queue_config[1])
    port_int = [int(port) for port in re.findall('\\d+', port)]
    queue_name = message_queue_config[0]

    api_configuration = Configuration(host,
                                      port_int[0],
                                      queue_name,
                                      key.get("message_key"))

    return api_configuration
