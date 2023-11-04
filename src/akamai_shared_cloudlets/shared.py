def get_shared_policies_text(json_response: str):
    """
    Extracts the policy name and policy id from the response coming back from akamai and returns it as text
    @param json_response: is a string representing the json string
    @return: python dictionary with policy name as key and policy id as value
    """
    response = {}
    policies = json_response["content"]
    for policy_object in policies:
        policy_name = policy_object["name"]
        policy_id = policy_object["id"]
        response[policy_name] = policy_id

    return response
