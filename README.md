# Akamai shared cloudlets library
## Purpose
This python library should (and could) serve as the base building block for any application that 'wants' to work with Akamai Shared Cloudlets (for more information about Akamai cloudlets, see https://techdocs.akamai.com/cloudlets/reference/api).

For whatever reason, Akamai have not put much effort in implementing the shared cloudlets into their automation products (such as Akamai CLI https://github.com/akamai/cli or Terraform Akamai provider https://registry.terraform.io/providers/akamai/akamai/latest/docs/guides/get_started_cloudlets).

## Getting it
Once finished in a 'functioning' state, it should be available via the standard pypi.

## Using it
### Prerequisites
You need Akamai credentials. To get them, see the https://techdocs.akamai.com/developer/docs/set-up-authentication-credentials documentation. You also need Python 3.8+ (it should work with older versions, but 3.8 is the oldest one that I tested with).

### Run
To start using, simply import & initialize the ```AkamaiRequestWrapper``` class. Something like this should work nicely:
```
from akamai_shared_cloudlets.src import akamai_api_requests_abstractions as api
api_func = api.AkamaiApiRequestsAbstractions('~/.edgerc')
print(api_func.list_shared_policies())
```
Example above does not do very much, but it shows the basic usage. First, you import (other import methods would work as well of course), then you instantiate the ```AkamaiApiRequestsAbstractions``` class using the only defined constructor (you can provide the location of your edgerc file - if you don't, it defaults to ```~/.edgerc```). Last step is to use one of this numerous methods to send the request to API.
