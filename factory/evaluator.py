import os
import re
import time
from dotenv import load_dotenv
from PIL import Image
from google import genai

load_dotenv()
client = genai.Client()

def evaluate_model(task: dict, model_name: str = "gemini-2.5-flash") -> dict:
    # Pause 2 seconds between requests to stay safely within Free Tier rate limits
    time.sleep(2)
    img = Image.open(task["image_path"])
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[img, task["question"]]
        )
        raw_output = response.text.strip()
        numbers = re.findall(r"\d+", raw_output)
        predicted_answer = numbers if numbers else "ERR"
    except Exception as e:
        raw_output = str(e)
        predicted_answer = "API_ERR"

    is_correct = (predicted_answer == task["ground_truth"])
    
    return {
        "task_id": task["task_id"],
        "difficulty": task["difficulty"],
        "model": model_name,
        "ground_truth": task["ground_truth"],
        "model_raw_output": raw_output,
        "parsed_prediction": predicted_answer,
        "passed": is_correct
    }
