########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Vector class attribution API call
#
# Date created: 15.04.2021
# Date last modified: 15.04.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.04
#
########################################################################################################################

from error_classes.http_error_400.http_error_400 import BadRequestError
from error_classes.http_error_404.http_error_404 import NotFoundError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import execute_database
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from geoville_ms_orderid_generator.generator import generate_orderid
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import service_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_service_name_existence, check_user_existence, get_service_id
from lib.general_helper_methods import publish_to_queue
from models.general_models.general_models import service_success_response_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_404 import error_404_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from models.models_services.vector_class_attribution.vector_class_attribution_model import \
    vector_class_attribution_request_model
from oauth.oauth2 import require_oauth
import json
import traceback


########################################################################################################################
# Resource definition for the vector class attribution API call
########################################################################################################################

@api.expect(vector_class_attribution_request_model)
@api.header('Content-Type', 'application/json')
class VectorClassAttribution(Resource):
    """ Class for handling the POST request

    This class defines the API call for starting the vector class attribution workflow. The class consists of one
    methods which accepts a POST request. For the POST request a JSON with several parameters is required, defined in
    the corresponding model.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin', 'vector_class_attribution'])
    @api.expect(auth_header_parser)
    @api.response(202, 'Order Received', service_success_response_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for starting off the vector class attribution workflow

        <p style="text-align: justify">This method defines the handler of the POST request for starting off the vector
        class attribution processing chain for CLC+ Task 2.2 and Task 3. It is an asynchronous call and thus, it does
        not return the requested data immediately but generates an order ID. After the request has been submitted
        successfully, a message to a RabbitMQ queue will be send. A listener in the backend triggers the further
        procedure, starting with the job scheduling of the order. The final result will be stored in a database in form
        of a link and can be retrieved via the browser. To access the service it is necessary to generate a valid Bearer
        token with sufficient access rights, otherwise the request will return a HTTP status code 401 or 403. In case of
        those errors, please contact the GeoVille service team for any support.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">This method can be used for both Task 2.2. and Task 3 for the Production of the
        CLC+ Backbone. The basic steps of this methods are:</p>
        <ul>
        <li><p><i>Preprocessing: Mosaics and clips input rasters to target vector file extent</i></p></li>
        <li><p><i>Extraction: Extracts values for each polygon and applies a function to these values.
        The result will be store in a csv file)</i></p></li>
        <li><p><i>Postprocessing / QC: Checks if any errors occurred during the extraction and prepares the csv files
        for the subsequent insertion into the HDF5 cubes</p></li>
        <li><p><i>Upload to S3</i></p></li>
        </ul>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>vector (str): Path to Vector File from Task 1. Can be any format such as gdb, shp, gpkg, etc...
        (e.g. "/vsis3/task22/tests/in/test1.shp")</i></p></li>
        <li><p><i>raster (str): List of Input Rasters that will be used for the extraction
        (e.g. "/vsis3/task22/tests/in/test.tif /vsis3/task22/tests/in/test2.tif") - separated with a whitespace</i></p></li>
        <li><p><i>subproduction_unit_name (int): ID of the Subproduction Unit (e.g. 214)</i></p></li>
        <li><p><i>id_column (str): Name of the ID column of the provided Vector File. (e.g. "id")</i></p></li>
        <li><p><i>na_value (int): NA Value that should be ignored during extraction (e.g. 255)</i></p></li>
        <li><p><i>method (str): Name of the aggregation method for the extracted values. To call Task 2.2. specify
        "clcp_vector_class", for Task 3 currently the following methods are implemented: "mean", "sd", "statistics"
        (Combination of mean and sd), "relative_count" (Relative occurrence of a specified class per polygon. To call
        the relative_count method "method_params" have to be specified indicating which value should be regarded),
        "min", "max", "quantile", "ffi" and "masl".
        </i></p></li>
        <li><p><i>method_params (str): Some methods expect parameters. (e.g. method relative_count: "0 2" In this case
        the relative occurrence inside each polygon for the classes 0 and 2 will be extracted)</i></p></li>
        <li><p><i>col_names (str): List of column names, same number as output parameters for a specific method
        (e.g. 2 for statistics "IMD_mean IMD_sd")</i></p></li>
        <li><p><i>reference_year (str): Year that will be used during post processing to create a "reference_year" column.
        The expected format is "YYYY"</i></p></li>
        <li><p><i>bucket_path (str): Path including the S3 bucket name where the extracted data and QC reports should
        be stored. Please note that the folder on S3 doesn't have to exist, since it will be automatically created
        during this process. However pay close attention to the file path naming convention:
        "bucketname/folder/subfolder/". Note that there is no leading "/" before the bucketname and a mandatory "/"
        after the folder name!</i></p></li>
	    <li><p><i>config (str): S3 / GDAL config parameters for reading and writing from / to S3.
	    (e.g. "AWS_SECRET_ACCESS_KEY 123abc AWS_S3_ENDPOINT cf2.cloudferro.com:8080 AWS_VIRTUAL_HOSTING FALSE
	    AWS_ACCESS_KEY_ID abc123")</i></p></li>
        <li><p><i>user_id (str): User specific client ID</i></p></li>
        <li><p><i>service_name (str): Unique name of the service to be called. Name should not be changed</i></p></li>
        </ul>



        <br><b>Result:</b>
        <p style="text-align: justify">After the request was successfully received by the CLC+ API, an order ID will be
        created for the submitted job in the GEMS backend and stored in a database with all necessary information for
        the consumer and the system itself. The initial status of the order in the database will be set to 'received'.
        After that the order ID will be returned in form of a Hypermedia link which enables the possibilities to
        programmatically check the status the order by a piece of code of a CLC+ API consumer. In the following the
        status of the order can be queried by using the GEMS service route listed below:</p>

        <ul><li><p><i>/services/order_status/{order_id}</i></p></li></ul>

        <p style="text-align: justify">The status of the order will be updated whenever the processing chain reaches
        the next step in its internal calculation. In case of success, the user will receive a link, which provides the
        ordered file. Additionally an e-mail notification is enabled, which sends out an e-mail in case of success,
        with the resulting link or in case of failure, with a possible error explanation.
        </p>

        """

        order_id = None

        try:
            req_args = api.payload

            if not check_user_existence(req_args['user_id'], database_config_file, database_config_section_api):
                error = NotFoundError('User ID does not exist', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-vector_class_attribution', order_id)
                return {'message': error.to_dict()}, 404

            if not check_service_name_existence(req_args['service_name'], database_config_file,
                                                database_config_section_api):
                error = NotFoundError('Service name does not exist', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-vector_class_attribution', order_id)
                return {'message': error.to_dict()}, 404

            service_id = get_service_id(req_args['service_name'], database_config_file, database_config_section_api)
            order_id = generate_orderid(req_args['user_id'], service_id, json.dumps(req_args))
            gemslog(LogLevel.INFO, f'Request payload: {req_args}', 'API-vector_class_attribution', order_id)

            publish_to_queue(req_args['service_name'], order_id, req_args)

            update_query = """UPDATE customer.service_orders 
                                  set status = 'RECEIVED' 
                              WHERE
                                  order_id = %s;
                           """
            execute_database(update_query, (order_id,), database_config_file, database_config_section_api, True)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-vector_class_attribution', order_id)
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-vector_class_attribution', order_id)
            return {'message': error.to_dict()}, 503

        except Exception as err:
            error = InternalServerErrorAPI(f'Unexpected error occurred: {err}', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-vector_class_attribution', order_id)
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, f'Request successful', 'API-vector_class_attribution', order_id)
            return {
                       'message': 'Your order has been successfully submitted',
                       'links': {
                           'href': f'/services/order_status/{order_id}',
                           'rel': 'services',
                           'type': 'GET'
                       }
                   }, 202
