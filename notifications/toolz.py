import re


def extract_parameters(value):
    param = "\{(\w+)\}"
    params_re = re.compile(param, re.VERBOSE | re.MULTILINE)
    return list(set(params_re.findall(value)))
