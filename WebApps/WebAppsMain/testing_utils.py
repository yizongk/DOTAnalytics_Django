import json
from django.urls import reverse
from WebAppsMain.settings import APP_DEFINED_HTTP_GET_CONTEXT_KEYS, APP_DEFINED_HTTP_POST_JSON_KEYS, TEST_WINDOWS_USERNAME
import copy
import unittest
from django.test import Client


class HttpPostTestCase(unittest.TestCase):
    """
        This class contains some standard functions that help test any HTTP POST requests in this Django project

        Each test case class must define the self.api_name in the setUpClass(self).
        Sample usage:

        class TestSomeThing(HttpPostTestCase):
            @classmethod
            def setUpClass(self):
                self.api_name                       = 'name_of_your_view'   ## This is REQUIRED
                self.response_param_specifications  = []                    ## This is REQUIRED, set it to empty list if is has none. Expects the format to be like this:
                                                                                [
                                                                                    {name: '...', null: False}   ## if null = True, the param is allowed to be None
                                                                                    ,{name: '...', null: True}
                                                                                    ,{name: '...', null: ...}
                                                                                    ,...
                                                                                ]

            @classmethod
            def tearDownClass(self):
                pass                                    ## Optional

    """
    client                          = Client()
    api_name                        = None
    response_param_specifications   = None

    def __post_to_api(self, payload):
        """Returns the response after calling the update api, as a dict. Will not pass if status_code is not 200"""
        response = post_to_api(
            client      = self.client,
            api_name    = self.api_name,
            payload     = payload,
            remote_user = TEST_WINDOWS_USERNAME)

        self.assertEqual(response.status_code, 200, f"'{self.api_name}' did not return status code 200")

        return response

    def post_and_get_json_response(self, payload):
        return decode_json_response_for_content( self.__post_to_api(payload) )

    def assert_request_param_good(self, valid_payload, testing_param_name, testing_data):
        """Assumes @valid_payload to contain a full payload that has all valid data and should allow the api to return successfully"""
        payload                     = copy.deepcopy(valid_payload) ## if not deepcopy, it will default to do a shallow copy
        payload[testing_param_name] = testing_data
        response                    = self.__post_to_api(payload=payload)
        content                     = decode_json_response_for_content(response)

        self.assertEqual(
            content['post_success'], True,
            f"POST request failed. Parameter '{testing_param_name}' should accept: '{testing_data}' ({type(testing_data)})\n{content}")

    def assert_request_param_bad(self, valid_payload, testing_param_name, testing_data):
        """Assumes @valid_payload to contain a full payload that has all valid data and should allow the api to return successfully"""
        payload                     = copy.deepcopy(valid_payload) ## if not deepcopy, it will default to do a shallow copy
        payload[testing_param_name] = testing_data
        response                    = self.__post_to_api(payload=payload)
        content                     = decode_json_response_for_content(response)

        self.assertEqual(
            content['post_success'], False,
            f"POST request succeded. Parameter '{testing_param_name}' should NOT accept: '{testing_data}' ({type(testing_data)})\n{content}")

    def assert_response_has_param(self, response_content, response_param_name):
        self.assertTrue(response_param_name in response_content['post_data'],
            f"'{response_param_name}' is not in the response: {response_content['post_data']}")

    def assert_response_has_param_and_not_null(self, response_content, response_param_name):
        self.assert_response_has_param(response_content=response_content, response_param_name=response_param_name)
        self.assertTrue(response_content['post_data'][response_param_name] is not None,
            f"response['post_data']['{response_param_name}'] can't be null: {response_content['post_data']}")

    def assert_response_satisfy_param_requirements(self, response_content):
        """
        Checks that the response param names in "post_data" match the criteria set by @self.response_param_specifications
        If response got extra param names in "post_data" that isn't in the @self.response_param_specifications, this will raise an error.

        Expects @self.response_param_specifications to be of this format:
            [
                {name: '...', null: False}   ## if null = True, the param is allowed to be None
                ,{name: '...', null: True}
                ,{name: '...', null: ...}
                ,...
            ]
        """
        if type(self.response_param_specifications) is not list:
            raise ValueError(f"assert_response_satisfy_param_requirements(): self.response_param_specifications is not a list: {type(self.response_param_specifications)}")

        required_propeties = ['name', 'null']
        for param_specification in self.response_param_specifications:
            ## Make sure the self.response_param_specifications follows the correct format
            for each_required_property in required_propeties:
                if each_required_property not in param_specification:
                    raise ValueError(f"assert_response_satisfy_param_requirements(): param_specification is missing this property: '{each_required_property}'")

            if type(param_specification['name']) is not str:
                raise ValueError(f"assert_response_satisfy_param_requirements(): param_specification['name'] must be a str.")
            if type(param_specification['null']) is not bool:
                raise ValueError(f"assert_response_satisfy_param_requirements(): param_specification['null'] must be a bool.")

            ## Check the response param to the given param specification
            if param_specification['null']:
                self.assert_response_has_param(response_content=response_content, response_param_name=param_specification['name'])
            else:
                self.assert_response_has_param_and_not_null(response_content=response_content, response_param_name=param_specification['name'])

        ## Make sure that the response don't got any extra param names that was specified by the caller
        specified_required_names = [each['name'] for each in self.response_param_specifications]
        for actual_response_param_name in response_content['post_data']:
            if actual_response_param_name not in specified_required_names:
                raise ValueError(f"assert_response_satisfy_param_requirements(): response got a param name '{actual_response_param_name}' that is not specified in the @self.response_param_specifications. Please add it to the test suite")


def validate_core_get_api_response_context(response):
    """
        In this django project, a standard GET response to any of the views should have these context variables
        "get_success"
        "get_error"
        "client_is_admin"
        additinal variables are optional
    """
    for key in APP_DEFINED_HTTP_GET_CONTEXT_KEYS:
        if key not in response.context_data:
            raise ValueError(f"validate_core_get_api_response_context(): Invalid GET response. Requires {APP_DEFINED_HTTP_GET_CONTEXT_KEYS} but there is missing keys from: {response.context_data.keys()}")

    return True


def validate_core_post_api_response_content(response):
    """
        Validates our project's standard JSON response.
        The standard response is a variation of the JSend standard: https://github.com/omniti-labs/jsend
        Looks like this:
        {
            "post_success": ...
            ,"post_msg": ...
            ,"post_data": ...
        }

        It is allowed to have additional keys to the required ones. For example:
        {
            "post_success": ...
            ,"post_msg": ...
            ,"post_data": ...
            ,"var_1": ...
            ,"var_2": ...
            ...
        }
    """
    response_content = decode_json_response_for_content(response=response)

    for key in APP_DEFINED_HTTP_POST_JSON_KEYS:
        if key not in response_content:
            raise ValueError(f"validate_core_post_api_response_content(): Invalid POST JSON response. Requires {APP_DEFINED_HTTP_POST_JSON_KEYS} but there is missing keys from: {response_content.keys()}")

    return True


def get_to_api(client, api_name, remote_user=TEST_WINDOWS_USERNAME):
    """return the response of the GET api call. Defaults to user @TEST_WINDOWS_USERNAME"""
    try:
        response = client.get(
            reverse(api_name)
            ,REMOTE_USER=remote_user
        )

        validate_core_get_api_response_context(response=response)

        return response
    except Exception as e:
        raise ValueError(f"get_to_api(): GET to {reverse(api_name)}: {e}")


def decode_json_response_for_content(response):
    """reponse.content is in binary, need to decode it to get access to it in python dictinary format"""
    return json.loads(response.content.decode('utf-8'))


def post_to_api(client, api_name, payload, remote_user=TEST_WINDOWS_USERNAME):
    """return the response of the POST api call. Defaults to user @TEST_WINDOWS_USERNAME"""
    try:
        response = client.post(
            reverse(api_name)
            ,data           = json.dumps(payload)
            ,content_type   = 'application/json'
            ,REMOTE_USER    = remote_user
        )

        validate_core_post_api_response_content(response=response)

        return response
    except Exception as e:
        raise ValueError(f"post_to_api(): POST to {reverse(api_name)}: {e}")

