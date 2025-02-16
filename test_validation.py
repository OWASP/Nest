from schema.utils.schema_validators import validate_data

def run_test_cases():
    # Define the schema
    schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "format": "uri"}
        },
        "required": ["url"]
    }

    # Define test cases with expected results
    test_cases = [
        {
            "name": "Valid URL",
            "data": {"url": "https://example.com"},
            "should_pass": True
        },
        {
            "name": "Empty URL",
            "data": {"url": ""},
            "should_pass": False
        },
        {
            "name": "Null URL",
            "data": {"url": None},
            "should_pass": False
        },
        {
            "name": "Invalid URL",
            "data": {"url": "not-a-url"},
            "should_pass": False
        },
        {
            "name": "Invalid Protocol",
            "data": {"url": "ftp://example.com"},
            "should_pass": False
        },
        {
            "name": "Incomplete URL",
            "data": {"url": "http://"},
            "should_pass": False
        }
    ]

    # Run each test case
    for test in test_cases:
        print(f"\nTesting: {test['name']}")
        print(f"Input: {test['data']}")
        
        result = validate_data(schema, test['data'])
        print(f"Result: {result}")
        
        if test['should_pass']:
            print("Status: ✓" if result == "Validation successful" else "Status: ✗")
        else:
            print("Status: ✓" if result != "Validation successful" else "Status: ✗")

if __name__ == "__main__":
    print("Starting URI validation tests...\n")
    run_test_cases()