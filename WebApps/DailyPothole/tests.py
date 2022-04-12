from django.test import Client
import unittest
from .models import *
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.contrib import auth
from django.utils import timezone
import copy
from WebAppsMain.settings import TEST_WINDOWS_USERNAME
from WebAppsMain.testing_utils import get_to_api, post_to_api, decode_json_response_for_content
### DO NOT RUN THIS IN PROD ENVIRONMENT


DEFAULT_OPERATION = "BRIDGE PM"
DEFAULT_BORO = "QUEENS"


def get_or_create_user(windows_username=TEST_WINDOWS_USERNAME):
    """create or get an user and return the user object. Defaults to TEST_WINDOWS_USERNAME as the user"""
    try:
        return TblUser.objects.using('DailyPothole').get_or_create(
            username=windows_username
        )[0]
    except Exception as e:
        raise ValueError(f"get_or_create_user(): {e}")


def grant_admin_status(windows_username=TEST_WINDOWS_USERNAME):
    """create or get an user and set it up with admin status and return the user object. Defaults to TEST_WINDOWS_USERNAME as the user"""
    try:
        user = get_or_create_user(windows_username=windows_username)
        user.is_admin=True
        user.save(using='DailyPothole')
        return user
    except Exception as e:
            raise ValueError(f"grant_admin_status(): {e}")


def remove_admin_status(windows_username=TEST_WINDOWS_USERNAME):
    """removes the admin status of an user"""
    try:
        user = get_or_create_user(windows_username=windows_username)
        user.is_admin=False
        user.save(using='DailyPothole')
        return user
    except Exception as e:
            raise ValueError(f"remove_admin_status(): {e}")


def set_up_permissions(windows_username=TEST_WINDOWS_USERNAME, operation_boro_pairs=[(DEFAULT_OPERATION, DEFAULT_BORO)]):
    """
        set up permissions for a user. If user is admin, the permissions added will probably mean nothing.

        @windows_username is self explanatory, just one name
        @operation_boro_pairs should be a list of 2-item tuple like this: (str_operation, str_boro)

        returns the user object associated for the permissions
    """
    try:
        for each in operation_boro_pairs:
            operation   = each[0]
            boro        = each[1]

            operation_boro = TblOperationBoro.objects.using('DailyPothole').get(
                operation_id__operation__exact  = operation
                ,boro_id__boro_long__exact      = boro
                ,is_active                      = True
            )

            user = get_or_create_user(windows_username=windows_username)
            permission = TblPermission.objects.using('DailyPothole').get_or_create(
                user_id             = user
                ,operation_boro_id  = operation_boro
            )[0]
            permission.is_active = True
            permission.save(using="DailyPothole")

            return user
    except Exception as e:
        raise ValueError(f"set_up_permissions(): {e}")


def tear_down_permissions(windows_username=TEST_WINDOWS_USERNAME):
    """set all permissions as inactive for an user. If user is admin, the permissions removed will probably mean nothing."""
    try:
        permissions = TblPermission.objects.using('DailyPothole').filter(
            user_id__username__exact=windows_username
        )

        for each in permissions:
            each.is_active = False
            each.save(using='DailyPothole')
    except Exception as e:
            raise ValueError(f"tear_down_permissions_for_user(): {e}")


def tear_down(windows_username=TEST_WINDOWS_USERNAME):
    """Removes admin status of @windows_username, and set all its permissions to inactive. Defaults to TEST_WINDOWS_USERNAME"""
    try:
        remove_admin_status(windows_username=windows_username)
        tear_down_permissions(windows_username=windows_username)
    except Exception as e:
        raise ValueError(f"tear_down(): {e}")


# Create your tests here.
class TestViewPagesResponse(unittest.TestCase):
    def setUp(self):
        tear_down()
        set_up_permissions()
        self.client                 = Client()

        self.regular_views = [
            'dailypothole_home_view',
            'dailypothole_about_view',
            'dailypothole_contact_view',
            'dailypothole_pothole_data_entry_view',
        ]

        self.admin_views = [
            'dailypothole_pothole_data_grid_view',
            'dailypothole_complaints_input_view',
            'dailypothole_reports_view',
            'dailypothole_admin_panel_view',
            'dailypothole_users_panel_view',
            'dailypothole_user_permissions_panel_view',
            'dailypothole_csv_export_view',
        ]

    def tearDown(self):
        tear_down()

    def test_views_response_status_200(self):
        """Test normal user"""
        remove_admin_status()
        for view in self.regular_views:
            response = get_to_api(client=self.client, api_name=view, remote_user=TEST_WINDOWS_USERNAME)
            self.assertEqual(response.status_code, 200, f"'{view}' did not return status code 200")

        for view in self.admin_views:
            response = get_to_api(client=self.client, api_name=view, remote_user=TEST_WINDOWS_USERNAME)
            self.assertEqual(response.status_code, 200, f"'{view}' did not return status code 200")

        """Test admin user"""
        grant_admin_status()
        for view in self.regular_views:
            response = get_to_api(client=self.client, api_name=view, remote_user=TEST_WINDOWS_USERNAME)
            self.assertEqual(response.status_code, 200, f"'{view}' did not return status code 200")

        for view in self.admin_views:
            response = get_to_api(client=self.client, api_name=view, remote_user=TEST_WINDOWS_USERNAME)
            self.assertEqual(response.status_code, 200, f"'{view}' did not return status code 200")

    def test_views_response_user_admin_restriction(self):
        """Test normal user, should only have acess to regular views"""
        remove_admin_status()
        for view in self.regular_views:
            response = get_to_api(client=self.client, api_name=view, remote_user=TEST_WINDOWS_USERNAME)
            self.assertTrue(response.context['req_success'], f"'{view}' did not return req_success True on a regular view for a non-admin client\n    {response.context['err_msg']}")

        for view in self.admin_views:
            response = get_to_api(client=self.client, api_name=view, remote_user=TEST_WINDOWS_USERNAME)
            self.assertFalse(response.context['req_success'], f"'{view}' returned req_success True on an admin view for a non-admin client\n    {response.context['err_msg']}")
            self.assertTrue("not an Admin" in response.context['err_msg'], f"'{view}' did not have error message on an admin view when client is non-admin\n    {response.context['err_msg']}")

        """Test admin user, should have access to all views"""
        grant_admin_status()
        for view in self.regular_views:
            response = get_to_api(client=self.client, api_name=view, remote_user=TEST_WINDOWS_USERNAME)
            self.assertTrue(response.context['req_success'], f"'{view}' did not return req_success True on a regular view for an admin client\n    {response.context['err_msg']}")

        for view in self.admin_views:
            response = get_to_api(client=self.client, api_name=view, remote_user=TEST_WINDOWS_USERNAME)
            self.assertTrue(response.context['req_success'], f"'{view}' did not return req_success True on an admin view for an admin client\n    {response.context['err_msg']}")

    def __assert_additional_context_data(self):
        for view in self.regular_views:
            response = get_to_api(client=self.client, api_name=view, remote_user=TEST_WINDOWS_USERNAME)
            if view == 'dailypothole_pothole_data_entry_view':
                self.assertTrue('today' in response.context_data.keys(), f"dailypothole_pothole_data_entry_view is missing context variable 'today'")

        for view in self.admin_views:
            response = get_to_api(client=self.client, api_name=view, remote_user=TEST_WINDOWS_USERNAME)
            if view == 'dailypothole_pothole_data_grid_view':
                self.assertTrue('ag_grid_col_def_json'  in response.context_data.keys(), f"dailypothole_pothole_data_grid_view is missing context variable 'ag_grid_col_def_json'")
                self.assertTrue('pothole_data_json'     in response.context_data.keys(), f"dailypothole_pothole_data_grid_view is missing context variable 'pothole_data_json'")
            if view == 'dailypothole_user_permissions_panel_view':
                self.assertTrue('user_list'             in response.context_data.keys(), f"dailypothole_user_permissions_panel_view is missing context variable 'user_list'")
                self.assertTrue('operation_list'        in response.context_data.keys(), f"dailypothole_user_permissions_panel_view is missing context variable 'operation_list'")
                self.assertTrue('boro_list'             in response.context_data.keys(), f"dailypothole_user_permissions_panel_view is missing context variable 'boro_list'")
            if view == 'dailypothole_csv_export_view':
                self.assertTrue('operation_list'        in response.context_data.keys(), f"dailypothole_csv_export_view is missing context variable 'operation_list'")

    def test_views_response_data(self):
        """Some views have additional context data, need to test for those here"""
        # Test normal user
        remove_admin_status()
        self.__assert_additional_context_data()

        # Test admin user
        grant_admin_status()
        self.__assert_additional_context_data()


class TestAPIUpdatePotholesData(unittest.TestCase):
    """methods that starts with name 'test...' are the methods be called by unittest"""
    def setUp(self):
        tear_down()
        self.user_obj                   = set_up_permissions()
        self.client                     = Client()
        self.api_name                   = 'dailypothole_update_potholes_data_api'

        self.valid_operation            = DEFAULT_OPERATION
        self.valid_borough              = DEFAULT_BORO
        self.valid_date                 = f'{datetime.now().strftime("%Y-%m-%d")}'
        self.valid_crew_count           = 1
        self.valid_holes_repaired       = 2
        self.valid_planned_crew_count   = 3

        self.valid_payload = {
            'PotholeData': {   ## valid for Pothole Data request
                'request_type'              : 'PotholeData',
                'date_of_repair'            : self.valid_date,
                'operation'                 : self.valid_operation,
                'borough'                   : self.valid_borough,
                'crew_count'                : self.valid_crew_count,
                'holes_repaired'            : self.valid_holes_repaired,
                'planned_crew_count'        : None,
                'planned_date'              : None,
            }
            ,'TodayCrewData': {  ## valid for Today Crew Data request
                "request_type"              : 'TodayCrewData',
                "date_of_repair"            : None,
                "operation"                 : self.valid_operation,
                "borough"                   : self.valid_borough,
                "crew_count"                : None,
                "holes_repaired"            : None,
                "planned_crew_count"        : self.valid_planned_crew_count,
                "planned_date"              : self.valid_date,
            }
        }

    def tearDown(self):
        tear_down()

    def __post_to_api(self, payload):
        """Returns the response after calling the update api, as a dict. Will not pass if status_code is not 200"""
        response = post_to_api(
            client      = self.client,
            api_name    = self.api_name,
            payload     = payload,
            remote_user = TEST_WINDOWS_USERNAME)

        self.assertEqual(response.status_code, 200, f"'{self.api_name}' did not return status code 200")

        return response

    def __assert_request_param_good(self, valid_payload, testing_param_name, testing_data):
        payload                     = copy.deepcopy(valid_payload) ## if not deepcopy, it will default to do a shallow copy
        payload[testing_param_name] = testing_data
        response                    = self.__post_to_api(payload=payload)
        content                     = decode_json_response_for_content(response)

        self.assertEqual(
            content['post_success'], True,
            f"POST request failed. Parameter '{testing_param_name}' should accept: '{testing_data}'\n{content}")

    def __assert_request_param_bad(self, valid_payload, testing_param_name, testing_data):
        payload                     = copy.deepcopy(valid_payload) ## if not deepcopy, it will default to do a shallow copy
        payload[testing_param_name] = testing_data
        response                    = self.__post_to_api(payload=payload)
        content                     = decode_json_response_for_content(response)

        self.assertEqual(
            content['post_success'], False,
            f"POST request succeded. Parameter '{testing_param_name}' should NOT accept: '{testing_data}'\n{content}")

    def test_with_valid_data(self):
        for payload_type in self.valid_payload:
            payload = self.valid_payload[payload_type]
            response_content = decode_json_response_for_content( self.__post_to_api(payload) )

            ## Check that the request was successful
            self.assertEqual(response_content['post_success'], True,
                f"payload_type '{payload_type}': update was not successfully with valid data\n{response_content['post_msg']}")

            ## Check if data was saved correctly
            saved_object = TblPotholeMaster.objects.using('DailyPothole').get(
                repair_date=self.valid_date
                ,operation_boro_id__operation_id__operation__exact=self.valid_operation
                ,operation_boro_id__boro_id__boro_long__exact=self.valid_borough
            )

            if payload_type == 'PotholeData':
                self.assertEqual(
                    self.valid_crew_count,
                    saved_object.repair_crew_count,
                    f"payload_type '{payload_type}': [repair_crew_count] didn't save correctly: '{self.valid_crew_count}' input-->database '{saved_object.repair_crew_count}'" )
                self.assertEqual(
                    self.valid_holes_repaired,
                    saved_object.holes_repaired,
                    f"payload_type '{payload_type}': [holes_repaired] didn't save correctly: '{self.valid_holes_repaired}' input-->database '{saved_object.holes_repaired}'" )
            elif payload_type == 'TodayCrewData':
                self.assertEqual(
                    self.valid_planned_crew_count,
                    saved_object.daily_crew_count,
                    f"payload_type '{payload_type}': [daily_crew_count] didn't save correctly: '{self.valid_planned_crew_count}' input-->database '{saved_object.daily_crew_count}'" )
            else:
                raise ValueError( f"TestAPIUpdatePotholesData: test_with_valid_data(): payload_type not recognized in test case: '{payload_type}'" )

            self.assertTrue(  (timezone.now() - saved_object.last_modified_timestamp).total_seconds() < 10,
                f"payload_type '{payload_type}': [last_modified_timestamp] didn't save correctly: '{saved_object.last_modified_timestamp.strftime('%Y-%m-%d %H:%M:%S')}' input-->database '{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}'. Cannot exceed more than 10 seconds difference" )
            self.assertEqual( saved_object.last_modified_by_user_id.user_id  , self.user_obj.user_id,
                f"payload_type '{payload_type}': [last_modified_by_user_id] didn't save correctly: '{saved_object.last_modified_by_user_id.user_id}' input-->database '{self.user_obj.user_id}'" )

    def test_data_validation(self):
        f"""Testing {self.api_name} data validation"""

        ## For PotholeData
        payload = self.valid_payload['PotholeData']
        parameters = [
            # Parameter name    # Accepted type
            "request_type"      # str   -> ['PotholeData']
            ,"operation"        # str   -> 'operation_names'
            ,"borough"          # str   -> 'boro_names'
            ,"date_of_repair"   # str   -> 'YYYY-MM-DD'
            ,"crew_count"       # float -> >= 0
            ,"holes_repaired"   # int   -> >= 0
        ]
        for param_name in parameters:

            if param_name == 'request_type':
                valid   = ['PotholeData']
                invalid = ['a', 1, 2.3, None, True]
            elif param_name == 'operation':
                valid   = [self.valid_operation]
                invalid = ['a', 1, 2.3, None, False]
            elif param_name == 'borough':
                valid   = [self.valid_borough]
                invalid = ['a', 1, 2.3, None, False]
            elif param_name == 'date_of_repair':
                valid   = [f'{datetime.now().strftime("%Y-%m-%d")}']
                invalid = ['a', 1, 2.3, False]
            elif param_name == 'crew_count':
                valid   = [1, 1.2]
                invalid = ['a', -5, False]
            elif param_name == 'holes_repaired':
                valid   = [1]
                invalid = ['a', -5, 2.4, False]
            else:
                raise ValueError(f"TestAPIUpdatePotholesData: test_data_validation(): PotholeData -> paremter test not implemented: '{param_name}'. Please remove or implement it")

            for data in valid:
                self.__assert_request_param_good(valid_payload=payload, testing_param_name=param_name, testing_data=data)

            for data in invalid:
                self.__assert_request_param_bad(valid_payload=payload, testing_param_name=param_name, testing_data=data)


        ## For TodayCrewData
        payload = self.valid_payload['TodayCrewData']
        parameters = [
            "request_type"          # str   -> ['TodayCrewData']
            ,"operation"            # str   -> 'operation_names'
            ,"borough"              # str   -> 'boro_names'
            ,"planned_date"         # str   -> 'YYYY-MM-DD'
            ,"planned_crew_count"   # float -> >= 0
        ]
        for param_name in parameters:

            if param_name == 'request_type':
                valid   = ['TodayCrewData']
                invalid = ['a', 1, 2.3, None, True]
            elif param_name == 'operation':
                valid   = [self.valid_operation]
                invalid = ['a', 1, 2.3, None, False]
            elif param_name == 'borough':
                valid   = [self.valid_borough]
                invalid = ['a', 1, 2.3, None, False]
            elif param_name == 'planned_date':
                valid   = [f'{datetime.now().strftime("%Y-%m-%d")}']
                invalid = ['a', 1, 2.3, False]
            elif param_name == 'planned_crew_count':
                valid   = [1, 1.2]
                invalid = ['a', -5, False]
            else:
                raise ValueError(f"TestAPIUpdatePotholesData: test_data_validation(): TodayCrewData -> paremter test not implemented: '{param_name}'. Please remove or implement it")

            for data in valid:
                self.__assert_request_param_good(valid_payload=payload, testing_param_name=param_name, testing_data=data)

            for data in invalid:
                self.__assert_request_param_bad(valid_payload=payload, testing_param_name=param_name, testing_data=data)


class TestAPILookupPotholesAndCrewData(unittest.TestCase):
    def setUp(self):
        tear_down()
        set_up_permissions()
        self.client                 = Client()
        self.api_name               = 'dailypothole_lookup_potholes_and_crew_data_api'

        self.valid_look_up_date     = f'{datetime.now().strftime("%Y-%m-%d")}'
        self.valid_operation        = DEFAULT_OPERATION
        self.valid_borough          = DEFAULT_BORO

        self.valid_payload = {
            'look_up_date'  : self.valid_look_up_date,
            'operation'     : self.valid_operation,
            'borough'       : self.valid_borough,
        }

    def tearDown(self):
        tear_down()

    def __post_to_api(self, payload):
        """Returns the response after calling the update api, as a dict. Will not pass if status_code is not 200"""
        response = post_to_api(
            client      = self.client,
            api_name    = self.api_name,
            payload     = payload,
            remote_user = TEST_WINDOWS_USERNAME)

        self.assertEqual(response.status_code, 200, f"'{self.api_name}' did not return status code 200")

        return response

    def __assert_request_param_good(self, valid_payload, testing_param_name, testing_data):
        payload                     = copy.deepcopy(valid_payload) ## if not deepcopy, it will default to do a shallow copy
        payload[testing_param_name] = testing_data
        response                    = self.__post_to_api(payload=payload)
        content                     = decode_json_response_for_content(response)

        self.assertEqual(
            content['post_success'], True,
            f"POST request failed. Parameter '{testing_param_name}' should accept: '{testing_data}'\n{content}")

    def __assert_request_param_bad(self, valid_payload, testing_param_name, testing_data):
        payload                     = copy.deepcopy(valid_payload) ## if not deepcopy, it will default to do a shallow copy
        payload[testing_param_name] = testing_data
        response                    = self.__post_to_api(payload=payload)
        content                     = decode_json_response_for_content(response)

        self.assertEqual(
            content['post_success'], False,
            f"POST request succeded. Parameter '{testing_param_name}' should NOT accept: '{testing_data}'\n{content}")

    def test_with_valid_data(self):
        payload = self.valid_payload
        response_content = decode_json_response_for_content( self.__post_to_api(payload) )

        ## Check that the request was successful
        self.assertEqual(response_content['post_success'], True,
            f"api call was not successfully with valid data")
        self.assertTrue('look_up_date' in response_content,
            f"'look_up_date' is not in the response")
        self.assertTrue(response_content['look_up_date'] is not None,
            f"response['look_up_date'] can't be null")
        self.assertTrue('repair_crew_count' in response_content,
            f"'repair_crew_count' is not in the response")
        self.assertTrue('holes_repaired' in response_content,
            f"'holes_repaired' is not in the response")
        self.assertTrue('daily_crew_count' in response_content,
            f"'daily_crew_count' is not in the response")

    def test_data_validation(self):
        payload = self.valid_payload
        parameters = [
            # Parameter name    # Accepted type
            "look_up_date"      # str   -> 'YYYY-MM-DD'
            ,"operation"        # str   -> 'operation_names'
            ,"borough"          # str   -> 'boro_names'
        ]
        for param_name in parameters:

            if param_name == 'look_up_date':
                valid   = [f'{datetime.now().strftime("%Y-%m-%d")}']
                invalid = ['a', 1, 2.3, False]
            elif param_name == 'operation':
                valid   = [self.valid_operation]
                invalid = ['a', 1, 2.3, None, False]
            elif param_name == 'borough':
                valid   = [self.valid_borough]
                invalid = ['a', 1, 2.3, None, False]
            else:
                raise ValueError(f"TestAPILookupPotholesAndCrewData: test_data_validation(): paremter test not implemented: '{param_name}'. Please remove or implement it")

            for data in valid:
                self.__assert_request_param_good(valid_payload=payload, testing_param_name=param_name, testing_data=data)

            for data in invalid:
                self.__assert_request_param_bad(valid_payload=payload, testing_param_name=param_name, testing_data=data)


class TestAPIUpdatePotholesFromDataGrid(unittest.TestCase):
    def setUp(self):
        tear_down()
        self.user_obj               = grant_admin_status()
        self.client                 = Client()
        self.api_name               = 'dailypothole_update_potholes_from_data_grid_api'

        self.valid_repair_date      = f'{datetime.now().strftime("%Y-%m-%d")}'
        self.valid_operation        = DEFAULT_OPERATION
        self.valid_boro_long        = DEFAULT_BORO

        self.valid_payloads = [
            {
                'repair_date'   : self.valid_repair_date,
                'operation'     : self.valid_operation,
                'boro_long'     : self.valid_boro_long,
                'column_name'   : 'Repair Crew Count',
                'new_value'     : '10.2',
            }
            ,{
                'repair_date'   : self.valid_repair_date,
                'operation'     : self.valid_operation,
                'boro_long'     : self.valid_boro_long,
                'column_name'   : 'Holes Repaired',
                'new_value'     : '20',
            }
            ,{
                'repair_date'   : self.valid_repair_date,
                'operation'     : self.valid_operation,
                'boro_long'     : self.valid_boro_long,
                'column_name'   : 'Daily Crew Count',
                'new_value'     : '30.2',
            }
        ]

    def tearDown(self):
        tear_down()

    def __post_to_api(self, payload):
        """Returns the response after calling the update api, as a dict. Will not pass if status_code is not 200"""
        response = post_to_api(
            client      = self.client,
            api_name    = self.api_name,
            payload     = payload,
            remote_user = TEST_WINDOWS_USERNAME)

        self.assertEqual(response.status_code, 200, f"'{self.api_name}' did not return status code 200")

        return response

    def __assert_request_param_good(self, valid_payload, testing_param_name, testing_data):
        payload                     = copy.deepcopy(valid_payload) ## if not deepcopy, it will default to do a shallow copy
        payload[testing_param_name] = testing_data
        response                    = self.__post_to_api(payload=payload)
        content                     = decode_json_response_for_content(response)

        self.assertEqual(
            content['post_success'], True,
            f"POST request failed. Parameter '{testing_param_name}' should accept: '{testing_data}'\n{content}")

    def __assert_request_param_bad(self, valid_payload, testing_param_name, testing_data):
        payload                     = copy.deepcopy(valid_payload) ## if not deepcopy, it will default to do a shallow copy
        payload[testing_param_name] = testing_data
        response                    = self.__post_to_api(payload=payload)
        content                     = decode_json_response_for_content(response)

        self.assertEqual(
            content['post_success'], False,
            f"POST request succeded. Parameter '{testing_param_name}' should NOT accept: '{testing_data}'\n{content}")

    def test_api_accept_only_admins(self):
        self.user_obj.is_admin=False
        self.user_obj.save(using='DailyPothole')

        payload = self.valid_payloads[0]
        res     = self.__post_to_api(payload)
        content = decode_json_response_for_content(res)

        self.assertTrue((content['post_success']==False) and ("not an admin" in content['post_msg']),
            f"api should have detected that user is not an admin and fail")

        self.user_obj.is_admin=True
        self.user_obj.save(using='DailyPothole')

    def test_with_valid_data(self):
        for payload in self.valid_payloads:
            response = self.__post_to_api(payload)
            response_content = decode_json_response_for_content( response )

            ## Check that the request was successful
            self.assertTrue(response_content['post_success'],
                f"update was not successfully with valid data: {response_content['post_msg']}")

            ## Check that the returned JSON Response got all the data it required
            self.assertTrue('repair_date' in response_content['post_data'],
                f"'repair_date' is not in the response: {response_content['post_data']}")
            self.assertTrue(response_content['post_data']['repair_date'] is not None,
                f"response['repair_date'] can't be null: {response_content['post_data']}")

            self.assertTrue('operation' in response_content['post_data'],
                f"'operation' is not in the response: {response_content['post_data']}")
            self.assertTrue(response_content['post_data']['operation'] is not None,
                f"response['operation'] can't be null: {response_content['post_data']}")

            self.assertTrue('boro_long' in response_content['post_data'],
                f"'boro_long' is not in the response: {response_content['post_data']}")
            self.assertTrue(response_content['post_data']['boro_long'] is not None,
                f"response['boro_long'] can't be null: {response_content['post_data']}")

            self.assertTrue('column_name' in response_content['post_data'],
                f"'column_name' is not in the response: {response_content['post_data']}")
            self.assertTrue(response_content['post_data']['column_name'] is not None,
                f"response['column_name'] can't be null: {response_content['post_data']}")

            self.assertTrue('new_value' in response_content['post_data'],
                f"'new_value' is not in the response: {response_content['post_data']}")
            self.assertTrue(response_content['post_data']['new_value'] is not None,
                f"response['new_value'] can't be null: {response_content['post_data']}")

            self.assertTrue('updated_by' in response_content['post_data'],
                f"'updated_by' is not in the response: {response_content['post_data']}")
            self.assertTrue(response_content['post_data']['updated_by'] is not None,
                f"response['updated_by'] can't be null: {response_content['post_data']}")


            ## Check if data was saved correctly
            saved_object = TblPotholeMaster.objects.using('DailyPothole').get(
                repair_date=self.valid_repair_date
                ,operation_boro_id__operation_id__operation__exact=self.valid_operation
                ,operation_boro_id__boro_id__boro_long__exact=self.valid_boro_long
            )

            if payload['column_name'] == 'Repair Crew Count':
                self.assertEqual(
                    float(payload['new_value']),
                    float(saved_object.repair_crew_count),
                    f"payload['column_name'] '{payload['column_name']}': [repair_crew_count] didn't save correctly: '{payload['new_value']}' input-->database '{saved_object.repair_crew_count}'" )
            elif payload['column_name'] == 'Holes Repaired':
                self.assertEqual(
                    float(payload['new_value']),
                    float(saved_object.holes_repaired),
                    f"payload['column_name'] '{payload['column_name']}': [holes_repaired] didn't save correctly: '{payload['new_value']}' input-->database '{saved_object.holes_repaired}'" )
            elif payload['column_name'] == 'Daily Crew Count':
                self.assertEqual(
                    float(payload['new_value']),
                    float(saved_object.daily_crew_count),
                    f"payload['column_name'] '{payload['column_name']}': [daily_crew_count] didn't save correctly: '{payload['new_value']}' input-->database '{saved_object.daily_crew_count}'" )
            else:
                raise ValueError( f"TestAPIUpdatePotholesFromDataGrid: test_with_valid_data(): payload['column_name'] not recognized in test case: '{payload['column_name']}'" )

            self.assertTrue(  (timezone.now() - saved_object.last_modified_timestamp).total_seconds() < 10,
                f"payload['column_name'] '{payload['column_name']}': [last_modified_timestamp] didn't save correctly: '{saved_object.last_modified_timestamp.strftime('%Y-%m-%d %H:%M:%S')}' input-->database '{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}'. Cannot exceed more than 10 seconds difference" )
            self.assertEqual( saved_object.last_modified_by_user_id.user_id  , self.user_obj.user_id,
                f"payload['column_name'] '{payload['column_name']}': [last_modified_by_user_id] didn't save correctly: '{saved_object.last_modified_by_user_id.user_id}' input-->database '{self.user_obj.user_id}'" )

    def test_data_validation(self):
        crew_count_payload      = self.valid_payloads[0]
        holes_repaired_payload  = self.valid_payloads[1]
        parameters = [
            # Parameter name    # Accepted type
            "repair_date"       # str   -> 'YYYY-MM-DD'
            ,"operation"        # str   -> 'operation_names'
            ,"boro_long"        # str   -> 'boro_names'
            ,"column_name"      # str   -> ['Repair Crew Count', 'Holes Repaired', 'Daily Crew Count']
            ,"new_value"        # str   -> string formatted postive int(for holes repaired) or string formatted decimal(no more than 2 decimal places, for crew count).
        ]
        for param_name in parameters:

            ## Test the two crew counts which allows positive decimal and int
            if param_name == 'repair_date':
                valid   = [f'{datetime.now().strftime("%Y-%m-%d")}']
                invalid = ['a', 1, 2.3, False]
            elif param_name == 'operation':
                valid   = [self.valid_operation]
                invalid = ['a', 1, 2.3, None, False]
            elif param_name == 'boro_long':
                valid   = [self.valid_boro_long]
                invalid = ['a', 1, 2.3, None, False]
            elif param_name == 'column_name':
                valid   = ['Repair Crew Count', 'Daily Crew Count']
                invalid = ['a', 1, 2.3, None, False]
            elif param_name == 'new_value':
                valid   = ['0', '1', '2.2', '4.45']
                invalid = ['a', 1, 2.3, '-1', '-1.2', '11.567', None, False]
            else:
                raise ValueError(f"TestAPIUpdatePotholesFromDataGrid: test_data_validation(): Crew Count -> paremter test not implemented: '{param_name}'. Please remove or implement it")

            for data in valid:
                self.__assert_request_param_good(valid_payload=crew_count_payload, testing_param_name=param_name, testing_data=data)

            for data in invalid:
                self.__assert_request_param_bad(valid_payload=crew_count_payload, testing_param_name=param_name, testing_data=data)

            ## Test the holes repaired which allows only positive int
            if param_name == 'repair_date':
                valid   = [f'{datetime.now().strftime("%Y-%m-%d")}']
                invalid = ['a', 1, 2.3, False]
            elif param_name == 'operation':
                valid   = [self.valid_operation]
                invalid = ['a', 1, 2.3, None, False]
            elif param_name == 'boro_long':
                valid   = [self.valid_boro_long]
                invalid = ['a', 1, 2.3, None, False]
            elif param_name == 'column_name':
                valid   = ['Holes Repaired']
                invalid = ['a', 1, 2.3, None, False]
            elif param_name == 'new_value':
                valid   = ['0', '1']
                invalid = ['a', 1, 2.3, '-1', '-1.2', '11.567', '2.2', '4.45', None, False]
            else:
                raise ValueError(f"TestAPIUpdatePotholesFromDataGrid: test_data_validation(): Holes Repaired -> paremter test not implemented: '{param_name}'. Please remove or implement it")

            for data in valid:
                self.__assert_request_param_good(valid_payload=holes_repaired_payload, testing_param_name=param_name, testing_data=data)

            for data in invalid:
                self.__assert_request_param_bad(valid_payload=holes_repaired_payload, testing_param_name=param_name, testing_data=data)

