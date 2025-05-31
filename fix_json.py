import json
import sys

def validate_json_file(json_path):
    """
    Validate a JSON file and report any issues.
    """
    print(f"Validating JSON file: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ JSON is valid. Loaded {len(data)} entries.")
        print(f"First entry type: {type(data[0])}")
        print(f"First few keys: {list(data[0].keys())}")
        
        # Check for required fields
        missing_fields = []
        for i, entry in enumerate(data[:100]):  # Check first 100 entries
            for field in ['focus', 'question', 'answer']:
                if field not in entry:
                    missing_fields.append((i, field))
        
        if missing_fields:
            print(f"⚠ Found {len(missing_fields)} missing required fields in the first 100 entries:")
            for i, field in missing_fields[:10]:  # Show first 10 issues
                print(f"  Entry {i} is missing field: {field}")
        else:
            print("✓ All required fields are present in sample entries.")
            
        return True
        
    except json.JSONDecodeError as e:
        print(f"✗ JSON is invalid: {e}")
        return False
    except Exception as e:
        print(f"✗ Error processing file: {e}")
        return False

if __name__ == "__main__":
    json_path = "medquad_data.json"
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    
    validate_json_file(json_path)