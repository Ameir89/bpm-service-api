import secrets
import os
import platform
import base64
from flask import current_app as app
from application.common.general import General


def save_img(base64_image, image_name):
    if platform.system() == "Linux":
        image_path = "/home/code/uploads"
    else:
        image_path = r'D:\log\uploads'

    file_name = image_name
    image_data = base64.b64decode(base64_image)
    # Set image whole path here
    file_path = os.path.join(image_path, file_name)
    with open(file_path, 'wb') as f:
        f.write(image_data)

    return file_path


def save_file(base64_image, image_name):
    if platform.system() == "Linux":
        image_path = "/home/code/uploads"
    else:
        image_path = r'D:\log\uploads'

    file_name = image_name
    image_data = base64.b64decode(base64_image)
    # Set image whole path here
    file_path = os.path.join(image_path, file_name)
    with open(file_path, 'wb') as f:
        f.write(image_data)

    return file_path


def read_image(image_dir):
    if platform.system() == "Linux":
        image_path = image_dir
        General.write_event(f'platform linux image path {image_path}')
    else:
        image_path = os.path.join(r'D:', image_dir)
        General.write_event(f'platform windows image path {image_path}')
    # Check if the file exists
    if not os.path.exists(image_path):
        General.write_event(f'File not found')
        print("Error: File not found")
        return None
    with open(image_path, 'rb') as file:
        encoded_string = base64.b64encode(file.read())
        encoded = encoded_string.decode('utf-8')
    return encoded







# import secrets
# import os
# from PIL import Image
# from flask import current_app as app
#
# def save_pic(picture):
#     """Saves an image to disk"""
#     file_name = secrets.token_hex(8) + os.path.splitext(picture.filename)[1]
#     if not os.path.isdir(os.path.join(app.root_path, 'static')):
#         os.mkdir(os.path.join(app.root_path, "static"))
#         os.mkdir(os.path.join(app.root_path, "static/images"))
#         os.mkdir(os.path.join(app.root_path, "static/images/books"))
#     if not os.path.isdir(os.path.join(app.root_path, 'static/images')):
#         os.mkdir(os.path.join(app.root_path, "static/images"))
#         os.mkdir(os.path.join(app.root_path, "static/images/books"))
#     if not os.path.isdir(os.path.join(app.root_path, 'static/images/books')):
#         os.mkdir(os.path.join(app.root_path, "static/images/books"))
#     file_path = os.path.join(app.root_path, "static/images/books", file_name)
#     picture = Image.open(picture)
#     picture.thumbnail((150, 150))
#     picture.save(file_path)
#     return file_name