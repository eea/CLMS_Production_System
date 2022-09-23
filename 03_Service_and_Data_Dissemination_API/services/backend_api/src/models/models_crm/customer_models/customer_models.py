########################################################################################################################
#
# Customer models for the Swagger UI
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import crm_namespace as api

########################################################################################################################
# Request model for the POST request
########################################################################################################################

customer_id_model = api.model('customer_id_model',
                              {
                                  'user_id': fields.String(
                                      description='Unique identifier of a customer',
                                      example="8KfYSDj8Wq2iNtIly98M5ES4",
                                      required=True
                                  ),
                              })

########################################################################################################################
# Response model for the POST request
########################################################################################################################

customer_creation_response_model = api.model('customer_creation_response_model',
                                             {
                                                 'client_id': fields.String(
                                                     description='Unique identifier of a customer in OAuth2',
                                                     example='8KfYSDj8Wq2iNtIly98M5ES4'
                                                 ),
                                                 'client_secret': fields.String(
                                                     description='Secret for further authorisation',
                                                     example='ece97e8804fb8239'
                                                 )
                                             })

########################################################################################################################
# Request model for POST and DELETE requests
########################################################################################################################

customer_model = api.model('customer_model',
                           {
                               'title': fields.String(
                                   description='form of address',
                                   required=True,
                                   example='Mr'
                               ),
                               'first_name': fields.String(
                                   description='first name of the customer',
                                   required=True,
                                   example='Max'
                               ),
                               'last_name': fields.String(
                                   description='last name of the customer',
                                   required=True,
                                   example='Mustermann'
                               ),
                               'email': fields.String(
                                   description='e-mail address of the customer',
                                   required=True,
                                   pattern="(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                                   example='max_mustermann@mustermann.de'
                               ),
                               'password': fields.String(
                                   description='e-mail address of the customer',
                                   required=True,
                                   example='ABCD1234'
                               ),
                               'address': fields.String(
                                   description='1st address of the customer',
                                   example='Sparkassenplatz 1',
                                   required=True
                               ),
                               'zip_code': fields.String(
                                   description='zip code of the address',
                                   example='6020',
                                   required=True
                               ),
                               'city': fields.String(
                                   description='city of the customer',
                                   example='Innsbruck',
                                   required=True
                               ),
                               'country': fields.String(
                                   description='country of the customer',
                                   example='Austria',
                                   required=True
                               ),
                               'nationality': fields.String(
                                   description='nationality of the customer',
                                   example='German'
                               ),
                               'phone': fields.String(
                                   description='phone number of the customer',
                                   example='012345',
                                   required=True
                               ),
                               'company_name': fields.String(
                                   description='Company name of the customer',
                                   example='GeoVille GmbH',
                                   required=True
                               ),
                           })

########################################################################################################################
# Request model for POST and DELETE requests
########################################################################################################################

customer_filter_model = api.model('customer_filter_model',
                                  {
                                      'title': fields.String(
                                          description='form of address',
                                          example='Mr'
                                      ),
                                      'first_name': fields.String(
                                          description='first name of the customer',
                                          example='Max'
                                      ),
                                      'last_name': fields.String(
                                          description='last name of the customer',
                                          example='Mustermann'
                                      ),
                                      'email': fields.String(
                                          description='e-mail address of the customer',
                                          pattern="(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                                          example='max_mustermann@mustermann.de'
                                      ),
                                      'address': fields.String(
                                          description='1st address of the customer',
                                          example='Sparkassenplatz 1'
                                      ),
                                      'zip_code': fields.String(
                                          description='zip code of the address',
                                          example='6020'
                                      ),
                                      'city': fields.String(
                                          description='city of the customer',
                                          example='Innsbruck'
                                      ),
                                      'country': fields.String(
                                          description='country of the customer',
                                          example='Austria'
                                      ),
                                      'nationality': fields.String(
                                          description='nationality of the customer',
                                          example='German'
                                      ),
                                      'phone': fields.String(
                                          description='phone number of the customer',
                                          example='012345'
                                      ),
                                      'company_name': fields.String(
                                          description='Company name of the customer',
                                          example='GeoVille GmbH',
                                          required=True
                                      ),
                                  })

########################################################################################################################
# Response model for GET, POST and DELETE requests
########################################################################################################################

customer_list_response_model = api.model('customer_list_response_model',
                                         {
                                             'customers': fields.List(
                                                 fields.Nested(
                                                     customer_filter_model
                                                 )
                                             ),
                                         })
