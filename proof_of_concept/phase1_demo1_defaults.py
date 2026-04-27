import inspect
import json
from sktime.forecasting.arima import ARIMA


print("PHASE 1 DEMO (PART 1): USING ONLY DEFAULT VALUES")

sig = inspect.signature(ARIMA.__init__)
schema_properties = {}

for name, param in sig.parameters.items():
    if name == 'self' or name == 'kwargs': continue
        
    property_schema = {}
    
    # ISSUE 1: No description available from inspect!
    property_schema["description"] = "NO DESCRIPTION AVAILABLE"
    
    # Infer type from default value
    if param.default is not inspect._empty:
        if isinstance(param.default, int) and not isinstance(param.default, bool):
            property_schema["type"] = "integer"
        elif isinstance(param.default, bool):
            property_schema["type"] = "boolean"
        elif isinstance(param.default, float):
            property_schema["type"] = "number"
        elif isinstance(param.default, str):
            property_schema["type"] = "string"
        elif param.default is None:
            # ISSUE 2: 'None' tells us nothing about the actual expected type!
            property_schema["type"] = "UNKNOWN (Default is None)"
        else:
            property_schema["type"] = "object"
            
    schema_properties[name] = property_schema

print(json.dumps({"ARIMA_Schema": {"properties": schema_properties}}, indent=2))
print("\n[ANALYSIS]:")
print("- It successfully inferred 'maxiter' is an integer.")
print("- THE FLAW: 'start_params' is UNKNOWN because its default is None.")
print("- THE FLAW: 0 descriptions. The LLM doesn't know what these parameters do.")
