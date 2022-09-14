FROM postgis/postgis:12-master

RUN mkdir ca_certificates
COPY /ca_certificates/server.crt /ca_certificates
COPY /ca_certificates/server.key /ca_certificates
COPY /ca_certificates/root.crt /ca_certificates

RUN chmod 400 /ca_certificates/*
RUN chown postgres:postgres /ca_certificates/*