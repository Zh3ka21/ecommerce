import json

# Read the existing data_temp.json file using UTF-16 encoding
with open('data_temp.json', 'r', encoding='utf-16') as infile:
    data = json.load(infile)

# Write it to a new file in UTF-8 encoding
with open('data.json', 'w', encoding='utf-8') as outfile:
    json.dump(data, outfile, ensure_ascii=False, indent=4)

print("Conversion to UTF-8 completed.")
