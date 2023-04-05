class ApiRequestSignatureError(Exception):
    """
    Unable to sign the request to Akamai
    """


class EdgeRcFileMissing(Exception):
    """
    Unable to find the file in provided location
    """


class IncorrectInputParameter(Exception):
    """
    Incorrect parameter was provided
    """
