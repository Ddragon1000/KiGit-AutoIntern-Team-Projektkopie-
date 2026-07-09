import sexpdata

def extract_parameters(element):
    """
    Helperfunction: Extracts parameters from elements
    """
    params = {}

    for item in element[1:]:
        if isinstance(item, list):
            key = str(item[0])

            if len(item) == 2:
                params[key] = str(item[1])
            else:
                params[key] = sexpdata.dumps(item[1:])

    return params