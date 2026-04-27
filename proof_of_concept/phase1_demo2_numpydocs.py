import inspect
import json
import re
from sktime.forecasting.arima import ARIMA
from numpydoc.docscrape import NumpyDocString

print("PHASE 1 DEMO (PART 2): NUMPYDOC PARSER + GRACEFUL DEGRADATION")


def parse_numpydoc_type(doc_type_str):

    doc_type_str = doc_type_str.lower()
    type_map = {
        "int": "integer", "integer": "integer",
        "float": "number", "str": "string", "string": "string",
        "bool": "boolean", "boolean": "boolean",
        "array-like": "array", "list": "array", "none": "null"
    }
    
    clean_str = re.sub(r'\(.*?\)', '', doc_type_str) # remove (default=None)
    clean_str = clean_str.replace(', optional', '')
    
    tokens = [t.strip() for t in re.split(r'\s+or\s+|,\s*', clean_str) if t.strip()]
    
    schema_types = []
    for token in tokens:
        if token in type_map:
            schema_types.append({"type": type_map[token]})
        else:
            return None
            
    if "optional" in doc_type_str or "default=none" in doc_type_str:
        if {"type": "null"} not in schema_types:
            schema_types.append({"type": "null"})

    if not schema_types:
        return None
    elif len(schema_types) == 1:
        return schema_types[0]
    else:
        unique_types = [dict(t) for t in {tuple(d.items()) for d in schema_types}]
        return {"anyOf": unique_types}

doc = NumpyDocString(ARIMA.__doc__)
doc_data = {
    param.name: {
        "doc_type": param.type,
        "description": " ".join(param.desc)
    }
    for param in doc["Parameters"]
}

sig = inspect.signature(ARIMA.__init__)
schema_properties = {}

for name, param in sig.parameters.items():
    if name == 'self' or name == 'kwargs': continue
        
    property_schema = {}
    
    if name in doc_data:
        raw_type = doc_data[name]["doc_type"]
        base_desc = doc_data[name]["description"]
        
        parsed_schema = parse_numpydoc_type(raw_type)
        
        if parsed_schema is not None:
            property_schema.update(parsed_schema)
            property_schema["description"] = base_desc
        else:
            property_schema["type"] = ["string", "integer", "number", "boolean", "array", "object", "null"]
            property_schema["description"] = f"[Type: {raw_type}] {base_desc}"
            
    schema_properties[name] = property_schema


print("=" * 60)
print("CASE 1: SUCCESSFUL PARSE")
print("=" * 60)
print(json.dumps({"maxiter": schema_properties["maxiter"]}, indent=2))

print("\n" + "=" * 60)
print("CASE 2: UNION TYPE PARSE")  
print("=" * 60)
print(json.dumps({"start_params": schema_properties["start_params"]}, indent=2))

print("\n" + "=" * 60)
print("CASE 3: GRACEFUL DEGRADATION FALLBACK")
print("=" * 60)
print(json.dumps({"order": schema_properties["order"]}, indent=2))

print("\n" + "=" * 60)
print("CASE 4: ISSUE")
print("=" * 60)
print(json.dumps({"method": schema_properties["method"]}, indent=2))



