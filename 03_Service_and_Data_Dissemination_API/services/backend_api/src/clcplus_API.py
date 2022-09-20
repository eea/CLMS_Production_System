########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Flask App entry point
#
# Date created: 01.06.2020
# Date last modified: 07.07.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.07
#
########################################################################################################################


from init.api_constructor import clcplus_api, clcplus_blueprint
from init.app_constructor import app
from init.namespace_constructor import *
from oauth.oauth2 import config_oauth
from resources.resources_auth.create_client.create_client import CreateOAuthClient
from resources.resources_auth.delete_clients.delete_clients import DeleteOAuthClients
from resources.resources_auth.delete_client_by_id.delete_client_by_id import DeleteOAuthClient
from resources.resources_auth.delete_tokens.delete_tokens import DeleteTokens
from resources.resources_auth.delete_tokens_by_id.delete_tokens_by_id import DeleteTokensByID
from resources.resources_auth.get_bearer_token.get_bearer_token import GetBearerToken
from resources.resources_auth.get_clients.get_clients import GetClients
from resources.resources_auth.get_client_by_id.get_client_by_id import GetClientByID
from resources.resources_auth.get_scopes.get_scopes import GetScopes
from resources.resources_auth.get_scope_by_id.get_scope_by_id import GetScopeByID
from resources.resources_auth.login.login import Login
from resources.resources_auth.set_scope_by_id.set_scope_by_id import UpdateScope
from resources.resources_auth.set_token_expiration_time.set_token_expiration_time import UpdateTokenExpirationTime

from resources.resources_config.add_airflow_config.add_airflow_config import AddAirflowConfig
from resources.resources_config.add_queue_config.add_queue_config import AddQueueConfig
from resources.resources_config.delete_airflow_config.delete_airflow_config import DeleteAirflowConfiguration
from resources.resources_config.delete_airflow_config_by_name.delete_airflow_config_by_name import DeleteAirflowConfigByName
from resources.resources_config.delete_queue_config.delete_queue_config import DeleteQueueConfiguration
from resources.resources_config.delete_queue_config_by_id.delete_queue_config_by_id import DeleteQueueByID
from resources.resources_config.delete_queue_config_by_name.delete_queue_config_by_name import DeleteQueueByName
from resources.resources_config.get_airflow_config.get_airflow_config import GetAirflowConfig
from resources.resources_config.get_queue_config.get_queue_config import GetMessageQueueConfig
from resources.resources_config.get_queue_config_by_id.get_queue_config_by_id import GetMessageQueueConfigByID
from resources.resources_config.get_queue_config_by_name.get_queue_config_by_name import GetMessageQueueConfigByName

from resources.resources_rabbitmq.delete_rabbitmq_queue.delete_rabbitmq_queue import DeleteRabbitMQQueue
from resources.resources_rabbitmq.get_rabbitmq_queues.get_rabbitmq_queues import RabbitMQListQueues
from resources.resources_rabbitmq.get_rabbitmq_message_count.get_rabbitmq_message_count import RabbitMQMessageCount
from resources.resources_rabbitmq.get_rabbitmq_server_status.get_rabbitmq_server_status import RabbitMQServerStatus
from resources.resources_rabbitmq.get_rabbitmq_users.get_rabbitmq_users import RabbitMQUsers
from resources.resources_rabbitmq.get_rabbitmq_vhosts.get_rabbitmq_vhosts import RabbitMQVHosts

from resources.resources_crm.create_customer.create_customer import CreateCustomer
from resources.resources_crm.create_service.create_service import CreateService
from resources.resources_crm.delete_all_customers.delete_all_customers import DeleteAllCustomers
from resources.resources_crm.delete_all_services.delete_all_services import DeleteServices
from resources.resources_crm.delete_customer_by_id.delete_customer_by_id import DeleteCustomerById
from resources.resources_crm.delete_customers_by_filter.delete_customers_by_filter import DeleteCustomersByFilter
from resources.resources_crm.delete_service_by_id.delete_service_by_id import DeleteServiceById
from resources.resources_crm.delete_service_by_name.delete_service_by_name import DeleteServiceByName
from resources.resources_crm.get_all_customers.get_all_customers import GetAllCustomers
from resources.resources_crm.get_all_services.get_all_services import GetAllServices
from resources.resources_crm.get_customers_by_filter.get_customers_by_filter import GetCustomersByFilter
from resources.resources_crm.get_customer_by_id.get_customer_by_id import GetCustomerById
from resources.resources_crm.get_service_by_id.get_service_by_id import GetServiceByID
from resources.resources_crm.get_service_by_name.get_service_by_name import GetServiceByName
from resources.resources_crm.get_service_orders.get_service_orders import GetServiceOrders
from resources.resources_crm.get_manual_tasks.get_manual_tasks import GetManualTasks
from resources.resources_crm.get_all_tasks.get_all_tasks import GetAllTasks
from resources.resources_crm.create_manual_task.create_manual_task import CreateManualTask
from resources.resources_crm.update_manual_task.update_manual_task import UpdateManualTask
from resources.resources_crm.update_manual_task_spu.update_manual_task_spu import UpdateManualTaskSPU
from resources.resources_crm.update_manual_task_order_id.update_manual_task_order_id import UpdateManualTaskOrderID

from resources.resources_logging.log_error.log_error import LogError
from resources.resources_logging.log_info.log_info import LogInfo
from resources.resources_logging.log_warning.log_warning import LogWarning

from resources.resources_rois.create_roi.create_roi import CreateROI
from resources.resources_rois.delete_all_rois.delete_all_rois import DeleteAllROIs
from resources.resources_rois.delete_roi_by_id.delete_roi_by_id import DeleteROIByID
from resources.resources_rois.delete_roi_by_user_id.delete_roi_by_user_id import DeleteROIByUserID
from resources.resources_rois.get_all_rois.get_all_rois import GetAllROIs
from resources.resources_rois.get_roi_by_id.get_roi_by_id import GetROIByID
from resources.resources_rois.get_roi_by_user_id.get_roi_by_user_id import GetROIByUserID
from resources.resources_rois.set_roi_attributes_by_id.set_roi_attributes_by_id import UpdateROIAttributes
from resources.resources_rois.update_roi_entity_by_id.update_roi_entity_by_id import UpdateROIEntity

from resources.resources_services.batch_classification_production.batch_classification_production import BatchClassificationProduction
from resources.resources_services.batch_classification_staging.batch_classification_staging import BatchClassificationStaging
from resources.resources_services.batch_classification_test.batch_classification_test import BatchClassificationTest
from resources.resources_services.harmonics.harmonics import Harmonics
from resources.resources_services.retransformation.retransformation import Retransformation
from resources.resources_services.service_order_status.order_status import OrderStatus
from resources.resources_services.task_1_batch_classification.task_1_batch_classification import Task1BatchClassification
from resources.resources_services.task_1_feature_classification.task_1_feature_classification import Task1FeatureCalculation
from resources.resources_services.task_1_reprocessing.task_1_reprocessing import Task1Reprocessing
from resources.resources_services.task_1_reprocessing_test.task_1_reprocessing_test import Task1ReprocessingTest
from resources.resources_services.task_1_stitching.task_1_stitching import Task1Stitching
from resources.resources_services.task_2_apply_model.task_2_apply_model import Task2ApplyModel
from resources.resources_services.task_2_apply_model_fast_lane.task_2_apply_model_fast_lane import Task2ApplyModelFastLane
from resources.resources_services.task_2_feature_calculation.task_2_feature_calculation import Task2FeatureCalculation
from resources.resources_services.vector_class_attribution.vector_class_attribution import VectorClassAttribution

from resources.resources_products.get_product.get_product import Products
from resources.resources_products.nations.nations import Nations
from resources.resources_products.get_national_product.get_national_product import NationalProducts
from resources.resources_products.get_product_europe.get_product_europe import ProductEurope

########################################################################################################################
# Retrieving the API env variable
########################################################################################################################

auth_namespace.add_resource(CreateOAuthClient, '/clients/create')
auth_namespace.add_resource(DeleteOAuthClients, '/clients/delete')
auth_namespace.add_resource(DeleteOAuthClient, '/clients/delete/<client_id>')
auth_namespace.add_resource(DeleteTokens, '/tokens/delete')
auth_namespace.add_resource(DeleteTokensByID, '/tokens/delete/<user_id>')
auth_namespace.add_resource(GetBearerToken, '/get_bearer_token')
auth_namespace.add_resource(GetClients, '/clients')
auth_namespace.add_resource(GetClientByID, '/clients/<user_id>')
auth_namespace.add_resource(GetScopes, '/scopes')
auth_namespace.add_resource(GetScopeByID, '/scopes/<user_id>')
auth_namespace.add_resource(Login, '/login')
auth_namespace.add_resource(UpdateScope, '/scopes/update')
auth_namespace.add_resource(UpdateTokenExpirationTime, '/tokens/update/expirationTime')

config_namespace.add_resource(AddAirflowConfig, '/airflow/create')
config_namespace.add_resource(AddQueueConfig, '/queues/create')
config_namespace.add_resource(DeleteAirflowConfiguration, '/airflow/delete')
config_namespace.add_resource(DeleteAirflowConfigByName, '/airflow/delete/<service_name>')
config_namespace.add_resource(DeleteQueueConfiguration, '/queues/delete')
config_namespace.add_resource(DeleteQueueByID, '/queues/delete/id/<service_id>')
config_namespace.add_resource(DeleteQueueByName, '/queues/delete/name/<queue_name>')
config_namespace.add_resource(GetAirflowConfig, '/airflow')
config_namespace.add_resource(GetMessageQueueConfig, '/queues')
config_namespace.add_resource(GetMessageQueueConfigByID, '/queues/id/<service_id>')
config_namespace.add_resource(GetMessageQueueConfigByName, '/queues/name/<queue_name>')

rabbitmq_namespace.add_resource(DeleteRabbitMQQueue, '/queues/delete/<queue_name>')
rabbitmq_namespace.add_resource(RabbitMQListQueues, '/queues')
rabbitmq_namespace.add_resource(RabbitMQUsers, '/users')
rabbitmq_namespace.add_resource(RabbitMQVHosts, '/virtualHosts')
rabbitmq_namespace.add_resource(RabbitMQMessageCount, '/messageCount/<queue_name>')
rabbitmq_namespace.add_resource(RabbitMQServerStatus, '/serverStatus')

crm_namespace.add_resource(CreateCustomer,  '/users/create')
crm_namespace.add_resource(GetAllCustomers, '/users')
crm_namespace.add_resource(GetCustomersByFilter, '/users/filter')
crm_namespace.add_resource(GetCustomerById, '/users/<user_id>')
crm_namespace.add_resource(DeleteAllCustomers, '/users/delete')
crm_namespace.add_resource(DeleteCustomerById, '/users/delete/<user_id>')
crm_namespace.add_resource(DeleteCustomersByFilter, '/users/delete/filter')
crm_namespace.add_resource(GetAllServices, '/services')
crm_namespace.add_resource(GetServiceByID, '/services/id/<service_id>')
crm_namespace.add_resource(GetServiceByName, '/services/name/<service_name>')
crm_namespace.add_resource(CreateService, '/services/create')
crm_namespace.add_resource(DeleteServices, '/services/delete')
crm_namespace.add_resource(DeleteServiceById, '/services/delete/id/<service_id>')
crm_namespace.add_resource(DeleteServiceByName, '/services/delete/name/<service_name>')
crm_namespace.add_resource(GetServiceOrders, '/services/order_query')
crm_namespace.add_resource(GetManualTasks, '/manual_tasks/task_query')
crm_namespace.add_resource(CreateManualTask,  '/manual_tasks/create')
crm_namespace.add_resource(UpdateManualTask,  '/manual_tasks/update_state')
crm_namespace.add_resource(UpdateManualTaskSPU,  '/manual_tasks/update_spu_state')
crm_namespace.add_resource(UpdateManualTaskOrderID,  '/manual_tasks/update_order_id')
crm_namespace.add_resource(GetAllTasks,  '/manual_tasks')

logging_namespace.add_resource(LogError, '/log_error')
logging_namespace.add_resource(LogInfo, '/log_info')
logging_namespace.add_resource(LogWarning, '/log_warning')

rois_namespace.add_resource(CreateROI, '/create')
rois_namespace.add_resource(DeleteAllROIs, '/delete')
rois_namespace.add_resource(DeleteROIByID, '/delete/id/<roi_id>')
rois_namespace.add_resource(DeleteROIByUserID, '/delete/user/<user_id>')
rois_namespace.add_resource(GetAllROIs, '/')
rois_namespace.add_resource(GetROIByID, '/id/<roi_id>')
rois_namespace.add_resource(GetROIByUserID, '/user/<user_id>')
rois_namespace.add_resource(UpdateROIAttributes, '/update/filter')
rois_namespace.add_resource(UpdateROIEntity, '/update')

service_namespace.add_resource(BatchClassificationProduction, '/batch_classification_production')
service_namespace.add_resource(BatchClassificationStaging, '/batch_classification_staging')
service_namespace.add_resource(BatchClassificationTest, '/batch_classification_test')
service_namespace.add_resource(Harmonics, '/harmonics')
service_namespace.add_resource(OrderStatus, '/order_status/<order_id>')
service_namespace.add_resource(Retransformation, '/retransformation')
service_namespace.add_resource(Task1BatchClassification, '/task1_batch_classification')
service_namespace.add_resource(Task1FeatureCalculation, '/task1_feature_calculation')
service_namespace.add_resource(Task1Reprocessing, '/task1_reprocessing')
service_namespace.add_resource(Task1ReprocessingTest, '/task1_reprocessing_test')
service_namespace.add_resource(Task1Stitching, '/task1_stitching')
service_namespace.add_resource(Task2ApplyModel, '/task2_apply_model')
service_namespace.add_resource(Task2ApplyModelFastLane, '/task2_apply_model_fast_lane')
service_namespace.add_resource(Task2FeatureCalculation, '/task2_feature_calculation')
service_namespace.add_resource(VectorClassAttribution, '/vector_class_attribution')

products_namespace.add_resource(Products, '/get_product')
products_namespace.add_resource(Nations, '/nations')
products_namespace.add_resource(NationalProducts, '/get_national_product')
products_namespace.add_resource(ProductEurope, '/get_product_europe')

########################################################################################################################
# Adding all the required namespaces for internal GeoVille API
########################################################################################################################

clcplus_api.add_namespace(auth_namespace)
clcplus_api.add_namespace(auth_header_namespace)
clcplus_api.add_namespace(general_error_namespace)
clcplus_api.add_namespace(config_namespace)
clcplus_api.add_namespace(crm_namespace)
clcplus_api.add_namespace(logging_namespace)
clcplus_api.add_namespace(rabbitmq_namespace)
clcplus_api.add_namespace(rois_namespace)
clcplus_api.add_namespace(service_namespace)
clcplus_api.add_namespace(products_namespace)

########################################################################################################################
# Configures the Flask app object with the oauth instance running in the background
########################################################################################################################

config_oauth(app)

########################################################################################################################
# Registering the Blueprints of each API version
########################################################################################################################

app.register_blueprint(clcplus_blueprint)

########################################################################################################################
# Run the app in debug mode
########################################################################################################################

# app.run(host=app.config['HOST'], debug=app.config['DEBUG'], port=app.config['PORT'])
