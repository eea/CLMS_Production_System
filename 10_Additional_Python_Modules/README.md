# Additional Python Modules

---

## Contributors
* Johannes Schmid
* Michel Schwandner

## Databse Module
This module abstracts a PostgreSQL database connector and provides several functions to read from and
write into tables. The provided methods are:

 * read one row from a query
 * read all rows from a query
 * read many (a specific number of) rows from a query
 *execute commands such as insert, update, create, drop, delete, etc

---

## Logging Module
The logging module is a Python module which simplifies logging from within Python code. It takes the log
messages, including the log level, and sends them to the logging queue (RabbitMQ). This module helps to
simplify the code, as it does not require communication with the logging API via HTTP. To send messages to
the queue, the RabbitMQ module described here further below is used.


---

## RabbitMQ Module
This Python module provides the basic implementation to retrieve messages from and publish messages to
RabbitMQ queues. It consists of the classes BaseReceiver and Publisher. The Publisher makes it very simple
to send a message to a queue, as can be identified by its name. A message can be everything from a string to
a number to a more complex object like a dictionary. The BaseReceiver on the other hand can listen to a
queue and retrieve messages whenever there are some in the queue

---

## Storage Gate Module
TODO ...