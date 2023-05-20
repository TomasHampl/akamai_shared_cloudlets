# library functions
from akamai_shared_cloudlets.src.akamai_enums import AkamaiNetworks, ActivationOperations
from akamai_shared_cloudlets.src.akamai_http_requests_wrapper import AkamaiRequestWrapper
from akamai_shared_cloudlets.src.akamai_project_constants import DEFAULT_EDGERC_LOCATION
from akamai_shared_cloudlets.src.exceptions import IncorrectInputParameter, EdgeRcFileMissing
import os.path


class AkamaiApiRequestsAbstractions(object):

    def __init__(self, edgerc_location: str = DEFAULT_EDGERC_LOCATION):
        """
        The only available constructor
        @param edgerc_location:
        """
        if edgerc_location is None:
            self.edgerc_location = DEFAULT_EDGERC_LOCATION
        else:
            self.edgerc_location = edgerc_location
        if os.path.isfile(self.edgerc_location):
            self.request_wrapper = AkamaiRequestWrapper(edgerc_location)
        else:
            raise EdgeRcFileMissing(f"Unable to find the edgerc file in location {self.edgerc_location}")

    def list_shared_policies(self):
        """
        listSharedPolicies is a method that abstracts the Akamai API call to get all shared policies available
         to the provided credentials. What policies are available to the credentials depends on the permissions
         assigned to the API user that created the credentials.

        There are no parameters to be provided.
        @return: json response from the API call (if http status code was 200) or None in case it was
        anything else.
        """
        api_path = "/cloudlets/v3/policies"
        response = self.request_wrapper.send_get_request(api_path, {})
        if response.status_code == 200:
            return response.json()
        return None

    def get_shared_policy_by_name(self, policy_name: str) -> object:
        """
        Returns Shared cloudlet policyId based on the policy name. If not found, returns None...
        @param policy_name: is the name of the policy we'll be looking for in all policies
        @return: string representing the policyId or None (in case nothing was found or the API request to get the
        policies failed)
        """
        response_json = self.list_shared_policies()
        if response_json is not None:
            policies = response_json["content"]
            for policy_object in policies:
                if policy_object['name'] == policy_name:
                    return policy_object['id']
        return None

    def get_shared_policies_by_approximate_name(self, policy_name: str):
        """
        Provides a dictionary of policy name (as key) and their IDs (as value) where policy name contains the provided
        search string. If request failed (http status code != 200), or nothing was found, returns empty dictionary.
        @param policy_name: is a string we want to find in the shared policies (needle)
        @return: dictionary of policy names & ids, if nothing was found, returns empty dict
        """

        result_list = {}
        response_json = self.list_shared_policies()
        if response_json is not None:
            all_policies = response_json["content"]
            for policy_object in all_policies:
                if policy_name.lower() in policy_object["name"]:
                    policy = policy_object["name"]
                    policy_id = policy_object["id"]
                    result_list.update({policy: policy_id})
        return result_list

    def get_policy_by_id(self, policy_id: str) -> object:
        """
        Returns the json string representing the shared policy identified by the provided 'policyId'
        @param policy_id: is the policy_id we're looking for
        @return: json representing the Akamai response or None if nothing was found (or request to API failed)
        """
        api_path = f"/cloudlets/v3/policies/{policy_id}"
        response = self.request_wrapper.send_get_request(api_path, {})
        if response.status_code == 200:
            return response.json()
        return None

    def list_policy_versions(self, policy_id: str, page_number: int, page_size: int):
        """
        Fetches the policy versions (including their metadata, but not their contents)
        @param policy_id: is the id we need to identify the policy
        @param page_number: in case there are more policy versions than page_size param, this can be leveraged
        to build pagination
        @param page_size: how many records should be returned in one 'page'
        @return: json-encoded contents of the response or None, if an error occurred or nothing was found
        """
        api_path = f"/cloudlets/v3/policies/{policy_id}/versions"
        query_params = {
            "page": str(page_number),
            "size": str(page_size)
        }
        response = self.request_wrapper.send_get_request(api_path, query_params)
        if response.status_code == 200:
            return response.json()
        return None

    def get_latest_policy_version(self, policy_id: str):
        """
        Returns the latest version number of the policy identified by its ID
        @param policy_id: is the identifier we need to find the policy
        @return: version number or None if nothing was found or an error occurred
        """
        latest_policy = self.get_latest_policy(policy_id)
        if latest_policy is not None:
            return latest_policy["version"]
        return None

    def get_latest_policy(self, policy_id: str):
        """
        Returns the latest policy version (we assume there are less than 1000 versions of the policy,
        if there are more, this may not be reliable). This relies on current Akamai API behaviour that listing
        all policies arranges the response in a way that the latest policy is in fact the 'first' (on the top).
        @param policy_id: is the identifier we need to find the policy
        @return: the latest policy contents or None if nothing was found or an error has occurred
        """
        all_policies = self.list_policy_versions(policy_id, 0, 1000)
        if all_policies is not None:
            all_policies_content = all_policies.get("content", None)
            return all_policies_content[0]
        return None

    def list_cloudlets(self):
        """
        Returns all available cloudlet types that we can access, as json-encoded value
        @return: all available cloudlet types, or None, if an error has occurred (http status was not 200)
        """
        api_path = "/cloudlets/v3/cloudlet-info"
        response = self.request_wrapper.send_get_request(api_path, {})
        if response.status_code == 200:
            return response.json()
        return None

    def list_groups(self):
        """
        Provides all groups with a request targeting the APIv2 to get the list of groups (including their member
        properties)
        @return: json representing the Akamai response or None, if an error has occurred (http status was not 200)
        """
        api_path = "/cloudlets/api/v2/group-info"
        response = self.request_wrapper.send_get_request(api_path, {})
        if response.status_code == 200:
            return response.json()
        return None

    def get_group_id(self):
        """
        Returns dict of groupIDs and their associated names
        @return: dict where groupId is the key and group name the value, or None, if nothing was found or
        an error has occurred
        """
        all_groups = self.list_groups()
        if all_groups is not None:
            groups = {}
            for element in all_groups:
                groups.update({element["groupId"]: element["groupName"]})
            return groups
        return None

    def get_group_id_by_name(self, group_name: str) -> object:
        """
        Provides the id of the group identified by its name
        @param group_name: is the string we're looking for
        @return: string representing the group_id or None in case nothing was found, or an error has occurred
        """
        all_groups = self.list_groups()
        if all_groups is not None:
            for element in all_groups:
                if element["groupName"].lower() == group_name.lower():
                    return element["groupId"]
        return None

    def create_shared_policy(self,
                             group_id: str,
                             policy_name: str,
                             description: str,
                             cloudlet_type: str) -> object:
        """
        Creates new shared policy and returns the Akamai response
        @param group_id: is the group_id where we want to create the new shared policy
        @param policy_name: is the name of the policy we want to assign (name should be descriptive enough
        so casual visitor of Akamai cloudlets is able to identify what rules does the policy contain (for example)
        @param description: is a short textual description of the policy
        @param cloudlet_type: is an 'enum' of the cloudlet policy types; permitted values are (for example): 'ER'
        @return: a dict of policy_id & policy_name or string representing the error message returned by Akamai
        """
        post_body = {
            "policyType": "SHARED",
            "cloudletType": cloudlet_type,
            "description": description,
            "groupId": group_id,
            "name": policy_name
        }
        api_path = "/cloudlets/v3/policies"
        response = self.request_wrapper.send_post_request(api_path, post_body)
        response_json = response.json()
        if response.status_code == 201:
            return {
                "policyId": response_json["id"],
                "policyName": response_json["name"]
            }

        return {
            "error": response_json["detail"]
        }

    def delete_shared_policy(self, policy_id: str):
        """
        Deletes shared policy identified by its id
        @param policy_id: is the policy id we want to remove
        @return: a string informing about the operation result
        """
        api_path = f"/cloudlets/v3/policies/{policy_id}"
        response = self.request_wrapper.send_delete_request(api_path)
        if response.status_code == 403:
            return f"No permissions to delete policy with id '{policy_id}'"
        if response.status_code == 404:
            return f"We could not find policy to delete - are you sure {policy_id} is correct?"
        if response.status_code == 204:
            return "Policy was deleted successfully"
        return f"Received status code we did not expect: {response.status_code}. Policy was NOT deleted."

    def delete_shared_policy_by_name(self, policy_name: str):
        policy_id = self.get_shared_policy_by_name(policy_name)
        if policy_id is None:
            print(f"Unable to find policy with name {policy_name}")
        else:
            return self.delete_shared_policy(str(policy_id))

    def get_active_properties(self,
                              policy_id: str,
                              page_number: str = "1",
                              page_size: str = "100"):
        """
        Returns all active properties that are assigned to the policy.
        @param policy_id: is the unique policy identifier
        @param page_number: in case you wish to paginate the results, you can request the records on specific page
        @param page_size: in case you wish to paginate the results, you can control the page size
        @return: json response representing the akamai response or None if we encountered an error (such as
        provided policy_id does not exist etc...)
        """
        api_path = f"/cloudlets/v3/policies/{policy_id}/properties"
        query_params = {
            "page": page_number,
            "size": page_size
        }
        response = self.request_wrapper.send_get_request(api_path, query_params)
        if response.status_code == 200:
            return response.json()
        return None

    def get_policy_version(self,
                           policy_id: str,
                           policy_version: str):
        """
        Returns information about a shared policy version, including match rules for a
        Cloudlet that you're using and whether its locked for changes.
        @param policy_id: is the policy's unique identifier
        @param policy_version: is the policy version we're interested in
        @return: json response representing the information you're looking for or None in case
        nothing was found (for example policy_id was incorrect or version does not exist)
        """
        api_path = f"/cloudlets/v3/policies/{policy_id}/versions/{policy_version}"
        response = self.request_wrapper.send_get_request(api_path, {})
        if response.status_code == 200:
            return response.json()
        return None

    def clone_non_shared_policy(self,
                                policy_id: str,
                                additional_version: list,
                                shared_policy_name: str,
                                group_id: str):
        """
        Clones the staging, production, and last modified versions of a non-shared (API v2) or shared policy
        into a new shared policy.
        @param group_id: is the id of the group where you wish to store the new policy
        @param policy_id: is the unique identifier of non-shared (api v2) policy
        @param additional_version: additional version numbers you wish to 'copy' from the old API v2 policy
        @param shared_policy_name: new name of the policy (technically we're creating a copy of the existing
        API v2 policy)
        @return: policy_id of the new (API v3) policy or None in case something went wrong
        """
        api_path = f"/cloudlets/v3/policies/{policy_id}/clone"
        post_body = {
            "additionalVersions": additional_version,
            "groupId": group_id,
            "newName": shared_policy_name
        }

        response = self.request_wrapper.send_post_request(api_path, post_body)
        if response.status_code == 200:
            json_response = response.json()
            return json_response["id"]
        return None

    def activate_policy(self, policy_id: str,
                        network: str,
                        operation: str,
                        policy_version: str) -> bool:
        """
        Activates or deactivates the selected Cloudlet policy version on the staging or production networks
        @param policy_version: is the policy version that is to be (de)activated
        @param operation: tells the method what we want it to do (activate or deactivate); permitted values are either
        'ACTIVATION' or 'DEACTIVATION'
        @param network: tells the method what Akamai network we want to perform such operation; permitted values are
        either 'PRODUCTION' or 'STAGING'
        @param policy_id: is the policy identifier - that tells us which policy is to be activated
        @return: bool indicating whether the (de)activation request was accepted by Akamai or not (true if yes,
        false if no)
        """
        if self.is_akamai_network(network) is not True:
            raise IncorrectInputParameter(f"Network parameter (akamai_network) must be either 'PRODUCTION' or 'STAGE'."
                                          f"Instead, it was {network}")

        if self.is_correct_operation(operation) is not True:
            raise IncorrectInputParameter(f"Operation parameter (operation) must be either 'ACTIVATION' or "
                                          f"'DEACTIVATION'. Instead, it was {operation}")

        api_path = f"/cloudlets/v3/policies/{policy_id}/activations"
        post_body = {
            "network": network,
            "operation": operation,
            "policyVersion": policy_version
        }

        response = self.request_wrapper.send_post_request(api_path, post_body)
        if response.status_code == 202:
            json_response = response.json()
            result = json_response["status"]
            if result == "SUCCESS":
                return True
        return False

    @staticmethod
    def is_akamai_network(obj):
        try:
            AkamaiNetworks(obj)
        except ValueError:
            return False
        return True

    @staticmethod
    def is_correct_operation(obj):
        try:
            ActivationOperations(obj)
        except ValueError:
            return False
        return True
