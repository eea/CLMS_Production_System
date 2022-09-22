########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Entry point for the status manager script
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Florian Girtler (girtler@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from init.init_env_variables import queue_service_name
from lib.receiver_lib import Receiver


########################################################################################################################
# Entry point for the status manager script
########################################################################################################################

def main():
    """ Main method of the status manager

    This method is the main method of the status manager and the entry point for the script. It creates a receiver
    object for the defined RabbitMQ queue name in the database. The script runs in an endless loop and processes the
    incoming messages.

    """

    receiver = Receiver(queue_service_name)
    receiver.listen()


########################################################################################################################
# Module entry point
########################################################################################################################

if __name__ == "__main__":
    main()
