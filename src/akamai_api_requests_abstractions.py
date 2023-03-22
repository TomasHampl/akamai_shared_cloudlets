# library functions
from src.akamai_http_requests_wrapper import AkamaiRequestWrapper


def get_request_wrapper(edgerc_location: str = '~/.edgerc'):
    return AkamaiRequestWrapper(edgerc_location)


def list_shared_policies(edgerc_location: str = '~/.edgerc'):
    """
    listSharedPolicies is a method that abstracts the Akamai API call to get all shared policies available
     to the provided credentials. What policies are available to the credentials depends on the 'edgerc' location.

    If the edgerc location is not provided, it defaults to ~/.edgerc
    """
    request_wrapper = get_request_wrapper(edgerc_location)
    api_path = "/cloudlets/v3/policies"
    response = request_wrapper.send_get_request(api_path, {})
    return response.json()


def get_shared_policy_by_name(policy_name: str, edgerc_location: str = '~/.edgerc') -> object:
    """
    Returns Shared cloudlet policyId based on the policy name. If not found, returns None...
    @param policy_name: is the name of the policy we'll be looking for in all policies
    @param edgerc_location: is the location of the 'edgerc', Akamai credentials file
    @return: string representing the policyId or None (in case nothing was found)
    """
    response_json = list_shared_policies(edgerc_location)
    policies = response_json["content"]
    for policyObject in policies:
        if policyObject['name'] == policy_name:
            return policyObject['id']
    return None


def get_shared_policies_by_approximate_name(policy_name: str, edgerc_location: str = '~/.edgerc'):
    """
    Returns a dictionary of policy names (as key) and their IDs (as value) where policy name contains the provided
    search string. If nothing is found, returns an empty dictionary
    """
    result_list = {}
    response_json = list_shared_policies(edgerc_location)
    all_policies = response_json["content"]
    for policyObject in all_policies:
        if policy_name.lower() in policyObject["name"]:
            policy = policyObject["name"]
            policy_id = policyObject["id"]
            result_list.update({policy: policy_id})
    return result_list


def get_policy_by_id(policy_id: str, edgerc_location='~/.edgerc') -> object:
    """
    Returns the json string representing the shared policy identified by the provided 'policyId'
    @param policy_id: is the policy_id we're looking for
    @param edgerc_location: is a location where we can access the 'edgerc' file, containing Akamai credentials
    @return: json representing the Akamai response
    """
    request_wrapper = get_request_wrapper(edgerc_location)
    api_path = f"/cloudlets/v3/policies/{policy_id}"
    response = request_wrapper.send_get_request(api_path, {})
    return response.json()


def list_policy_versions(policy_id: str, page_number: str, page_size: str, edgerc_location: str = '~/.edgerc'):
    """
    Fetches the policy versions (including their metadata, but not their contents)
    """
    request_wrapper = get_request_wrapper(edgerc_location)
    api_path = f"/cloudlets/v3/policies/{policy_id}/versions"
    query_params = {
        "page": page_number,
        "size": page_size
    }
    response = request_wrapper.send_get_request(api_path, query_params)
    return response.json()


def get_latest_policy_version(policy_id: str, edgerc_location: str = '~/.edgerc'):
    """
    Returns the json string representing the latest version of a redirect policy
    """
    latest_policy = get_latest_policy(policy_id, edgerc_location)
    return latest_policy["version"]


def get_latest_policy(policy_id: str, edgerc_location: str = '~/.edgerc'):
    """
    Returns the latest policy version - returns only the ID, not the contents itself.
    """
    all_policies = list_policy_versions(policy_id, "0", "100", edgerc_location)
    all_policies_content = all_policies.get("content", None)
    return all_policies_content[0]


def list_cloudlets(edgerc_location: str = '~/.edgerc'):
    """
    Returns all available cloudlet types
    """
    request_wrapper = get_request_wrapper(edgerc_location)
    api_path = "/cloudlets/v3/cloudlet-info"
    response = request_wrapper.send_get_request(api_path, {})
    return response.json()


def list_groups(edgerc_location: str = '~/.edgerc'):
    """
    Provides all groups with a request targeting the APIv2 to get the list of groups (including their member properties)
    @type edgerc_location: object
    @param edgerc_location: is a location of the 'edgerc' file that contains the Akamai credentials
    @return: json representing the Akamai response
    """
    request_wrapper = get_request_wrapper(edgerc_location)
    api_path = "/cloudlets/api/v2/group-info"
    response = request_wrapper.send_get_request(api_path, {})
    return response.json()


def get_group_id(edgerc_location: str = '~/.edgerc'):
    """
    Returns dict of groupIDs and their associated names
    """
    all_groups = list_groups(edgerc_location)
    groups = {}
    for element in all_groups:
        groups.update({element["groupId"]: element["groupName"]})
    return groups


def get_group_id_by_name(group_name: str, edgerc_location: str = '~/.edgerc') -> object:
    """
    Provides the id of the group identified by its name
    @param group_name: is the string we're looking for
    @param edgerc_location: is a location of the 'edgerc' file that contains the Akamai credentials
    @return: string representing the group_id or None in case nothing was found
    """
    all_groups = list_groups(edgerc_location)
    for element in all_groups:
        if element["groupName"].lower() == group_name.lower():
            return element["groupId"]
    return None


def create_shared_policy(group_id: str,
                         policy_name: str,
                         description: str,
                         cloudlet_type: str,
                         edgerc_location: str = '~/.edgerc') -> object:
    """
    Creates new shared policy and returns the Akamai response
    @param group_id: is the group_id where we want to create the new shared policy
    @param policy_name: is the name of the policy we want to assign (name should be descriptive enough so casual visitor
     of Akamai cloudlets is able to identify what rules does the policy contain (for example)
    @param description: is a short textual description of the policy
    @param cloudlet_type: is an 'enum' of the cloudlet policy types; permitted values are (for example): 'ER'
    @param edgerc_location: is a location of the 'edgerc' file that contains the Akamai credentials
    @return: a dict of policy_id & policy_name or string representing the error message returned by Akamai
    """
    post_body = {
        "policyType": "SHARED",
        "cloudletType": cloudlet_type,
        "description": description,
        "groupId": group_id,
        "name": policy_name
    }
    request_wrapper = get_request_wrapper(edgerc_location)
    api_path = "/cloudlets/v3/policies"
    response = request_wrapper.send_post_request(api_path, post_body)
    response_json = response.json()
    if response.status_code == 201:
        return {
            "policyId": response_json["id"],
            "policyName": response_json["name"]
        }

    return {
        "error": response_json["detail"]
    }


def delete_shared_policy(policy_id: str, edgerc_location: str = '~/.edgerc'):
    """
    Deletes shared policy identified by its id
    @param policy_id: is the policy id we want to remove
    @param edgerc_location: is a location of the 'edgerc' file that contains the Akamai credentials
    @return: a string informing about the operation result
    """
    request_wrapper = get_request_wrapper(edgerc_location)
    api_path = f"/cloudlets/v3/policies/{policy_id}"
    response = request_wrapper.send_delete_request(api_path)
    if response.status_code == 403:
        return f"No permissions to delete policy with id '{policy_id}'"
    if response.status_code == 404:
        return f"We could not find policy to delete - are you sure {policy_id} is correct?"
    return "Policy was deleted successfully"


def delete_shared_policy_by_name(policy_name: str, edgerc_location: str = '~/.edgerc'):
    policy_id = get_shared_policy_by_name(policy_name, edgerc_location)
    if policy_id is None:
        print(f"Unable to find policy with name {policy_name}")
    else:
        return delete_shared_policy(str(policy_id), edgerc_location)


def get_active_properties(policy_id: str,
                          page_number: str = "1",
                          page_size: str = "100",
                          edgerc_location: str = '~/.edgerc'):
    """
    Returns all active properties that are assigned to the policy.
    @param policy_id: is the unique policy identifier
    @param page_number: in case you wish to paginate the results, you can request the records on specific page
    @param page_size: in case you wish to paginate the results, you can control the page size
    @param edgerc_location: is a location of the 'edgerc' file that contains the Akamai credentials
    @return: json response representing the akamai response or None if we encountered an error (such as
    provided policy_id does not exist etc...)
    """
    request_wrapper = get_request_wrapper(edgerc_location)
    api_path = f"/cloudlets/v3/policies/{policy_id}/properties"
    query_params = {
        "page": page_number,
        "size": page_size
    }
    response = request_wrapper.send_get_request(api_path, query_params)
    if response.status_code == 200:
        return response.json()
    return None


def get_policy_version(policy_id: str,
                       policy_version: str,
                       edgerc_location='~/.edgerc_location'):
    """
    Returns information about a shared policy version, including match rules for a
    Cloudlet that you're using and whether its locked for changes.
    @param policy_id: is the policy's unique identifier
    @param policy_version: is the policy version we're interested in
    @param edgerc_location: is a location of the 'edgerc' file that contains the Akamai credentials
    @return: json response representing the information you're looking for or None in case
    nothing was found (for example policy_id was incorrect or version does not exist)
    """
    request_wrapper = get_request_wrapper(edgerc_location)
    api_path = f"/cloudlets/v3/policies/{policy_id}/versions/{policy_version}"
    response = request_wrapper.send_get_request(api_path, {})
    if response.status_code == 200:
        return response.json()
    return None


def clone_non_shared_policy(policy_id: str,
                            additional_version: list,
                            shared_policy_name: str,
                            group_id: str,
                            edgerc_location: str = '~/.edgerc'):
    """
    Clones the staging, production, and last modified versions of a non-shared (API v2) or shared policy
    into a new shared policy.
    @param group_id: is the id of the group where you wish to store the new policy
    @param policy_id: is the unique identifier of non-shared (api v2) policy
    @param additional_version: additional version numbers you wish to 'copy' from the old API v2 policy
    @param shared_policy_name: new name of the policy (technically we're creating a copy of the existing
    API v2 policy)
    @param edgerc_location: is a location of the 'edgerc' file that contains the Akamai credentials
    @return: policy_id of the new (API v3) policy or None in case something went wrong
    """
    request_wrapper = get_request_wrapper(edgerc_location)
    api_path = f"/cloudlets/v3/policies/{policy_id}/clone"
    post_body = {
        "additionalVersions": additional_version,
        "groupId": group_id,
        "newName": shared_policy_name
    }

    response = request_wrapper.send_post_request(api_path, post_body)
    if response.status_code == 200:
        json_response = response.json()
        return json_response["id"]
    return None
