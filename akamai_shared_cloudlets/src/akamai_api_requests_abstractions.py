# library functions
from akamai_http_requests_wrapper import AkamaiRequestWrapper
from akamai_project_constants import DEFAULT_EDGERC_LOCATION


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
        self.request_wrapper = AkamaiRequestWrapper(edgerc_location)

    def list_shared_policies(self):
        """
        listSharedPolicies is a method that abstracts the Akamai API call to get all shared policies available
         to the provided credentials. What policies are available to the credentials depends on the 'edgerc' location.

        If the edgerc location is not provided, it defaults to ~/.edgerc
        """
        api_path = "/cloudlets/v3/policies"
        response = self.request_wrapper.send_get_request(api_path, {})
        return response.json()

    def get_shared_policy_by_name(self, policy_name: str) -> object:
        """
        Returns Shared cloudlet policyId based on the policy name. If not found, returns None...
        @param policy_name: is the name of the policy we'll be looking for in all policies
        @return: string representing the policyId or None (in case nothing was found)
        """
        response_json = self.list_shared_policies()
        policies = response_json["content"]
        for policy_object in policies:
            if policy_object['name'] == policy_name:
                return policy_object['id']
        return None

    def get_shared_policies_by_approximate_name(self, policy_name: str):
        """
        Returns a dictionary of policy names (as key) and their IDs (as value) where policy name contains the provided
        search string. If nothing is found, returns an empty dictionary
        """
        result_list = {}
        response_json = self.list_shared_policies()
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
        @return: json representing the Akamai response
        """
        api_path = f"/cloudlets/v3/policies/{policy_id}"
        response = self.request_wrapper.send_get_request(api_path, {})
        return response.json()

    def list_policy_versions(self, policy_id: str, page_number: str, page_size: str):
        """
        Fetches the policy versions (including their metadata, but not their contents)
        """
        api_path = f"/cloudlets/v3/policies/{policy_id}/versions"
        query_params = {
            "page": page_number,
            "size": page_size
        }
        response = self.request_wrapper.send_get_request(api_path, query_params)
        return response.json()

    def get_latest_policy_version(self, policy_id: str):
        """
        Returns the json string representing the latest version of a redirect policy
        """
        latest_policy = self.get_latest_policy(policy_id)
        return latest_policy["version"]

    def get_latest_policy(self, policy_id: str):
        """
        Returns the latest policy version - returns only the ID, not the contents itself.
        """
        all_policies = self.list_policy_versions(policy_id, "0", "100")
        all_policies_content = all_policies.get("content", None)
        return all_policies_content[0]

    def list_cloudlets(self):
        """
        Returns all available cloudlet types that we can access
        """
        api_path = "/cloudlets/v3/cloudlet-info"
        response = self.request_wrapper.send_get_request(api_path, {})
        return response.json()

    def list_groups(self):
        """
        Provides all groups with a request targeting the APIv2 to get the list of groups (including their member properties)
        @return: json representing the Akamai response
        """
        api_path = "/cloudlets/api/v2/group-info"
        response = self.request_wrapper.send_get_request(api_path, {})
        return response.json()

    def get_group_id(self):
        """
        Returns dict of groupIDs and their associated names
        """
        all_groups = self.list_groups()
        groups = {}
        for element in all_groups:
            groups.update({element["groupId"]: element["groupName"]})
        return groups

    def get_group_id_by_name(self, group_name: str) -> object:
        """
        Provides the id of the group identified by its name
        @param group_name: is the string we're looking for
        @return: string representing the group_id or None in case nothing was found
        """
        all_groups = self.list_groups()
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
        @param policy_name: is the name of the policy we want to assign (name should be descriptive enough so casual visitor
         of Akamai cloudlets is able to identify what rules does the policy contain (for example)
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
