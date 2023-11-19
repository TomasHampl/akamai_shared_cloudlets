import os


def get_shared_policies_text(json_response: dict):
    """
    Extracts the policy name and policy id from the response coming back from akamai and returns it as text
    @param json_response: is a dict representing the json string
    @return: python dictionary with policy name as key and policy id as value
    """
    response = {}
    policies = json_response["content"]
    for policy_object in policies:
        policy_name = policy_object["name"]
        policy_id = policy_object["id"]
        response[policy_name] = policy_id

    return response


def get_home_folder(edgerc_location: str):
    """
    Returns the real, OS-agnostics, reference to home folder. If the path is not determined to belong to 'home folder',
    we return the original provided location.
    @param edgerc_location: is the location where we should be able to find the edgerc (akamai credentials file)
    @return: OS-agnostic reference to home folder
    """
    return os.path.expanduser(edgerc_location)
