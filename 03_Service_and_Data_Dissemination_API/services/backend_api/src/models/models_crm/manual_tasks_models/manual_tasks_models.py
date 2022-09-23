########################################################################################################################
#
# Service models for the Swagger UI
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from datetime import datetime
from flask_restx import fields
from init.namespace_constructor import crm_namespace as api

########################################################################################################################
# Request model for the POST request
########################################################################################################################

manual_task_request_model = api.model('manual_task_request_model',
                                      {
                                          'processing_unit': fields.List(
                                              fields.String,
                                              description='Unique identifier of a cell',
                                              example=['10kmE108N256', '10kmE109N257'],
                                              required=False
                                          ),
                                          'subproduction_unit': fields.List(
                                              fields.String,
                                              description='Unique identifier of a cell',
                                              example=['64', '118'],
                                              required=False
                                          ),
                                          'task_id': fields.String(
                                              description='Unique identifier of the manual task',
                                              example='12345',
                                              required=True
                                          ),
                                          'service_id': fields.String(
                                              description='Unique identifier of the service',
                                              example='046ab5de45ca923bb276f877845642a156d9589bf500bcf2756e3f38da0839fe',
                                              required=True

                                          ),

                                          # 'status': fields.String(
                                          #     description='Status of the manual task',
                                          #     example='TODO',
                                          #     required=True
                                          # ),
                                          # 'result': fields.String(
                                          #     description='Result of the manual task',
                                          #     example='test'
                                          # ),
                                          # 'comment': fields.String(
                                          #     description='Comment for the manual task',
                                          #     example='0259bc74928c7bf958be38c767c30ac57da4f9b543dc351ad1456df28014c992'
                                          # ),
                                          #'refers_to_order_id': fields.Integer(
                                          #    description='Order-ID which is connected to the manual task',
                                          #    example='4a34a348500d7f3e799b3095df994602'
                                          # ),

                                          'client_id': fields.String(
                                              description='Unique identifier of a customer in OAuth2',
                                              example='S6aIHB1NOSbaj1ghq99pXq9a',
                                              required=True
                                          ),
                                      })

########################################################################################################################
# Hypermedia manual task model
########################################################################################################################

hypermedia_model = api.model('hypermedia_model',
                             {
                                 'href': fields.String(
                                     description='URI to linked resource',
                                     example='/crm/manual_tasks/task_query?processing_unit=<processing_unit>'
                                 ),
                                 'rel': fields.String(
                                     description='Linked resource',
                                     example='manual_tasks'
                                 ),
                                 'type': fields.String(
                                     description='Type of HTTP method',
                                     example='GET'
                                 )
                             })

########################################################################################################################
# Response model for the POST request
########################################################################################################################

manual_task_response_model = api.model('manual_task_response_model',
                                         {
                                             'message': fields.String(
                                                 description='Success message',
                                                 example='Manual task successfully created'
                                             ),
                                             'links': fields.Nested(
                                                 hypermedia_model,
                                                 description='Hypermedia model'
                                             )
                                         })

########################################################################################################################
# Object model for the get_all_services GET request
########################################################################################################################

task_query_model = api.model('task_query_model',
                             {
                                 'subproduction_unit': fields.String(
                                         description='Unique identifier of a sub-production unit',
                                         example='1_2'
                                     ),
                                 'processing_unit': fields.String(
                                     description='Unique identifier of a processing unit',
                                     example='10kmE108N256'
                                 ),
                                 'service_name': fields.String(
                                     description='Unique name of a service',
                                     example='service_name'
                                 ),
                                 'order_status': fields.String(
                                     description='Status of an order',
                                     example='order status'
                                 ),
                                 'order_id': fields.String(
                                     description='Unique identifier of an order',
                                     example='2bfedd049fb5cff841e4965fabbeec46'
                                 ),
                                 'task_name': fields.String(
                                     description='Unique name of a manual task',
                                     example='task_name'
                                 ),
                                 'task_status': fields.String(
                                     description='Status of a manual task',
                                     example='task status'
                                 ),
                                 'task_result': fields.String(
                                     description='Result of a manual task',
                                     example='task result'
                                 )

                             })

task_object_model = api.model('task_object_model',
                                 {
                                     'task_id': fields.String(
                                         description='Unique identifier of a service',
                                         example='a798a06534046dadfac995b3f3806122317dba4391022a1f9296b911b789f344'
                                     ),
                                     'task_name': fields.String(
                                         description='Unique name of a service',
                                         example='service_name'
                                     ),
                                     'task_comment': fields.String(
                                         description='Description of what the service offers',
                                         example='The service calculates...'
                                     ),
                                     'task_validity': fields.Boolean(
                                         description='Indicator if the service is active',
                                         example=True
                                     ),
                                     'task_owner': fields.String(
                                         description='Responsible person within GeoVille',
                                         example='IT-Services'
                                     ),
                                     'external': fields.Boolean(
                                         description='Internal or external service',
                                         example=True
                                     ),
                                     'date_of_creation': fields.DateTime(
                                         description='Date of creation of the service',
                                         example=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                                     ),
                                     'order_id_not_required': fields.DateTime(
                                         description='False, if manual task is based on a service result',
                                         example=True
                                     )
                                 })

########################################################################################################################
# Response model for the get_all_services GET request
########################################################################################################################

task_list_model = api.model('task_list_model',
                               {
                                   'tasks': fields.List(fields.Nested(
                                       task_object_model,
                                       description='Detailed task information')
                                   ),
                               })

task_query_list_model = api.model('task_query_list_model',
                                  {
                                      'tasks': fields.List(fields.Nested(
                                          task_query_model,
                                          description='Detailed query information')
                                      ),
                                  })

########################################################################################################################
# Request model for updating a task (state and result)
########################################################################################################################


manual_task_update_model = api.model('manual_task_update_model',
                                  {
                                      'state': fields.String(
                                          description='Task state',
                                          example='finished',
                                          required=True
                                      ),
                                      'result': fields.String(
                                          description='Result path of the task (allowed states: not_started, '
                                                      'in_progress, failed, finished) ',
                                          example='/results/result_12345.tif',
                                          required=False
                                      ),
                                      'processing_unit': fields.String(
                                          description='Unique identifier of a processing unit',
                                          example='10kmE108N256',
                                          required=True
                                      ),
                                      'service_id': fields.String(
                                          description='Unique id of a service',
                                          example='0259bc74928c7bf958be38c767c30ac57da4f9b543dc351ad1456df28014c992',
                                          required=True
                                      ),
                                      'task_id': fields.String(
                                          description='Unique id of a task',
                                          example='12345',
                                          required=True
                                      ),
                                      'client_id': fields.String(
                                          description='Unique identifier of a customer in OAuth2',
                                          example='S6aIHB1NOSbaj1ghq99pXq9a',
                                          required=False
                                      ),
                                  })

########################################################################################################################
# Request model for updating a task (state and result) based on SPU
########################################################################################################################


manual_task_update_spu_model = api.model('manual_task_update_spu_model',
                                  {
                                      'state': fields.String(
                                          description='Task state',
                                          example='finished',
                                          required=True
                                      ),
                                      'result': fields.String(
                                          description='Result path of the task (allowed states: not_started, '
                                                      'in_progress, failed, finished) ',
                                          example='/results/result_12345.tif',
                                          required=False
                                      ),
                                      'subproduction_unit': fields.String(
                                          description='Unique identifier of a subproduction unit',
                                          example='123',
                                          required=True
                                      ),
                                      'service_id': fields.String(
                                          description='Unique id of a service',
                                          example='0259bc74928c7bf958be38c767c30ac57da4f9b543dc351ad1456df28014c992',
                                          required=True
                                      ),
                                      'task_id': fields.String(
                                          description='Unique id of a task',
                                          example='12345',
                                          required=True
                                      ),
                                      'client_id': fields.String(
                                          description='Unique identifier of a customer in OAuth2',
                                          example='S6aIHB1NOSbaj1ghq99pXq9a',
                                          required=False
                                      ),
                                  })

########################################################################################################################
# Request model for updating the order_id
########################################################################################################################

manual_task_update_order_id_model = api.model('manual_task_update_order_id_model',
                                  {
                                      'refers_to_order_id': fields.String(
                                          description='Order-ID',
                                          example='035f4fc8b82544666c97357551441e32',
                                          required=True
                                      ),
                                      'processing_unit': fields.String(
                                          description='Unique identifier of a processing unit',
                                          example='10kmE108N256',
                                          required=True
                                      ),
                                      'service_id': fields.String(
                                          description='Unique id of a service',
                                          example='0259bc74928c7bf958be38c767c30ac57da4f9b543dc351ad1456df28014c992',
                                          required=True
                                      ),
                                      'task_id': fields.String(
                                          description='Unique id of a task',
                                          example='12345',
                                          required=True
                                      ),
                                      'client_id': fields.String(
                                          description='Unique identifier of a customer in OAuth2',
                                          example='S6aIHB1NOSbaj1ghq99pXq9a',
                                          required=False
                                      ),
                                  })

########################################################################################################################
# Response model for the PUT request (/crm/manual_tasks/update_order_id)
########################################################################################################################

manual_task__update_order_id_response_model = api.model('manual_task__update_order_id_response_model',
                                         {
                                             'message': fields.String(
                                                 description='Success message',
                                                 example='Your update has been successfully submitted'
                                             ),
                                             'refers_to_order_id': fields.String(
                                                 description='Order-ID',
                                                 example='92d32e1fbda9957138d6dde42d064a12'
                                             ),

                                         })

########################################################################################################################
# Response model for the PUT request (/crm/manual_tasks/update_state)
########################################################################################################################

manual_task_update_state_response_model = api.model('manual_task_update_state_response_model',
                                         {
                                             'message': fields.String(
                                                 description='Success message',
                                                 example='Your update has been successfully submitted'
                                             )
                                         })