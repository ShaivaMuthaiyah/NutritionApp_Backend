
import boto3
import json
import random
from werkzeug.utils import secure_filename
from datetime import datetime
import logging

import os
from dotenv import load_dotenv
load_dotenv()


# AWS configuration
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')
REGION = os.getenv('REGION')
BUCKET_URL = os.getenv('BUCKET_URL')

# Create an S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)

def generate_blog_id():
    return random.randint(10000, 99999)


def upload_image_to_s3(file, blog_title):

    # secure file name for removing spaces
    filename = secure_filename(blog_title) + os.path.splitext(file.filename)[1]

    # name fo the folder is /images creating path with the folde name
    file_path = f'images/{filename}'

    try:
        # upload into the specific bucket in the path and with the new file name
        s3_client.upload_fileobj(file, BUCKET_NAME, file_path)

        # make the url of the new file inside the folder inside bucket
        img_url = f"{BUCKET_URL}{file_path}"
        print("Image uploaded was success")

        return img_url
    
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

def update_blog_json(data):
    try:
        blog_key = f"blogs/{secure_filename(data['title'])}.json"
        blog_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=blog_key)
        current_data = json.loads(blog_obj['Body'].read().decode('utf-8'))

        current_data['description'] = data['description']
        current_data['tags'] = data['tags']
        current_data['content'] = data['content']
        current_data['imgSrc'] = data.get('imgSrc', current_data['description'])

        updated_blog_json = json.dumps(current_data, indent=4)

        s3_client.put_object(Body=updated_blog_json, Bucket=BUCKET_NAME, Key=blog_key)

        return {"message": "Blog updated successfully"}
    
    except Exception as e:
        logging.error(f"Error updating blog JSON: {e}")
        return None



# Function to create a blog JSON and upload to S3
def create_blog_json(data, img_url):

    # input data is in json form so getting values from keys as dictionary
    blog_data = {
        "title": data['title'],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "imgSrc": img_url,
        "description": data['description'],
        "author": data['author'],
        "role": data['role'],
        "content": data['content'],
        "category": data['category'],
        "blogId": generate_blog_id()
    }

    # convert the dictionary into json file
    blog_json = json.dumps(blog_data, indent=4)
    # create secure name from the title and add the json extension
    filename = secure_filename(data['title']) + ".json"
    # path of the json inside the blogs folder inside the bucket
    json_path = f'blogs/{filename}'

    try:
        # insert the json into the bucket using the key
        s3_client.put_object(Body=blog_json, Bucket=BUCKET_NAME, Key=json_path)
        return {"message": "Blog created successfully", "blog_url": f"{BUCKET_URL}{json_path}"}
    except Exception as e:
        print(f"Error uploading blog JSON: {e}")
        return None




def get_blogs():
    try:
        # List all objects in the S3 bucket
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix='blogs/')
        blogs = []

        # Check if any files are returned
        if 'Contents' in response:
            for item in response['Contents']:
                # Ensure the file is a JSON file
                if item['Key'].endswith('.json'):
                    # Get the blog content
                    blog_key = item['Key']
                    blog_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=blog_key)
                    blog_content = blog_obj['Body'].read().decode('utf-8')

                    # Parse the JSON content
                    blog_data = json.loads(blog_content)

                    # Append relevant details to the blogs list
                    blogs.append({
                        'BlogId': blog_data.get('BlogId'),
                        'title': blog_data.get('title'),
                        'imageSrc': blog_data.get('imageSrc'),
                        'description': blog_data.get('description'),
                        'date': blog_data.get('date'),
                        'content': blog_data.get('content'),
                        'category': blog_data.get('category'),
                        'author': blog_data.get('author'),
                        'role': blog_data.get('role'),
                    })
        
        # return an array of blogs to display
        return blogs
    except Exception as e:
        print(f'Error fetching blogs: {e}')
        return []

