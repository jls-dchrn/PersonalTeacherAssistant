import openai
import json
import os
from PIL import Image
import base64
from personalteacherassistant.cost import CostCalculator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
class GPT():

    def __init__(self,user):
        self.model = "gpt-4o"
        self.client = openai.OpenAI()
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.cost_calculator = CostCalculator()
        """
        -------------------------------------------------------------------------------------------------------------------------
                                                             Init prompt
        -------------------------------------------------------------------------------------------------------------------------

        """

        self.init_prompt = """
        You are a personal teacher assistant. This, means that you should never provide a direct solution to his problems.
        Rather, you will have to give him hints to help him doing his exercice and to understand the notions that it cover.
        Your student is young so adapt your speech to his level, keep your focus on clearly and concisely explaining the problem.
        """
        
        

        # Create contextfiles directory at project root if not exists
        context_dir = os.path.join(self.project_root, "contextfiles")
        os.makedirs(context_dir, exist_ok=True)

        # Path for the user's context file
        self.contextfile = os.path.join(context_dir, f"CF{user}.txt")

        # Read existing context if available
        if os.path.exists(self.contextfile):
            with open(self.contextfile, "r") as f:
                self.init_prompt += """
                Below are the conclusions from previous sessions with this student.
                Consider them when teaching.

                Here are the conclusions:
                """ + f.read()
        else:
            open(self.contextfile, "w").close()

    # basic call to GPT API
    def basicSendMessage(self, message, max_tokens):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=message,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def sendMessage(self, prompt, history, max_tokens=500):
        messages = [{"role": "system", "content": self.init_prompt}] 

        for user_msg, bot_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": bot_msg})

        messages.append({"role": "user", "content": prompt})

        input_tokens = len(prompt.split())
        self.cost_calculator.calculate_token_cost(input_tokens, "input")

        response = self.basicSendMessage(message=messages, max_tokens=max_tokens)

        output_tokens = len(response.split())
        self.cost_calculator.calculate_token_cost(output_tokens, "output")

        return response
        

    def save_chat_history(self, username, title, history):
        history_dir = os.path.join(self.project_root, "..", "history")
        os.makedirs(history_dir, exist_ok=True)
        filepath = os.path.join(history_dir, f"{username}_history.json")

        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
        else:
            data = {}

        data[title] = history

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_chat_titles(self, username):
        filepath = os.path.join(self.project_root, "..", "history", f"{username}_history.json")
        if not os.path.exists(filepath):
            return []
        with open(filepath, "r") as f:
            return list(json.load(f).keys())

    def load_chat_history(self, username, title):
        filepath = os.path.join(self.project_root, "..", "history", f"{username}_history.json")
        if not os.path.exists(filepath):
            return []
        with open(filepath, "r") as f:
            return json.load(f).get(title, [])

    def list_sessions(self):
        if not os.path.exists(self.history_file):
            return []
        with open(self.history_file, "r") as f:
            data = json.load(f)
        return list(data.keys())

    def load_session(self, title):
        if not os.path.exists(self.history_file):
            return
        with open(self.history_file, "r") as f:
            data = json.load(f)
        if title in data:
            self.sessionmemory = data[title]



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
                summaryprompt += f"""Use this, and your previous knowledge of the student, what teaching methods does the student respond to. 
                                    Here is your previous knowledge: {f.read()}.
                                    In order to do this you should use the ratings on a scale of 1-5 that the student has provided here: {rating}. 
                                    """
            
        else:
            with open(self.contextfile, "w") as f:
                pass

        message = [{
                        "role": "user",
                        "content": summaryprompt,
                    }]

        # get the response from the model
        summary = self.basicSendMessage(message=message,max_tokens=200)

        # Update the user context and write to the context file:
        usercontext += summary
        with open(self.contextfile, "a", newline='') as f:
            f.write(summary)
    

    def imagePrep(self, image_path):
        # Resize the image
        resized_image_path = "tmp_image.jpg"
        self.imageResize(image_path, resized_image_path)
        
        # Encode the resized image to base64
        image_base64 = self.encode_image_to_base64(resized_image_path)
        os.remove(resized_image_path)  # Clean up the temporary file
        return image_base64

    # resize image and file format to standard format

    def imageResize(self, input_image_path, output_image_path):
        """
        Resizes the input image so that the longest side is 512 pixels while maintaining the aspect ratio.
        
        :param input_image_path: Path to the input image.
        :param output_image_path: Path to save the resized image.
        """

        with Image.open(input_image_path) as img:
            # Convert RGBA or other modes to RGB
            if img.mode != "RGB":
                img = img.convert("RGB")

            max_size = 512
            width, height = img.size
            if width > height:
                new_width = max_size
                new_height = int((height / width) * max_size)
            else:
                new_height = max_size
                new_width = int((width / height) * max_size)

            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            resized_img.save(output_image_path, format="JPEG")

    def encode_image_to_base64(self, image_path):
        """
        Encodes an image to base64.
        
        :param image_path: Path to the image file.
        :return: Base64 encoded string of the image.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    

    def process_prompt(self, prompt:str="", image_paths:list[str]=[],max_tokens=500, detail="high"):
        token_cost = 0
        message = ""
        if image_paths:
            # Resize and encode the image
            for image in image_paths:
                image_base64 = self.imagePrep(image)
                token_cost += self.cost_calculator.calculate_image_cost(image, detail)
                message += f"![image](data:image/jpeg;base64,{image_base64})\n"
       
            if prompt:
                token_cost += self.cost_calculator.calculate_token_cost(len(prompt.split()), "input")
                message += prompt + "\n"
        return message, token_cost

