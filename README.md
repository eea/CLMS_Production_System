# CLC+ Backbone System
CLC+ Backbone System and Data Dissemination API.

*powered by*

![Figure 1:GeoVille Logo](01_Documentation/img/geoville_logo_150.png)

## Introduction
This repository provides all components, descriptions, configurations, sources and manuals of the CLC+ backbone system and data dissemination API.

#### 1. Documentation 
Product specification and user manual.

#### 2. Authorization API
User authentication, authorization and management are based on the OAuth2 framework. It is used to exchange data between client and server through authorization. 
The API of the authorization server provides a set of endpoints which are required to perform common authorization operations and flows. Amongst others, this includes for example creating OAuth clients, user login, access token generation, token validation and the generation of scopes and scope managements.

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
Apache Airflow is a workflow management platform and is used to create data pipelines. This repository provides the configuratin of the airflow instance and the Airflow workers. 

#### 5. Airflow DAGs
This section contains the source codes of the Airflow Directed Acyclic Graphs (DAGs).
A DAG (Directed Acyclic Graph) is the core concept of Airflow, 
collecting Tasks together, organized with dependencies and relationships 
to say how they should run. To put it in a nutshell, a DAG is a Python based 
workflow description while each Task within this workflow can be a containerized
application (Docker), a Bash Command or simply a Python function.


#### 6. Database
Any modern backend solution needs a storage system to store data whilst processing particular tasks. As spatial information will be processed in the project, the tool chosen was a PostgreSQL database server with its extension PostGIS for spatial operations. A relational database model is required to persist the processed information in a structured manner. This directory provides database DDL files and database models.

#### 7. Status Manager
The status manager is responsible for updating the status of each order. Whenever the status of an order changes, the manager sets the according state in the order database. The module is based on Python. The possible states are: RECEIVED, RUNNING, QUEUED, SUCCESS, FAILED. 

#### 8. User Interface
The user interface is a _Vue.js_ based frontend for the communication with the service API. 
The single page application (SPA) was developed for the operation of the CLC+ Backbone project. 
Here, various automatic processes as well as manual tasks can be started and 
monitored. While an automatic process is simply the communication with the API that 
in turn triggers an Airflow DAG, manual processes are simply database updates to document
and monitor manual steps. Therefore, replicable products can be ensured.

#### 9. Monitoring & Logging
The system monitoring is based on the Grafana software. Grafana is a multi-platform analytics and visualization tool. It provides charts, graphs, metrics, logs, traces and for monitoring the health state of a system. 

The logging module is used to log and monitor all relevant messages of the backbone processing system. The moduel T module supports different log levels (INGO, WARNING, ERROR). It's written in Python and the module architecture is based on a message queueing system (RabbitMQ). 

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

#### 11. System Components (third party software licenses)
List of all software modules and their licence models.
