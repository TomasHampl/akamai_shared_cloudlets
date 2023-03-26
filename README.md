# Akamai shared cloudlets library
## Purpose
This python library should (and could) serve as the base building block for any application that 'wants' to work with Akamai Shared Cloudlets (for more information about Akamai cloudlets, see https://techdocs.akamai.com/cloudlets/reference/api).

For whatever reason, Akamai have not put much effort in implementing the shared cloudlets into their automation products (such as Akamai CLI https://github.com/akamai/cli or Terraform Akamai provider https://registry.terraform.io/providers/akamai/akamai/latest/docs/guides/get_started_cloudlets).

## Getting it
Once finished in a 'functioning' state, it should be available via the standard pypi.

## Using it
There are two main file in the 'package':
* akamai_api_requests_abstractions.py
* akamai_http_requests_wrapper.py

### API requests abstractions
First file contains a class that contains implementation of (nearly) all requests describes in the official Akamai documentation available at https://techdocs.akamai.com/cloudlets/reference/api. If you're looking for a particular request and you find it missing, Pull Requests are welcome.

### HTTP requests abstractions
It contains the logic that's capable of sending the signed requests to Akamai . There is a lot of code inside this class 