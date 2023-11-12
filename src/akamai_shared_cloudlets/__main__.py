import os
import click
import akamai_shared_cloudlets.akamai_api_requests_abstractions as api
import akamai_shared_cloudlets.shared as common


@click.group()
def main():
    """
    Empty method that only exists because of the command group
    """
    pass


@click.command()
@click.argument(
    "policy_name",
    type=click.STRING,
)
@click.option(
    "--edgerc-location",
    "edgerc_location",
    type=click.Path(exists=False),
    default="~/.edgerc",
    help="Gives an option to provide your own location of the 'edgerc' file."
)
def find_policy_by_name(policy_name, edgerc_location):
    """ Returns the id of the policy identified by the provided name. Returns nothing, if policy not found in Akamai """
    edgerc = get_home_folder(edgerc_location)
    policy = api.get_shared_policy_by_name(policy_name, edgerc)
    if len(policy) == 0:
        print(f"We found no policy matching the name {policy_name}. Please check the input for"
              f" any typing errors and try again")
    if len(policy) == 1:
        final_policy_name = list(policy)[0]
        policy_id = policy.get(final_policy_name)
        print(f"We found the following policy matching the name {final_policy_name}: {policy_id} ")
    else:
        number_of_policies = len(policy)
        print(f"We could not find policy matching exactly {policy_name}. Instead we found {number_of_policies} "
              f"policies that contain the provided policy name '{policy_name}'")
        for policy, id in policy.items():
            print(f"{policy}: {id}")


@click.command()
@click.option(
    "--edgerc-location",
    "edgerc_location",
    type=click.Path(exists=False),
    default="~/.edgerc",
    help="Gives an option to provide your own location of the 'edgerc' file."
)
@click.option(
    "--response-format",
    help="Controls how to print the response. If 'text' is chosen, response contains "
         "just policy names with their respective id"
         "response_format",
    type=click.Choice([
        'json',
        'text'
    ],
        case_sensitive=False
    )
)
def list_policies(edgerc_location, response_format):
    """ Returns all available policies"""
    edgerc = get_home_folder(edgerc_location)
    policies = api.list_shared_policies(edgerc)

    if policies is not None:
        if response_format == "text":
            parsed_response = common.get_shared_policies_text(policies)
            for name, policy_id in sorted(parsed_response.items()):
                print(name, ':', policy_id)
        else:
            print(policies)
    else:
        print("No policies found...perhaps your credentials do not grant you permissions to view any policies?")


def get_home_folder(edgerc_location: str):
    return os.path.expanduser(edgerc_location)


main.add_command(find_policy_by_name)
main.add_command(list_policies)

if __name__ == "__main__":
    main()
