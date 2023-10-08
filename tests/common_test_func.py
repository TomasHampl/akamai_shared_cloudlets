import os


def get_sample_edgerc(filename: str = "sample_edgerc"):
    return get_working_dir() + "supplemental" + "/" + filename


def get_working_dir():
    if "tests" in os.getcwd():
        return os.getcwd() + "/"
    else:
        # return os.getcwd() + "/" + "akamai_shared_cloudlets" + "/" + "tests" + "/"
        return os.getcwd() + "/" + "/" + "tests" + "/"
