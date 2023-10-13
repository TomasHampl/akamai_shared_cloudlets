from akamai_shared_cloudlets import akamai_api_requests_abstractions
import importlib.metadata
import argparse


def main():
    akamai_requests = akamai_api_requests_abstractions.AkamaiApiRequestsAbstractions('/home/tomas/.edgerc')
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--version",
        help="Outputs program version and exits",
        action="version",
        version=importlib.metadata.version('akamai_shared_cloudlets'))

    arguments = parser.parse_args()


if __name__ == "__main__":
    main()
