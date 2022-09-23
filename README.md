# CLC+ Backbone System
CLC+ Backbone System and Data Dissemination API

## Introduction
This repository provides all components, descriptions, configurations, sources and manuals of the CLC+ backbone system and data dissemination API.

#### 1. Documentation 
Product specification and user manual

#### 2. Authorization API
OAuth2 server based on Python for user authorization

#### 3. Service and Data Dissemination API
The Python based API gateway sits between the client and a collection of backend 
services and serves as the entry point to the microservice infrastructure.
Hence, it communicates with Airflow and triggers the processes that compute and
retrieve the raster and vector products.
The RESTful API accepts all application programming interface (API) calls,
aggregates the various services required to fulfil them, and returns the appropriate result.
Moreover, it provides all endpoints which are required to interact with the system. The endpoints are divided into
namespaces or sections to group common operations (e.g.: geo-services, custom-relation-management
services, etc.). While the endpoints for processes are
within the 'section' namespace, the retrieval of the products is within the 
'products' section of the API.

#### 4. Airflow
Apache Airflow installation and configuration

#### 5. Airflow DAGs
This section contains the source codes of the Airflow Directed Acyclic Graphs (DAGs).
A DAG (Directed Acyclic Graph) is the core concept of Airflow, 
collecting Tasks together, organized with dependencies and relationships 
to say how they should run. To put it in a nutshell, a DAG is a Python based 
workflow description while each Task within this workflow can be a containerized
application (Docker), a Bash Command or simply a Python function.


#### 6. Database
Database DDL files and database models

#### 7. Status Manager
Source code of the status manager service

#### 8. User Interface
The user interface is a _Vue.js_ based frontend for the communication with the service API. 
The single page application (SPA) was developed for the operation of the CLC+ Backbone project. 
Here, various automatic processes as well as manual tasks can be started and 
monitored. While an automatic process is simply the communication with the API that 
in turn triggers an Airflow DAG, manual processes are simply database updates to document
and monitor manual steps. Therefore, replicable products can be ensured.

#### 9. Monitoring & Logging
Grafana dashboards and logging techniques

#### 10. Additional Python Modules
The system architecture also includes helper functions and modules
to avoid duplicated code and a modular microservice infrastructure.  
The modules are:  

* <u>Logging Module</u>  
  The logging module is used to send log message (in form of a dictionary) to a 
  logging queue. All the logs are going to be saved in a database table.  
  
* <u>Database Module</u>  
  This module allows every interaction with a database. This includes reading, 
  writing and updating rows, but also much more.
  
* <u>RabbitMQ Module</u>  
  This microservice module consists of the class BaseReceiver and a Publisher. 
  It provides the basic implementation to receive and publish messages to the RabbitMQ queue.
  
* <u>Storage Module</u>  
  The Python based storage module is used for reading from and writing into netCDF files in various ways.
  Both general geospatial data types; raster and vector data; are supported by this module.
  
* <u>Product Ingestion Code</u>  
  This module serves as utility to upload quality checked CLC+ Backbone 
  products to netCDF files. The product netCDF files will be accessed by the 
  endpoints within the 'products' namespace of the API.

