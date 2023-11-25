# Akamai shared cloudlets library
## Purpose
This python program implements the API requests that deal with Akamai Shared Cloudlets 
(for more information about Akamai cloudlets, 
see https://techdocs.akamai.com/cloudlets/reference/api).

It could be used as a building block for any application using the 'shared cloudlets API'
(such as Akamai CLI https://github.com/akamai/cli or Terraform Akamai provider https://registry.terraform.io/providers/akamai/akamai/latest/docs/guides/get_started_cloudlets).

## Using it
### Prerequisites
* You need Akamai credentials. To get them, see the https://techdocs.akamai.com/developer/docs/set-up-authentication-credentials documentation. 
* You also need Python 3.8+ (it should work with older versions, but 3.8 is the oldest one that I tested with).

### Run
There are two basic ways how to work with the app - importing the app and making it part of your own code like that - or there is limited 'cli' capability (that doesn't provide all the requests, but it may help you find some basic information anyway.)
#### Getting it
It is recommended to use this app in virtual environment (especially for your development needs). Then install the app from PyPI.
Following command installs the app from the TEST PYPI:
##### TEST PYPI
```
python3 -m pip install --index-url https://test.pypi.org/simple/ akamai-shared-cloudlets
```

##### PROD PYPI
```
python3 -m pip install akamai-shared-cloudlets
```
##### Poetry
To add the library to your own project as dependency, and you happen to use Poetry to manage your dependencies:
```
poetry add akamai-shared-cloudlets
```
#### Using it
Next step would be to import (example):
```
from akamai_shared_cloudlets import akamai_api_requests_abstractions as akamai_api
```
And finally you're ready to use the app:
```
print(akamai_api.list_cloudlets("~/.edgerc"))
```
Example above does not do very much, but it shows how to start using the app. 

#### Usint it as CLI
Issuing the following command:
```commandline
cloudlets list-cloudlets
```
Would produce this output (for example, it may be different in your case)
```
Sending request to Akamai...
[{'cloudletType': 'ER', 'cloudletName': 'EDGE_REDIRECTOR'}]
```
Help is provided when issued the ```cloudlets``` command without any parameters or ```clouldets --help```
