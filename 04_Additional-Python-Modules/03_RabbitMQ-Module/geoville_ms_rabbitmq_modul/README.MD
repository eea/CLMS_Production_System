# Receiver
This GeoVille Microservice module consists of the class BaseReceiver and a Publisher. It provides the basic implementation to receive and publish messages to
the Geoville-RabbitMQ.

## 1. Installation
`pip3 install https://USER:TOKEN@bitbucket.org/geoville/geoville_ms_rabbitmq_modul/get/master.zip`
Note that USER and TOKEN are placeholders and need to get filled with information.

## 2. Usage BaseReceiver
After installing the module, import it with `from geoville_ms_receiver.basereceiver import BaseReceiver`

Implement the BaseReceiver.class and work with the received message in the function callback:
```python
    class Receiver(BaseReceiver):

    def __init__(self, service):
        super().__init__(service)

    def callback(self, ch, method, properties, body):
        message = super().callback(ch, method, properties, body)
        # DO STUFF HERE!
```
Create an instance of your Receiver and listen to the queue:
```python
    receiver = Receiver("service_name")
    receiver.listen()
```

## 3. Usage of Publisher
After installing the module, import it with `from geoville_ms_publisher.publisher import Publisher`

Create an instance of the Publisher class:
```python
    publisher = Publisher("service_name")
    publisher.publish(<<dictionary>>)
```