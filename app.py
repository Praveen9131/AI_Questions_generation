import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, send_file, url_for
from io import BytesIO
from dotenv import load_dotenv
from PIL import Image
import requests
from openai import OpenAI
from simple_mcq import generate_quiz
from simple_checkox import generate_quizc
from fill_in_the_blanks import generate_quiz1
from image_to_image_mcq import (
    download_and_resize_image as download_and_resize_image2, 
    generate_image as generate_image2, 
    generate_image_options, 
    generate_mcq_with_image_options, 
    generate_custom_content, 
    image_store_imcq
)
from images_txt import generate_custom_content1, image_store1
from image_txt_checkbox import generate_custom_content11, image_store11
from sequence import generate_sequence_quiz
from image_checkbox1 import generate_custom_content_checkbox,image_store_checkbox
from True_False_Radio_Btn_with_Image_Text_Question import generate_custom_content_true, image_store_true
# Load environment variables
load_dotenv()
KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Set up RotatingFileHandler
log_file = '/root/brain/app.log'
if not os.path.exists('/root/brain'):
    os.makedirs('/root/brain', exist_ok=True)

handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=5)
handler.setLevel(logging.ERROR)  # Set the handler to log only ERROR level messages and above
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Set the root logger level to ERROR
logging.getLogger().setLevel(logging.ERROR)

@app.route('/generate_quiz', methods=['GET'])
def generate_quiz_route():
    try:
        number = request.args.get('number', type=int)
        if number is None:
            raise ValueError("The 'number' parameter must be an integer")
        
        subject = request.args.get('subject', type=str)
        if subject is None:
            raise ValueError("The 'subject' parameter must be a string")

        tone = request.args.get('tone', type=str)
        if tone is None:
            raise ValueError("The 'tone' parameter must be a string")

        quiz_type = request.args.get('quiz_type', type=int)
        if quiz_type is None:
            raise ValueError("The 'quiz_type' parameter must be an integer")

        if quiz_type == 100:
            response = generate_quiz(number, subject, tone)
        elif quiz_type == 200:
            response = generate_quizc(number, subject, tone)
        elif quiz_type == 300:
            response = generate_quiz1(number, subject, tone)
        elif quiz_type == 400:
            response = generate_sequence_quiz(number, subject, tone)
        elif quiz_type == 500:
            response = generate_custom_content1(number, subject, tone)
        elif quiz_type == 501:
            response = generate_custom_content11(number, subject, tone)
        elif quiz_type == 600:
            response = generate_custom_content(number, subject, tone)
        elif quiz_type == 601:
            response = generate_custom_content_checkbox(number, subject, tone)
        elif quiz_type == 700:
            response = generate_custom_content_true(number, subject, tone)
        else:
            raise ValueError("Invalid quiz type, please enter a correct quiz_type")

        return jsonify(response)
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/image/<image_key>', methods=['GET'])
def get_image(image_key):
    try:
        quiz_type = request.args.get('quiz_type', type=int)
        if quiz_type == 500 and image_key in image_store1:
            return send_file(
                BytesIO(image_store1[image_key].getvalue()),
                mimetype='image/png'
            )
        elif quiz_type == 501 and image_key in image_store11:
            return send_file(
                BytesIO(image_store11[image_key].getvalue()),
                mimetype='image/png'
            )
        elif quiz_type == 600 and image_key in image_store_true:
            return send_file(
                BytesIO(image_store_true[image_key].getvalue()),
                mimetype='image/png'
            )
        elif quiz_type == 601 and image_key in image_store_checkbox:
            return send_file(
                BytesIO(image_store_checkbox[image_key].getvalue()),
                mimetype='image/png'
            )
        elif quiz_type == 700 and image_key in image_store_true:
            return send_file(
                BytesIO(image_store_true[image_key].getvalue()),
                mimetype='image/png'
            )
        else:
            raise ValueError("Image with key not found")

    except Exception as e:
        app.logger.error(str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/list_all_images', methods=['GET'])
def list_all_images():
    try:
        images = {
            'image_store': [
                {"key": key, "url": url_for('get_image', image_key=key, quiz_type=600, _external=True)}
                for key in image_store_true.keys()
            ],
            'image_store1': [
                {"key": key, "url": url_for('get_image', image_key=key, quiz_type=500, _external=True)}
                for key in image_store1.keys()
            ],
            'image_store11': [
                {"key": key, "url": url_for('get_image', image_key=key, quiz_type=501, _external=True)}
                for key in image_store11.keys()
            ],
            'image_store_checkbox': [
                {"key": key, "url": url_for('get_image', image_key=key, quiz_type=601, _external=True)}
                for key in image_store_checkbox.keys()
            ],
           'image_store_true': [
                {"key": key, "url": url_for('get_image', image_key=key, quiz_type=700, _external=True)}
                for key in image_store_true.keys()
            ]
        }
        return jsonify(images)
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/delete_images', methods=['GET', 'POST'])
def delete_images():
    try:
        start_index = request.args.get('start_index', type=int)
        if start_index is None:
            raise ValueError("The 'start_index' parameter must be an integer")

        end_index = request.args.get('end_index', type=int)
        if end_index is None:
            raise ValueError("The 'end_index' parameter must be an integer")

        quiz_type = request.args.get('quiz_type', type=int)
        if quiz_type is None:
            raise ValueError("The 'quiz_type' parameter must be an integer")
        
        if start_index < 0 or end_index < start_index:
            raise ValueError("Invalid index range provided for deletion")

        if quiz_type == 500:
            keys = list(image_store1.keys())
            for key in keys[start_index:end_index + 1]:
                del image_store1[key]
        elif quiz_type == 501:
            keys = list(image_store11.keys())
            for key in keys[start_index:end_index + 1]:
                del image_store11[key]
        elif quiz_type == 600:
            keys = list(image_store_true.keys())
            for key in keys[start_index:end_index + 1]:
                del image_store_true[key]
        elif quiz_type == 601:
            keys = list(image_store_checkbox.keys())
            for key in keys[start_index:end_index + 1]:
                del image_store_checkbox[key]
        elif quiz_type == 700:
            keys = list(image_store_true.keys())
            for key in keys[start_index:end_index + 1]:
                del image_store_true[key]
        else:
            raise ValueError("Invalid quiz type for deletion")
        
        return jsonify({"message": "Images deleted successfully"}), 200
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
