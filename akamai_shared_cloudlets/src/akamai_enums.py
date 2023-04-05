from enum import Enum


class EdgeGridKeys(Enum):
    CLIENT_TOKEN = "client_token"
    CLIENT_SECRET = "client_secret"
    ACCESS_TOKEN = "access_token"
    BASE_URL = "hostname"


class AkamaiNetworks(Enum):
    STAGING = "staging"
    PRODUCTION = "production"


class ActivationOperations(Enum):
    ACTIVATION = "activation"
    DEACTIVATION = "deactivation"
