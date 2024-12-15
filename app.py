from flask import Flask, request, jsonify, render_template, send_file
from flask_apscheduler import APScheduler
from flask_cors import CORS
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
from mongodb_functions import mealCalculator
from nutritional_calculations import calculate_nutrition
from blog_functions import get_blogs, upload_image_to_s3, create_blog_json, update_blog_json
from health_report import generateHealthReport, cleanupActivity, cleanupActivityFolder
from urllib.parse import unquote
import logging
import uuid
import os
# from dotenv import load_dotenv

# load_dotenv()


BUCKET_URL = os.getenv('BUCKET_URL')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


logging.basicConfig(level=logging.INFO)


# scheduler for automating cleanup
scheduler = APScheduler()
report_list = []


@scheduler.task('interval', id='cleanup_reports', minutes=10)
def cleanupFiles():
    if len(report_list) > 0:
        for each_item in report_list:
            cleanupActivity(each_item)
            print(f"deleting of {each_item} is a success")
            report_list.remove(each_item)
    else:
        # removes all items in folder if there is no reports in queue
        cleanupActivityFolder()


@app.route('/')
def home():
    return render_template('index.html')



@app.route('/api/blogs', methods=['GET'])
def blogs_route():
    blogs = get_blogs()  # Call the function to get blogs
    if blogs:
        return jsonify(blogs)
    else:
        return jsonify({'error': 'Could not fetch blogs'}), 500



# Route to get a specific blog by title
@app.route('/api/blogs/title/<path:title>', methods=['GET'])
def get_blog_by_title(title):

    decoded_title = unquote(title)

    app.logger.info(f"Received title: {title}") 
    print(f"Decoded title: {decoded_title}")
    blogs = get_blogs()  # Retrieve the list of blogs from S3 or wherever stored
    blog = next((b for b in blogs if b['title'] == decoded_title), None)

    if blog:
        return jsonify(blog)
    else:
        return jsonify({'error': 'Blog not found'}), 404


@app.route('/create_blog_form')
def create_blog_form():
    return render_template('createblog.html') 



@app.route('/edit_blog_form')
def edit_blog_form():
    return render_template('editblog.html')  


@app.route('/api/update_blog', methods=['PUT'])
def update_blog():
    if 'title' not in request.form:
        return jsonify({'error': 'Title is required'}), 400

    title = request.form['title']

    # Fetch existing blogs and find the blog by title
    blogs = get_blogs()
    blog = next((b for b in blogs if b['title'] == title), None)
    if not blog:
        return jsonify({'error': 'Blog not found'}), 404

    # Prepare a clean image name based on the title
    blog_title = title.replace(" ", "_")  # Replace spaces with underscores for the image name

    # Default to the current image path or new image path
    new_img_src = ""

    # Check if a file is uploaded
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        print(file)

        # Extract the file extension of the uploaded file
        # file_ext = os.path.splitext(file.filename)[1]  # Gets the file extension (e.g., '.jpg', '.png')

        # Set the new image name using the blog title and the extracted extension
        new_image_name = blog_title
        print(new_image_name)

        # Upload the new image to S3 with the title as the name
        img_url = upload_image_to_s3(file, new_image_name)
        print(img_url)

        # Update the image source URL to the new S3 URL
        new_img_src = img_url  # Full URL with bucket details
    else:
        new_img_src = blog.get('imgSrc', BUCKET_URL + "images/" + blog_title + ".jpg")

    # Construct blog data for updating, using form data for non-file fields
    blog_data = {
        'title': title,
        'description': request.form.get('description', blog['description']),
        'tags': request.form.get('tags', blog['tags']).split(','),  # Convert tags to list
        'content': request.form.get('content', blog['content']),
        'imgSrc': new_img_src
    }

    # Update the blog in the JSON file
    result = update_blog_json(blog_data)

    if result:
        return jsonify({'success': "Blog updated successfully"}), 200
    else:
        return jsonify({'error': "Failed to update blog"}), 500



@app.route('/api/download_report/<report_id>', methods=['GET'])
def generate_report(report_id):

    report_list.append(report_id)

    fileName = f'reports/nutrition_report_{report_id}.pdf'

    response = send_file(fileName, as_attachment=True, mimetype='application/pdf')

    return response



@app.route('/api/create_blog', methods=['POST'])
def create_blog():
    if 'file' not in request.files or 'title' not in request.form:
        return jsonify({'error': 'Image file and blog title are required'}), 400

    file = request.files['file']
    blog_data = {
        "avatarInitial": request.form['avatarInitial'],
        "title": request.form['title'],
        "description": request.form['description'],
        "tags": request.form.getlist('tags'),
        "content": request.form['content']
    }

    img_url = upload_image_to_s3(file, blog_data['title'])
    if not img_url:
        return jsonify({'error': 'Failed to upload image'}), 500

    result = create_blog_json(blog_data, img_url)
    if result:
        return jsonify(result), 201
    else:
        return jsonify({'error': 'Failed to create blog'}), 500



# Define the route for user input
@app.route('/calculate', methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE'])
def calculate():

    id = uuid.uuid1()
    data = request.json
    print("Received data:", data) 
    # first_name = data.get("first_name")
    # last_name = data.get("last_name")
    # email = data.get("email")
    age = data.get("age")
    gender = data.get("gender")
    weight = data.get("weight")
    height = data.get("height")
    diet = data.get("diet")
    allergies = data.get("allergies")
    activity_level = data.get("activity_level")
    goal = data.get("goal") 

    # if not all([age, gender, weight, height, activity_level, goal]):
    #     return jsonify({"error": "Missing required parameters"}), 400

    # Perform nutrition calculation with goal
    nutrients = calculate_nutrition(age, gender, weight, height, activity_level, goal, diet, allergies)
    # print("Required nutrients", nutrients)

    generateHealthReport(nutrients, id)

    # Meals from the nutrients calculated
    meals = mealCalculator(nutrients)


    result = {
        'nutrients': nutrients,
        'meals': meals,
        "report_id":str(id)
    }


    return jsonify(result)




# MongoDB URI
MONGO_URI = os.getenv('MONGO_URI')

# Initialize MongoDB client
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

# Liveness Probe - Checks if the app is running
@app.route('/healthz', methods=['GET'])
def liveness_probe():
    return jsonify({"status": "alive"}), 200

# Readiness Probe - Dynamically checks if MongoDB is connected
@app.route('/readiness', methods=['GET'])
def readiness_probe():
    try:
        # Ping MongoDB to verify connectivity
        client.admin.command({'ping': 1})
        return jsonify({"status": "ready"}), 200
    except ConnectionFailure:
        print("Issue ith database connectivity")
        return jsonify({"status": "not_ready"}), 503




if __name__ == '__main__':

    # scheduler
    scheduler.init_app(app)
    scheduler.start()

    # running ap
    app.run(host="0.0.0.0", port=5000, debug=True)

