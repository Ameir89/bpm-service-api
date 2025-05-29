import os
import platform
import base64

from application.common.general import General


class FileImage:   
    def __init__(self, image_name=None):
        self.image_name = image_name

    def get_file_path(self, file_name, is_linux_path=False):
        """
        Generate file path based on platform.
        """
        if platform.system() == "Linux" or is_linux_path:
            base_path = "/home/code/uploads"
        else:
            base_path = r'D:\log\uploads'
        
        # Ensure directory exists
        os.makedirs(base_path, exist_ok=True)

        return os.path.join(base_path, file_name)

    def save_file(self, base64_content, file_name=None):
        """
        Save any file (image or other) from base64 content.
        """
        file_name = file_name or self.image_name
        if not file_name:
            raise ValueError("File name is required")

        file_path = self.get_file_path(file_name)
        try:
            file_data = base64.b64decode(base64_content)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            return file_path
        except Exception as e:
            General.write_event(f"Error saving file {file_name}: {str(e)}")
            raise

    def read_file(self, file_name, is_linux_path=False):
        """
        Read any file (image or other) and return base64 encoding.
        """
        file_path = self.get_file_path(file_name, is_linux_path)

        if not os.path.exists(file_path):
            General.write_event(f'File not found: {file_path}')
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'rb') as file:
                encoded_string = base64.b64encode(file.read()).decode('utf-8')
            return encoded_string
        except Exception as e:
            General.write_event(f"Error reading file {file_name}: {str(e)}")
            raise

    def save_image(self, base64_image, file_name=None):
        """
        Save image file specifically (alias for save_file).
        """
        return self.save_file(base64_image, file_name)

    def read_image(self, image_dir):
        """
        Read image file specifically (alias for read_file).
        """
        return self.read_file(image_dir)
