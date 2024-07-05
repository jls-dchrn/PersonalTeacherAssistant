# Import necessary modules at the top of your file
import openai
from openai import OpenAI

import os
import csv
from PIL import Image

import base64
from Cost import CostCalculator


from sys import path as sys_path
from os import path as os_path
from os import environ

environ["OPENAI_API_KEY"] = "ENTER_API_KEY"
sys_path.append(os_path.dirname(os_path.dirname(os_path.abspath(__file__))))


class gpt:

    def __init__(self):
        self.model = "gpt-4o"
        self.client = OpenAI()
        self.sessionmemory = ""
        self.cost_calculator = CostCalculator()
        # Use "Export MI_CHATGPT_APIKEY=xxxxxxxxxxxxxxx" to get api access

    # Input name of User as string
    def _summarize(self, user):
        # Context of user that will be updated:
        usercontext = []

        # First find the user's context file or create a new
        contextfile = "/contextfiles/CF" + user + ".csv"
        if os.path.exists(contextfile):
            with open(contextfile, "r") as f:
                usercontext = list(csv.reader(f))
        else:
            with open(contextfile, "w") as f:
                pass

        # Prompt for summary after a teaching session
        summaryprompt = f"""You are a personal teaching assistant, and you have just finished tutoring a session.
        You now want to adapt your future teaching methods to adopt to this specific student.
        This is the current session memory: {self.sessionmemory}.
        Expand your knowledge of the student and what teaching methods they respond to, to the following csv file: {usercontext}"""

        # get the response from the model
        response = self.sendMessage(prompt=summaryprompt)
        summary = response.choices[0].text.strip()

        # Update the user context and write to the context file:
        usercontext.append([summary])
        with open(contextfile, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(usercontext)

    # resize image and file format to standard format
    # Jules
    def imagePrep(self, image_path):
        # Resize the image
        resized_image_path = "tmp_image.jpg"
        self.imageResize(image_path, resized_image_path)
        
        # Encode the resized image to base64
        image_base64 = self.encode_image_to_base64(resized_image_path)
        return image_base64

    # resize image and file format to standard format
    def imageResize(self, input_image_path, output_image_path):
        """
        Resizes the input image so that the longest side is 512 pixels while maintaining the aspect ratio.
        
        :param input_image_path: Path to the input image.
        :param output_image_path: Path to save the resized image.
        """
        with Image.open(input_image_path) as img:
            max_size = 512
            width, height = img.size
            if width > height:
                new_width = max_size
                new_height = int((height / width) * max_size)
            else:
                new_height = max_size
                new_width = int((width / height) * max_size)
            
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            resized_img.save(output_image_path)

    def encode_image_to_base64(self, image_path):
        """
        Encodes an image to base64.
        
        :param image_path: Path to the image file.
        :return: Base64 encoded string of the image.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')


    # Update the sendMessage method in SmallFunctions.py
    def sendMessage(self, prompt=None, image_path=None, max_tokens=50, detail="high"):
        """
        Sends a request to the OpenAI GPT-4 model using the openai library. Handles text, image, and text+image inputs.
        
        :param prompt: The prompt to be sent to the model (optional if only sending an image).
        :param image_path: Path to the image file to be sent to the model (optional if only sending text).
        :param max_tokens: The maximum number of tokens to generate (used for text prompts).
        :param detail: The detail level for image inputs ("low" or "high").
        :return: Response from the API.
        """
        if image_path:
            # Resize and encode the image
            image_base64 = self.imagePrep(image_path)

            if prompt:

                
                # Handle text + image
                input_tokens = len(prompt.split())
                self.cost_calculator.calculate_token_cost(input_tokens, "input")
                response = self.client.chat.completions.create(
                    model=self.model,
                    
                    messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                            }
                        ],
                    }],
                    max_tokens=max_tokens
                )
            else:
                # Handle image only
                self.cost_calculator.calculate_image_cost(image_path, detail)
                response = self.client.chat.completions.create(
                    model=self.model,
                    
                    messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                            }
                        ],
                    }],
                    max_tokens=max_tokens
                )
            # we don't want to keep in memory multiple example of resized image. Once the request is send we delete it
            os.remove("tmp_image.jpg")
        else:
            # Handle text only
            input_tokens = len(prompt.split())
            self.cost_calculator.calculate_token_cost(input_tokens, "input")
            response = self.client.chat.completions.create(
                    model=self.model,
                    
                    messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            }
                        ],
                    }],
                    max_tokens=max_tokens
                )
        
        output_tokens = len(response.choices[0].message.content.split())
        self.cost_calculator.calculate_token_cost(output_tokens, "output")
        
        return response.choices[0].message.content


# Example usage:
if __name__ == "__main__":
    # Initialize GPT instance
    gpt_instance = gpt()

    # Send text message
    response_text = gpt_instance.sendMessage(prompt='Hello, how are you?')
    print(response_text)

    # Send image message
    response_image = gpt_instance.sendMessage(image_path='img/test1.jpg')
    print(response_image)

    # Send text + image message
    response_text_image = gpt_instance.sendMessage(prompt='Describe this image.', image_path='img/test1.jpg')
    print(response_text_image)