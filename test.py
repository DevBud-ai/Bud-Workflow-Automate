import os
import json
import subprocess

# Ask the user for the Action name and description
action_name = input("Enter the name of your new Action: ")
action_description = input("Enter a description for your new Action: ")

# Ask the user for the input fields
print("Enter the input fields for your new Action (leave blank to finish):")
input_fields = []
while True:
    field_name = input("Field name: ")
    if not field_name:
        break
    field_type = input("Field type (string, number, boolean): ")
    field_required = input("Is this field required? (y/n): ").lower() == "y"
    input_fields.append({
        "name": field_name,
        "type": field_type,
        "required": field_required
    })

# Define the directory and file names for the new Action
action_dir = f"pieces/{action_name}"
metadata_file = f"{action_dir}/metadata.json"
schema_file = f"{action_dir}/schema.json"
run_file = f"{action_dir}/run.js"

# Create the new directory and metadata file
os.makedirs(action_dir)
with open(metadata_file, "w") as f:
    json.dump({
        "name": action_name,
        "description": action_description,
        "inputs": {field["name"]: {"type": field["type"], "description": ""} for field in input_fields}
    }, f, indent=2)

# Create the schema file based on the input fields
with open(schema_file, "w") as f:
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {field["name"]: {"type": field["type"]} for field in input_fields},
        "required": [field["name"] for field in input_fields if field["required"]]
    }
    json.dump(schema, f, indent=2)

# Create the run file with a simple "Hello, World!" implementation
with open(run_file, "w") as f:
    f.write('function run(input) {\n')
    f.write('  const name = input.name || "World";\n')
    f.write('  const message = `Hello, ${name}!`;\n')
    f.write('  return { message };\n')
    f.write('}\n\n')
    f.write('module.exports = {\n')
    f.write('  run\n')
    f.write('};\n')

# Test the new Action locally
subprocess.run(["ap-local", "run", action_name])

print(f"New Action '{action_name}' created in directory '{action_dir}'.")