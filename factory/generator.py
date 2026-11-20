import os
import json
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUTPUT_DIR = "generated_tasks"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def add_warehouse_noise(img: Image.Image, difficulty: int) -> Image.Image:
    if difficulty >= 2:
        angle = random.uniform(-3 * difficulty, 3 * difficulty)
        img = img.rotate(angle, expand=True, fillcolor="white")
        
    if difficulty >= 3:
        draw = ImageDraw.Draw(img, "RGBA")
        x = random.randint(180, 320)
        y = random.randint(180, 260)
        draw.rectangle([x, y, x + 160, y + 50], outline=(220, 20, 20, 180), width=4)
        draw.text((x + 15, y + 15), "INSPECTED", fill=(220, 20, 20, 180))

    if difficulty >= 4:
        img = img.filter(ImageFilter.GaussianBlur(radius=difficulty * 0.35))

    if difficulty == 5:
        arr = np.array(img).astype(np.int16)
        noise = np.random.normal(0, 22, arr.shape)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)

    return img

def generate_task(task_id: int, difficulty: int = 1) -> dict:
    items = [
        {"sku": "MED-901", "qty": random.randint(2, 10), "hazmat": False},
        {"sku": "CHM-404", "qty": random.randint(1, 5), "hazmat": True},
        {"sku": "EQP-112", "qty": random.randint(3, 12), "hazmat": False},
    ]
    total_hazmat_qty = sum(item["qty"] for item in items if item["hazmat"])
    
    img = Image.new("RGB", (600, 400), color="white")
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([20, 20, 580, 380], outline="black", width=3)
    draw.text((40, 40), f"WAREHOUSE MANIFEST #{1000 + task_id}", fill="black")
    draw.line([20, 80, 580, 80], fill="black", width=2)
    
    draw.text((40, 100), "SKU CODE        QTY        HAZMAT STATUS", fill="black")
    y_pos = 140
    for item in items:
        status = "YES [FLAMMABLE]" if item["hazmat"] else "NO"
        row_text = f"{item['sku']}          {item['qty']}          {status}"
        draw.text((40, y_pos), row_text, fill="black")
        y_pos += 45

    final_img = add_warehouse_noise(img, difficulty)
    
    image_filename = f"task_{task_id}_diff_{difficulty}.png"
    image_path = os.path.join(OUTPUT_DIR, image_filename)
    final_img.save(image_path)

    return {
        "task_id": task_id,
        "difficulty": difficulty,
        "image_path": image_path,
        "image_url": f"/static/{image_filename}",
        "question": "What is the total quantity of items marked as HAZMAT? Reply with a single integer only.",
        "ground_truth": str(total_hazmat_qty)
    }

if __name__ == "__main__":
    sample = generate_task(task_id=1, difficulty=4)
    print(json.dumps(sample, indent=2))

