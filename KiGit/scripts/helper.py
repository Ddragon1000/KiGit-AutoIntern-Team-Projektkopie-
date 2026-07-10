import sexpdata

def extract_parameters(element):
    # convert string into S-expression
    if isinstance(element, str):
        element = sexpdata.loads(element)

    params = {}
    # we skip first entry since its only component part
    for item in element[1:]:
        #we process s-expression lists
        if isinstance(item, list):
            # first element is the parameter name
            key = str(item[0])
            #UUID not relevant for user
            if key == "uuid":
                continue
            #parameter with single values
            if len(item) == 2:
                params[key] = str(item[1])
            #parameters with multiple values
            else:
                params[key] = sexpdata.dumps(item[1:])
    #return extracted parameters for the Renderer
    return params