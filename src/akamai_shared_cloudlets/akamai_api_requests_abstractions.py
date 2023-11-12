# library functions

from . import akamai_enums
from . import akamai_project_constants
from . import exceptions
from . import http_requests


def list_shared_policies(edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    listSharedPolicies is a method that abstracts the Akamai API call to get all shared policies available
     to the provided credentials. What policies are available to the credentials depends on the permissions
     assigned to the API user that created the credentials.

    There are no parameters to be provided.
    @return: json response from the API call (if http status code was 200) or None in case it was
    anything else.
    """
    api_path = "/cloudlets/v3/policies"
    response = http_requests.send_get_request(api_path, {}, edgerc_location)
    if response.status_code == 200:
        return response.json()
    return None


def get_shared_policy_by_name(
        policy_name: str,
        edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION) -> dict:
    """
    Returns Shared cloudlet policyId based on the policy name. If not found, returns None... If no match is found using
    exact comparison, we return all items matching partially
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @param policy_name: is the name of the policy we'll be looking for in all policies
    @return: dict that contains the policy (or policies) matching the name
    """
    response_dict = {}
    response_json = list_shared_policies(edgerc_location)
    if response_json is not None:
        policies = response_json["content"]
        for policy_object in policies:
            if policy_object['name'] == policy_name:
                policy_id = policy_object['id']
                response_dict.update({policy_name: policy_id})
                return response_dict
    return get_policies_by_approximate_name(response_json, policy_name)


def get_policies_by_approximate_name(response_json, policy_name: str) -> dict:
    """
    Parses the Akamai response related to 'get shared policies' and returns a dict of the items partially matching
    the provided policy_name. May contain 0 items ...
    @param response_json: is a string representing the Akamai response
    @param policy_name: is a string representing the policy name we want to find
    @return: a dict with policy name as key and its id as value
    """
    result_list = {}
    if response_json is not None:
        all_policies = response_json["content"]
        for policy_object in all_policies:
            if policy_name.lower() in policy_object["name"]:
                policy = policy_object["name"]
                policy_id = policy_object["id"]
                result_list.update({policy: policy_id})
    return result_list


def get_shared_policies_by_approximate_name(
        policy_name: str,
        edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Provides a dictionary of policy name (as key) and their IDs (as value) where policy name contains the provided
    search string. If request failed (http status code != 200), or nothing was found, returns empty dictionary.
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @param policy_name: is a string we want to find in the shared policies (needle)
    @return: dictionary of policy names & ids, if nothing was found, returns empty dict
    """
    response_json = list_shared_policies(edgerc_location)
    return get_policies_by_approximate_name(response_json, policy_name)


def get_policy_by_id(policy_id: str, edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION) -> object:
    """
    Returns the json string representing the shared policy identified by the provided 'policyId'
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @param policy_id: is the policy_id we're looking for
    @return: json representing the Akamai response or None if nothing was found (or request to API failed)
    """
    api_path = f"/cloudlets/v3/policies/{policy_id}"
    response = http_requests.send_get_request(api_path, {}, edgerc_location)
    if response.status_code == 200:
        return response.json()
    return None


def list_policy_versions(
        policy_id: str,
        page_number: int,
        page_size: int,
        edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Fetches the policy versions (including their metadata, but not their contents)
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
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
    response = http_requests.send_get_request(api_path, query_params, edgerc_location)
    if response.status_code == 200:
        return response.json()
    return None


def get_latest_policy_version(policy_id: str, edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Returns the latest version number of the policy identified by its ID
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @param policy_id: is the identifier we need to find the policy
    @return: version number or None if nothing was found or an error occurred
    """
    latest_policy = get_latest_policy(policy_id, edgerc_location)
    if latest_policy is not None:
        return latest_policy["version"]
    return None


def get_latest_policy(policy_id: str, edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Returns the latest policy version (we assume there are less than 1000 versions of the policy,
    if there are more, this may not be reliable). This relies on current Akamai API behaviour that listing
    all policies arranges the response in a way that the latest policy is in fact the 'first' (on the top).
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @param policy_id: is the identifier we need to find the policy
    @return: the latest policy contents or None if nothing was found or an error has occurred
    """
    all_policies = list_policy_versions(policy_id, 0, 1000, edgerc_location)
    if all_policies is not None:
        all_policies_content = all_policies.get("content", None)
        return all_policies_content[0]
    return None


def list_cloudlets(edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Returns all available cloudlet types that we can access, as json-encoded value
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @return: all available cloudlet types, or None, if an error has occurred (http status was not 200)
    """
    api_path = "/cloudlets/v3/cloudlet-info"
    response = http_requests.send_get_request(api_path, {}, edgerc_location)
    if response.status_code == 200:
        return response.json()
    return None


def list_groups(edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Provides all groups with a request targeting the APIv2 to get the list of groups (including their member
    properties)
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @return: json representing the Akamai response or None, if an error has occurred (http status was not 200)
    """
    api_path = "/cloudlets/api/v2/group-info"
    response = http_requests.send_get_request(api_path, {}, edgerc_location)
    if response.status_code == 200:
        return response.json()
    return None


def get_group_id(edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Returns dict of groupIDs and their associated names
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @return: dict where groupId is the key and group name the value, or None, if nothing was found or
    an error has occurred
    """
    all_groups = list_groups(edgerc_location)
    if all_groups is not None:
        groups = {}
        for element in all_groups:
            groups.update({element["groupId"]: element["groupName"]})
        return groups
    return None


def get_group_id_by_name(
        group_name: str,
        edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION) -> object:
    """
    Provides the id of the group identified by its name. Caution: returns the first entry found.
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @param group_name: is the string we're looking for
    @return: string representing the group_id or None in case nothing was found, or an error has occurred
    """
    all_groups = list_groups(edgerc_location)
    if all_groups is not None:
        for element in all_groups:
            if element["groupName"].lower() == group_name.lower():
                return element["groupId"]
            if group_name.lower() in element["groupName"].lower():
                return element["groupId"]
    return None


def create_shared_policy(group_id: str,
                         policy_name: str,
                         description: str,
                         cloudlet_type: str,
                         edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION) -> object:
    """
    Creates new shared policy and returns the Akamai response
    @param group_id: is the group_id where we want to create the new shared policy
    @param policy_name: is the name of the policy we want to assign (name should be descriptive enough
    so casual visitor of Akamai cloudlets is able to identify what rules does the policy contain (for example)
    @param description: is a short textual description of the policy
    @param cloudlet_type: is an 'enum' of the cloudlet policy types; permitted values are (for example): 'ER'
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
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
    response = http_requests.send_post_request(api_path, post_body, edgerc_location)
    response_json = response.json()
    if response.status_code == 201:
        return {
            "policyId": response_json["id"],
            "policyName": response_json["name"]
        }

    return response_json["errors"]


def delete_shared_policy(policy_id: str, edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Deletes shared policy identified by its id
    @param policy_id: is the policy id we want to remove
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @return: a string informing about the operation result
    """
    api_path = f"/cloudlets/v3/policies/{policy_id}"
    response = http_requests.send_delete_request(api_path, edgerc_location)
    if response.status_code == 403:
        return f"No permissions to delete policy with id '{policy_id}'"
    if response.status_code == 404:
        return f"We could not find policy to delete - are you sure {policy_id} is correct?"
    if response.status_code == 204:
        return "Policy was deleted successfully"
    return f"Received status code we did not expect: {response.status_code}. Policy was NOT deleted."


def delete_shared_policy_by_name(
        policy_name: str,
        edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Deletes shared policy based on the provided name. This request first downloads all available policies from
    Akamai and then looks through the returned data to determine the policy (therefore, if 'user' knows the
    policy he/she wants to delete, it would be more effective to call the 'delete_shared_policy' and providing
    the policy directly).
    @param policy_name: is the name of the policy you wish to delete, needs to be exact
    match for the lookup to work
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @return: string response indicating success / error message
    """
    policy = get_shared_policy_by_name(policy_name, edgerc_location)
    if len(policy) == 0:
        print(f"Unable to find policy with name {policy_name}. No policy was deleted")
    elif len(policy) == 1:
        policy_id = next(iter(policy.values()))
        return delete_shared_policy(str(policy_id), edgerc_location)
    else:
        print(f"More than one policies returned based on name '{policy_name}'. Not deleting anything...")


def get_active_properties(policy_id: str,
                          page_number: str = "1",
                          page_size: str = "100",
                          edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Returns all active properties that are assigned to the policy.
    @param policy_id: is the unique policy identifier
    @param page_number: in case you wish to paginate the results, you can request the records on specific page
    @param page_size: in case you wish to paginate the results, you can control the page size
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @return: json response representing the akamai response or None if we encountered an error (such as
    provided policy_id does not exist etc...)
    """
    api_path = f"/cloudlets/v3/policies/{policy_id}/properties"
    query_params = {
        "page": page_number,
        "size": page_size
    }
    response = http_requests.send_get_request(api_path, query_params, edgerc_location)
    if response.status_code == 200:
        return response.json()
    return None


def get_policy_version(policy_id: str,
                       policy_version: str,
                       edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Returns information about a shared policy version, including match rules for a
    Cloudlet that you're using and whether its locked for changes.
    @param policy_id: is the policy's unique identifier
    @param policy_version: is the policy version we're interested in
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @return: json response representing the information you're looking for or None in case
    nothing was found (for example policy_id was incorrect or version does not exist)
    """
    api_path = f"/cloudlets/v3/policies/{policy_id}/versions/{policy_version}"
    response = http_requests.send_get_request(api_path, {}, edgerc_location)
    if response.status_code == 200:
        return response.json()
    return None


def clone_non_shared_policy(policy_id: str,
                            additional_version: list,
                            shared_policy_name: str,
                            group_id: str,
                            edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Clones the staging, production, and last modified versions of a non-shared (API v2) or shared policy
    into a new shared policy.
    @param group_id: is the id of the group where you wish to store the new policy
    @param policy_id: is the unique identifier of non-shared (api v2) policy
    @param additional_version: additional version numbers you wish to 'copy' from the old API v2 policy
    @param shared_policy_name: new name of the policy (technically we're creating a copy of the existing
    API v2 policy)
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @return: policy_id of the new (API v3) policy or None in case something went wrong
    """
    api_path = f"/cloudlets/v3/policies/{policy_id}/clone"
    post_body = {
        "additionalVersions": additional_version,
        "groupId": group_id,
        "newName": shared_policy_name
    }

    response = http_requests.send_post_request(api_path, post_body, edgerc_location)
    if response.status_code == 200:
        json_response = response.json()
        return json_response["id"]
    return None


def activate_policy(policy_id: str,
                    network: str,
                    operation: str,
                    policy_version: str,
                    edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION) -> bool:
    """
    Activates or deactivates the selected Cloudlet policy version on the staging or production networks
    @param policy_version: is the policy version that is to be (de)activated
    @param operation: tells the method what we want it to do (activate or deactivate); permitted values are either
    'ACTIVATION' or 'DEACTIVATION'
    @param network: tells the method what Akamai network we want to perform such operation; permitted values are
    either 'PRODUCTION' or 'STAGING'
    @param policy_id: is the policy identifier - that tells us which policy is to be activated
    @param edgerc_location: is the location of EdgeRC file that we use to extract the authentication credentials for
     your API user
    @return bool indicating whether the (de)activation request was accepted by Akamai or not (true if yes,
    false if no)
    """
    if is_akamai_network(network.lower()) is not True:
        raise exceptions.IncorrectInputParameter(f"Network parameter (akamai_network) must be either 'production' "
                                                 f"or 'stage. Instead, it was {network}")

    if is_correct_operation(operation.lower()) is not True:
        raise exceptions.IncorrectInputParameter(f"Operation parameter (operation) must be either 'activation' or "
                                                 f"'deactivation'. Instead, it was {operation}")

    api_path = f"/cloudlets/v3/policies/{policy_id}/activations"
    post_body = {
        "network": network,
        "operation": operation,
        "policyVersion": policy_version
    }

    response = http_requests.send_post_request(api_path, post_body, edgerc_location)
    if response.status_code == 202:
        json_response = response.json()
        result = json_response["status"]
        if result == "SUCCESS":
            return True
    return False


def is_akamai_network(obj):
    try:
        akamai_enums.AkamaiNetworks(obj)
    except ValueError:
        return False
    return True


def is_correct_operation(obj):
    try:
        akamai_enums.ActivationOperations(obj)
    except ValueError:
        return False
    return True
