import pandas as pd
import ast

input_csv = "recipes.csv"
output_csv = "recipes_after.csv"

df = pd.read_csv(input_csv)

def convert_to_array(value):
    if isinstance(value, str):
        if value == 'NA':
            return None
        
        if value.startswith('c(') and value.endswith(')'):
            try:
                # Remove 'c(' and ')'
                list_str = value[2:-1]
                
                # Replace 'NA' with None
                list_str = list_str.replace('NA', 'None')
                
                # Safely convert to a Python list
                result = ast.literal_eval('[' + list_str + ']')
                
                return result  # This will now return a list
            except Exception as e:
                print(f"Error evaluating {value}: {e}")
                return value  # If there's an error, keep the original value
    
    return value

# Apply the conversion function
df = df.map(convert_to_array)

# Save to a CSV with JSON-like strings (if needed)
df.to_csv(output_csv, index=False)

# Upload to MongoDB
from pymongo import MongoClient

# Replace this with your MongoDB connection string
client = MongoClient("mongodb://localhost:27017/")
db = client["food"]
collection = db["recipes"]

# Convert DataFrame to a dictionary and insert into MongoDB
collection.insert_many(df.to_dict("records"))

print("Data uploaded successfully!")
