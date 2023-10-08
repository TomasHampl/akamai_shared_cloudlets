import json
import os
from . import common_test_func as test_common
from os import path
import pytest
from akamai.edgegrid import EdgeRc
from src.akamai_shared_cloudlets.akamai_api_requests_abstractions import AkamaiApiRequestsAbstractions


def get_request_loc():
    return "akamai_shared_cloudlets.src.akamai_http_requests_wrapper.AkamaiRequestWrapper.send_get_request"


def get_sample_json(api_call):
    folder_path = os.path.dirname(__file__)
    file_name = path.normpath(f"{folder_path}/supplemental/{api_call}.json")
    print(f"file name: {file_name}")
    if path.isfile(file_name):
        with open(file_name, mode="r") as json_file:
            return json.load(json_file)
    else:
        raise FileNotFoundError(f"Could not find the file {file_name}")


def new_negative_send_get_request():
    return get_sample_json('list_shared_policies')


def get_akamai_host(edgerc_path):
    print(os.listdir())
    edge_rc = EdgeRc(edgerc_path)
    return edge_rc.get('default', 'host')


@pytest.fixture()
def api():
    """
    Instantiates the AkamaiApiRequestsAbstractions object and returns it, ready for tests
    @return: an instance of AkamaiApiRequestsAbstractions
    """
    return AkamaiApiRequestsAbstractions(test_common.get_sample_edgerc())


@pytest.fixture()
def api_destination():
    """
    Provides the akamai host from the 'sample' edgerc file
    @return: a String representing the Akamai hostname obtained from the credentials file
    """
    return get_akamai_host(test_common.get_sample_edgerc())


def test_list_shared_policies(requests_mock, api, api_destination):
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies", json=get_sample_json("list_shared_policies"))
    response = api.list_shared_policies()
    assert response is not None


def test_list_shared_policies_negative(requests_mock, api, api_destination):
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies", status_code=404)
    response = api.list_shared_policies()
    assert response is None


def test_find_shared_policy_by_name(requests_mock, api, api_destination):
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies", json=get_sample_json("list_shared_policies"))
    response = api.get_shared_policy_by_name("static_assets_redirector")
    assert response == 1001


def test_find_shared_policy_by_name_negative(requests_mock, api, api_destination):
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies", json=get_sample_json("list_shared_policies"))
    response = api.get_shared_policy_by_name("not_present")
    assert response is None


def test_find_shared_policy_by_approximate_name(requests_mock, api, api_destination):
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies", json=get_sample_json("list_shared_policies"))
    response = api.get_shared_policies_by_approximate_name("assets")
    assert response == {"static_assets_redirector": 1001}


def test_find_shared_policy_by_approximate_name_negative(requests_mock, api, api_destination):
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies", json=get_sample_json("list_shared_policies"))
    response = api.get_shared_policies_by_approximate_name("ssssss")
    assert response == {}


def test_get_policy_by_id(requests_mock, api, api_destination):
    policy_id = "1001"
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies/{policy_id}",
                      json=get_sample_json("get_a_policy"))
    response = api.get_policy_by_id("1001")
    assert response is not None


def test_get_policy_by_id_negative(requests_mock, api, api_destination):
    policy_id = "1001"
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies/{policy_id}",
                      status_code=401)
    response = api.get_policy_by_id("1001")
    assert response is None


def test_list_policy_versions(requests_mock, api, api_destination):
    policy_id = "1001"
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies/{policy_id}/versions",
                      json=get_sample_json('list_policy_versions'))
    response = api.list_policy_versions(policy_id, 3, 100)
    assert response is not None
    content = response["content"]
    assert content[0]["description"] == "Initial version"


def test_list_policy_versions_negative_response(requests_mock, api, api_destination):
    policy_id = "1001"
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies/{policy_id}/versions",
                      status_code=404)
    response = api.list_policy_versions(policy_id, 3, 100)
    assert response is None


def test_get_latest_policy(requests_mock, api, api_destination):
    policy_id = "1001"
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies/{policy_id}/versions",
                      json=get_sample_json('list_policy_versions'))
    response = api.get_latest_policy(policy_id)
    assert response["description"] == "Initial version"


def test_get_latest_policy_negative_response(requests_mock, api, api_destination):
    policy_id = "1001"
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies/{policy_id}/versions",
                      status_code=404)
    response = api.get_latest_policy(policy_id)
    assert response is None


def test_get_latest_policy_version(requests_mock, api, api_destination):
    policy_id = "1001"
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies/{policy_id}/versions",
                      json=get_sample_json('list_policy_versions'))
    response = api.get_latest_policy_version(policy_id)
    assert response == 1


def test_get_latest_policy_version_negative_response(requests_mock, api, api_destination):
    policy_id = "1001"
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies/{policy_id}/versions",
                      status_code=404)
    response = api.get_latest_policy_version(policy_id)
    assert response is None


def test_get_cloudlets(requests_mock, api, api_destination):
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/cloudlet-info", json=get_sample_json("cloudlet_info"))
    response = api.list_cloudlets()
    assert response is not None
    assert response[0]["cloudletName"] == "API_PRIORITIZATION"


def test_list_groups(requests_mock, api, api_destination):
    url = f"https://{api_destination}/cloudlets/api/v2/group-info"
    print(f"URL in test: '{url}'")
    requests_mock.get(f"{url}", json=get_sample_json("list_groups"))
    response = api.list_groups()
    assert response is not None
    assert response[0]["groupName"] == "Master Group Name"


def test_get_groups_ids(requests_mock, api, api_destination):
    url = f"https://{api_destination}/cloudlets/api/v2/group-info"
    print(f"URL in test: '{url}'")
    requests_mock.get(f"{url}", json=get_sample_json("list_groups"))
    response = api.get_group_id()
    assert response[1234] == "Master Group Name"


@pytest.mark.parametrize("group_name_input", ["group name", "master group name"])
def test_get_group_id_by_name(requests_mock, group_name_input, api, api_destination):
    url = f"https://{api_destination}/cloudlets/api/v2/group-info"
    print(f"URL in test: '{url}'")
    requests_mock.get(f"{url}", json=get_sample_json("list_groups"))
    response = api.get_group_id_by_name(group_name_input)
    assert response == 1234


def test_create_shared_policy(requests_mock, api, api_destination):
    url = f"https://{api_destination}/cloudlets/v3/policies"
    print(f"URL in test: '{url}'")
    requests_mock.post(f"{url}", json=get_sample_json('create_policy_ok_response'), status_code=201)
    response = api.create_shared_policy("123", "dummy-policy", "bla", "ER")
    assert response is not None
    assert response["policyId"] == 1001


def test_create_shared_policy_negative(requests_mock, api, api_destination):
    url = f"https://{api_destination}/cloudlets/v3/policies"
    print(f"URL in test: '{url}'")
    requests_mock.post(f"{url}", json=get_sample_json('create_policy_ko_response'), status_code=403)
    response = api.create_shared_policy("123", "dummy-policy", "bla", "ER")
    assert response is not None
    assert response[0]["detail"] == "User does not have view capability for Edge Redirector Cloudlet in group 120."


@pytest.mark.parametrize("status_codes", [204, 403, 404, 500])
def test_delete_shared_policy(requests_mock, api, api_destination, status_codes):
    policy_id = 1234
    url = f"https://{api_destination}/cloudlets/v3/policies/{policy_id}"
    requests_mock.delete(f"{url}", status_code=status_codes)
    response = api.delete_shared_policy(str(policy_id))
    if status_codes == 204:
        assert response == "Policy was deleted successfully"
    if status_codes == 403:
        assert response == f"No permissions to delete policy with id '{policy_id}'"
    if status_codes == 404:
        assert response == f"We could not find policy to delete - are you sure {policy_id} is correct?"
    if status_codes == 500:
        assert "Received status code we did not expect" in response


def test_delete_shared_policy_by_name(requests_mock, api, api_destination):
    policy_id = 1001
    url_policies = f"https://{api_destination}/cloudlets/v3/policies"
    url_deletion = f"https://{api_destination}/cloudlets/v3/policies/{policy_id}"
    requests_mock.get(f"{url_policies}", json=get_sample_json("list_shared_policies"))
    requests_mock.delete(f"{url_deletion}", status_code=204)
    response = api.delete_shared_policy_by_name("static_assets_redirector")
    assert response == "Policy was deleted successfully"


def test_get_active_properties(requests_mock, api, api_destination):
    policy_id = 1001
    url = f"https://{api_destination}/cloudlets/v3/policies/{policy_id}/properties"
    requests_mock.get(f"{url}", json=get_sample_json("get_active_properties"))
    response = api.get_active_properties(str(policy_id))
    assert response is not None
    assert response["content"][0]["name"] == "property"


@pytest.mark.parametrize("status_codes", [403, 404])
def test_get_active_properties_negatives(requests_mock, api, api_destination, status_codes):
    policy_id = 1001
    url = f"https://{api_destination}/cloudlets/v3/policies/{policy_id}/properties"
    requests_mock.get(f"{url}", status_code=status_codes)
    response = api.get_active_properties(str(policy_id))
    assert response is None


@pytest.mark.parametrize("status_codes", [200, 403, 404])
def test_get_policy_version(requests_mock, api, api_destination, status_codes):
    policy_id = 2002
    version = 1
    url = f"https://{api_destination}/cloudlets/v3/policies/{policy_id}/versions/{version}"
    requests_mock.get(f"{url}", json=get_sample_json("get_policy_version"), status_code=status_codes)
    response = api.get_policy_version(str(policy_id), str(version))
    if status_codes == 200:
        assert response["matchRules"][0]["akaRuleId"] == "ac0ca0af44f57683"
    else:
        assert response is None


@pytest.mark.parametrize("status_codes", [200, 403, 404, 400])
def test_clone_non_shared_policy(requests_mock, api, api_destination, status_codes):
    policy_id = 1001
    additional_versions = [
        3,
        4
    ]
    shared_policy_name = "new name"
    group_id = "123"
    url = f"https://{api_destination}/cloudlets/v3/policies/{policy_id}/clone"
    requests_mock.post(f"{url}", json=get_sample_json("clone_non_shared_policy"), status_code=status_codes)
    response = api.clone_non_shared_policy(str(policy_id), additional_versions, shared_policy_name, group_id)
    if status_codes == 200:
        assert response == 1001
    else:
        assert response is None


@pytest.mark.parametrize("status_codes", [202, 403, 404, 400])
def test_activate_policy(requests_mock, api, api_destination, status_codes):
    policy_id = 1001
    url = f"https://{api_destination}/cloudlets/v3/policies/{policy_id}/activations"
    requests_mock.post(f"{url}", json=get_sample_json("activate_policy"), status_code=status_codes)
    response = api.activate_policy(str(policy_id), "production", "activation", str(1))
    if status_codes == 202:
        assert response is True
    else:
        assert response is False
