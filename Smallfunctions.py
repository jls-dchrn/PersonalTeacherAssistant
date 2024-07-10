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

    def __init__(self,user):
        self.model = "gpt-4o"
        self.client = OpenAI()
        self.sessionmemory = []

        """
        -------------------------------------------------------------------------------------------------------------------------
                                                             Init prompt
        -------------------------------------------------------------------------------------------------------------------------

        """

        init_prompt = """
        You are a personal teacher assistant. This, means that you should never provide a direct solution to his problems.
        Rather, you will have to give him hints to help him doing his exercice and to understand the notions that it cover.
        Your student is young so adapt your speech to his level, keep your focus on clearly and concisely explaining the problem.
        """
    
        # First find the user's context file or create a new
        self.contextfile = "/contextfiles/CF" + user + ".csv"
        if os.path.exists(self.contextfile):
            with open(self.contextfile, "r") as f:
                init_prompt += """
                Bellow are the conclusions you had with the previous sessions with this student.
                Take in consideration when teaching him.

                Here are the conclusions:
                """
                for line in f:
                    init_prompt += "\n" + line[1] # add the summary and not the session id
                
        
        self.sessionmemory.append({
            "role" : "system",
            "content": init_prompt,
        })

        """
        ------------------------------------------------------------------------------------------------------------------------
        """
        self.cost_calculator = CostCalculator()
        # Use "Export MI_CHATGPT_APIKEY=xxxxxxxxxxxxxxx" to get api access
    
    def memoryToString(self):   
        text = ""
        for dict in self.sessionmemory:
            text += dict["content"] + "\n"
        return text

    # Input name of User as string
    def _summarize(self, user, rating):
        # Context of user that will be updated:
        usercontext = []

        # Prompt for summary after a teaching session
        summaryprompt = f"""You are a personal teaching assistant, and you have just finished tutoring a session.
        You now want to adapt your future teaching methods to adopt to this specific student.
        Some of the possible teaching method classifications could be the following:
        Concrete Examples, Visual Aids, Interactive Activities, Analogies and Metaphors, Step-by-Step Breakdown,
        Stories and Narratives, Scaffolded Questions, Simplified Language, Multisensory Approaches, Encouraging Exploration.
        You should optimize your response for use in an LLM prompt, therefore your summary, should be concise and precise, and it should be less than 100 words
        This is the current session memory: {self.memoryToString()}."""


        # If there is already some context add it to the summary prompt
        if os.path.exists(self.contextfile):
            with open(self.contextfile, "r") as f:
                usercontext = list(csv.reader(f))
                summaryprompt += f"""Use this, and your previous knowledge of the student, what teaching methods does the student respond to. 
                                    Here is your previous knowledge: {usercontext}.
                                    In order to do this you should use the ratings on a scale of 1-5 that the student has provided here: {rating}. 
                                    """
            
        else:
            with open(self.contextfile, "w") as f:
                f.write("id_session;summerize")

        message = {
                        "role": "user",
                        "content": summaryprompt,
                    }

        # get the response from the model
        summary = self.basicSendMessage(message=message,max_tokens=200)

        # Update the user context and write to the context file:
        usercontext.append([summary])
        with open(self.contextfile, "w", newline='') as f:
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
    
    # basic call to GPT API
    def basicSendMessage(self, message, max_tokens):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=message,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
        

    def sendMessage(self, prompt=None, image_path=None, max_tokens=500, detail="high"):
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
                # Template for text+ image
                self.sessionmemory.append(
                    {
                        "role": "user",
                        "content": f"{prompt}\n![image](data:image/jpeg;base64,{image_base64})",
                    }
                )
                response = self.basicSendMessage(max_tokens=max_tokens, message=self.sessionmemory)
            else:
                # Handle image only
                self.cost_calculator.calculate_image_cost(image_path, detail)
                # Template for image only
                self.sessionmemory.append(
                    {
                        "role": "user",
                        "content": f"![image](data:image/jpeg;base64,{image_base64})",
                    }
                )
            response = self.basicSendMessage(max_tokens=max_tokens, message=self.sessionmemory)
            # we don't want to keep in memory multiple example of resized image. Once the request is send we delete it
            os.remove("tmp_image.jpg")
        else:
            # Handle text only
            input_tokens = len(prompt.split())
            self.cost_calculator.calculate_token_cost(input_tokens, "input")
            # Template for image only
            self.sessionmemory.append(
                    {
                        "role": "user",
                        "content": prompt,
                    }
                )
            response = self.basicSendMessage(max_tokens=max_tokens, message=self.sessionmemory)

        # calculate the tokens of the answer
        output_tokens = len(response.split())
        self.cost_calculator.calculate_token_cost(output_tokens, "output")

        self.sessionmemory.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )
        
        return response


# Example usage:
if __name__ == "__main__":
    # Initialize GPT instance
    gpt_instance = gpt("test")

    # Send image message
    response_image = gpt_instance.sendMessage(image_path='img/test1.jpg')
    print(response_image)

    # Send text message
    response_text = gpt_instance.sendMessage(prompt='Describe the image.')
    print(response_text)

    # Send text + image message
    response_text_image = gpt_instance.sendMessage(prompt='Explain me the link of this image with the previous one', image_path='img/test2.jpg')
    print(response_text_image)
