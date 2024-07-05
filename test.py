# Test.py

import unittest
from PIL import Image
import os
import base64
from Smallfunctions import gpt

class TestImageResize(unittest.TestCase):

    def setUp(self):
        self.gpt_instance = gpt()
        self.input_image_path = "test_image.jpg"
        self.output_image_path = "resized_test_image.jpg"

        # Create a test image
        img = Image.new('RGB', (1000, 800), color = 'red')
        img.save(self.input_image_path)

    def tearDown(self):
        # Clean up the test image files
        if os.path.exists(self.input_image_path):
            os.remove(self.input_image_path)
        if os.path.exists(self.output_image_path):
            os.remove(self.output_image_path)

    def test_image_resize(self):
        self.gpt_instance.imageResize(self.input_image_path, self.output_image_path)
        
        # Check if the output image exists
        self.assertTrue(os.path.exists(self.output_image_path))

        # Open the resized image and check its dimensions
        with Image.open(self.output_image_path) as img:
            width, height = img.size
            self.assertTrue(width == 512 or height == 512)

    def test_encode_image_to_base64(self):
        # Resize the image first to have a valid test case
        self.gpt_instance.imageResize(self.input_image_path, self.output_image_path)
        
        # Encode the resized image to base64
        encoded_image = self.gpt_instance.encode_image_to_base64(self.output_image_path)
        
        # Decode the base64 image back to binary and check if it matches the original resized image
        decoded_image_data = base64.b64decode(encoded_image)
        with open("decoded_test_image.jpg", "wb") as f:
            f.write(decoded_image_data)
        
        # Open the original resized image and the decoded image to compare their content
        with Image.open(self.output_image_path) as original_img:
            with Image.open("decoded_test_image.jpg") as decoded_img:
                self.assertEqual(original_img.tobytes(), decoded_img.tobytes())
        
        # Clean up the decoded image file
        os.remove("decoded_test_image.jpg")

if __name__ == '__main__':
    unittest.main()
