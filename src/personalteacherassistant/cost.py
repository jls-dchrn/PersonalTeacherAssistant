import os
import csv
import datetime
from PIL import Image

class CostCalculator:
    
    # GPT-4o token prices in euros
    INPUT_TOKEN_COST = 0.03 / 1000 * 0.89  # €0.03 per 1,000 tokens for input (converted to EUR)
    OUTPUT_TOKEN_COST = 0.06 / 1000 * 0.89  # €0.06 per 1,000 tokens for output (converted to EUR)
    LOW_DETAIL_IMAGE_COST = 85  # Fixed token cost for low detail images
    HIGH_DETAIL_BASE_COST = 85  # Base token cost for high detail images
    HIGH_DETAIL_TILE_COST = 170  # Token cost per 512px square tile in high detail images

    def __init__(self):
        self.log_file = "logs.csv"
        # Create the log file with headers if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as csvfile:
                logwriter = csv.writer(csvfile)
                logwriter.writerow(["Date", "Type", "Num Tokens/Size (MB)", "Price (€)"])

    def log_cost(self, date, token_type, num_tokens, price):
        with open(self.log_file, 'a', newline='') as csvfile:
            logwriter = csv.writer(csvfile)
            logwriter.writerow([date, token_type, num_tokens, price])

    def calculate_token_cost(self, num_tokens, token_type):
        if token_type == "input":
            cost = num_tokens * self.INPUT_TOKEN_COST
        elif token_type == "output":
            cost = num_tokens * self.OUTPUT_TOKEN_COST
        else:
            raise ValueError("Unknown token type")
        
        self.log_cost(datetime.datetime.now(), token_type, num_tokens, cost)
        return cost

    def calculate_image_cost(self, image_path, detail="high"):
        with Image.open(image_path) as img:
            width, height = img.size
            
            if detail == "low":
                num_tokens = self.LOW_DETAIL_IMAGE_COST
            elif detail == "high":
                if width > 2048 or height > 2048:
                    if width > height:
                        new_width = 2048
                        new_height = int((height / width) * 2048)
                    else:
                        new_height = 2048
                        new_width = int((width / height) * 2048)
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                    width, height = img.size
                
                shortest_side = min(width, height)
                scale_factor = 768 / shortest_side
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                img = img.resize((new_width, new_height), Image.LANCZOS)
                
                num_tiles = (new_width // 512) * (new_height // 512)
                num_tokens = self.HIGH_DETAIL_BASE_COST + num_tiles * self.HIGH_DETAIL_TILE_COST
            
            cost = num_tokens * self.INPUT_TOKEN_COST  # Same token cost rate for input tokens
            self.log_cost(datetime.datetime.now(), "image", num_tokens, cost)
            return cost
