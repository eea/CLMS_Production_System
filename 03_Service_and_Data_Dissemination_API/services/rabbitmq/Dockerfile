FROM rabbitmq

RUN mkdir ca_certificates

COPY /ca_certificates/server.crt /ca_certificates
COPY /ca_certificates/server.key /ca_certificates
COPY /ca_certificates/root.crt /ca_certificates

RUN rabbitmq-plugins enable --offline rabbitmq_management