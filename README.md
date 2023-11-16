# Akamai shared cloudlets library
## Purpose
This python program implements the API requests that deal with Akamai Shared Cloudlets 
(for more information about Akamai cloudlets, 
see https://techdocs.akamai.com/cloudlets/reference/api).

It could be used as a building block for any application using the 'shared cloudlets API'
(such as Akamai CLI https://github.com/akamai/cli or Terraform Akamai provider https://registry.terraform.io/providers/akamai/akamai/latest/docs/guides/get_started_cloudlets).

## Getting it
Once finished in a 'functioning' state, it should be available via the standard pypi.

## Using it
### Prerequisites
* You need Akamai credentials. To get them, see the https://techdocs.akamai.com/developer/docs/set-up-authentication-credentials documentation. 
* You also need Python 3.8+ (it should work with older versions, but 3.8 is the oldest one that I tested with).

### Run
There are two basic ways how to work with the app - importing the app and making it part of your own code like that - or there is limited 'cli' capability (that doesn't provide all the requests, but it may help you find some basic information anyway.)
#### Module
To start using, simply import & initialize the ```AkamaiRequestWrapper``` class. Something like this should work nicely:
```
...tbd
```
Example above does not do very much, but it shows the basic usage. First, you import (other import methods would work as well of course), then you instantiate the ```AkamaiApiRequestsAbstractions``` class using the only defined constructor (you can provide the location of your edgerc file - if you don't, it defaults to ```~/.edgerc```). Last step is to use one of this numerous methods to send the request to API.

#### CLI
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
