"""
MIT License

Copyright (c) Jannick Tim Medda, Dennis Piotrowski, Marcel Wiemann, Ismail Koc, Daniel Quayes, Adrian Sturm

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import sexpdata
import scripts.BasicChange as bc
from typing import Any, Optional

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

    if "modified" in detail:
        for change in changes:
            if not isinstance(change, bc.ComponentModified):
                continue
            if not hasattr(change, "old_component"):
                continue 
            modified = get_modified_parameters(change.old_component,change.new_component)
            if not modified:
                continue
            all_params.append("[Modified]")

            for key, values in modified.items():
                old_value = values["old"]
                new_value = values["new"]

                all_params.append(
                    f"{key}: {old_value} -> {new_value}"
                )

            all_params.append("")
        return "\n".join(all_params) if all_params else "-"

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
       # if all_params:
        #    all_params.append("")
        #add type 
        if isinstance(change, bc.ComponentAdded):
            all_params.append("[Added]")
        elif isinstance(change, bc.ComponentRemoved):
            all_params.append("[Removed]")
        else:
            all_params.append("[Modified]")  
        all_params.extend(match_params)

        if all_params:
            all_params.append("")
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
    if "modified" in detail:
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

def get_modified_parameters(old_component: str, new_component: str)-> dict:
    old_params= extract_parameters(old_component)
    new_params = extract_parameters(new_component)
    modified = {}
    all_keys = set(old_params) | set(new_params)

    for key in all_keys:
        old_value = old_params.get(key)
        new_value = new_params.get(key)

        if old_value != new_value:
            modified[key] ={"old": old_value,"new": new_value}
    return modified

def extract_uuid(element: Any) -> Optional[str]:
    """
    Extract the UUID from the S-Expression elements
    """
    if not isinstance(element,list):
        return None
    for item in element:
        if not isinstance(item,list) or not item:
            continue
        if str(item[0]) == "uuid" and len(item) > 1:
            return str(item[1])
        nested_uuid = extract_uuid(item)
        if nested_uuid is not None:
            return nested_uuid
    return None

def find_mod_match(old_el: list[Any], cand: list[list[Any]])-> Optional[list[Any]]:
    """
    find new element to old_el through the uuid
    """
    old_uuid = extract_uuid(old_el)
    if old_uuid is None:
        return None

    for new_el in cand:
        new_uuid = extract_uuid(new_el)
        if new_uuid == old_uuid:
            return new_el

    return None