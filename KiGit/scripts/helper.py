import sexpdata
import scripts.BasicChange as bc

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

def format_parameters(changes, detail):
    """
    Formats component parameters according to the requested details
    detail:
        []              -> no output
        ["all"]         -> all parameters
        ["start"]       -> only start
        ["start","end"] -> only start and end
    """
    #if no details
    if not detail:
        return "-"

    all_params = []
    #we go thorugh components
    for change in changes:
        params = extract_parameters(change.component)
        match_params = []
        #we keep the requested detail parameters
        for key, value in params.items():
            if "all" in detail:
                match_params.append(f"{key}={value}")
            elif key in detail:
                match_params.append(f"{key}={value}")
        if not match_params:
            continue
        # separate wires/segments
        if all_params:
            all_params.append("")
        #add type 
        if isinstance(change, bc.ComponentAdded):
            all_params.append("[Added]")
        elif isinstance(change, bc.ComponentRemoved):
            all_params.append("[Removed]")
        else:
            all_params.append("[Modified]")  
        all_params.extend(match_params)
    #formatted output getting returned 
    return "\n".join(all_params) if all_params else "-"

def filter_parameters(params, detail):
    """
    Filters a parameter dictionary for JSON output.
    Returns:
        {}                  -> no details requested
        params              -> all parameters requested
        filtered dict       -> only the selected parameters
    """
    #if no details
    if not detail:
        return {}
    # Return the complete parameter set
    if "all" in detail:
        return params
    # Return only the parameters requested in a dictionary
    filtered_params = {}
    # Iterate over all extracted parameters and keep requested ones
    for key, value in params.items():
        if key in detail:
            filtered_params[key] = value

    return filtered_params