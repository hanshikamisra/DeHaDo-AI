# src/inference.py

import json
import os
import torch
from ultralytics import YOLO
from tqdm import tqdm

# Local imports
from model_architecture import OptimizedDonutInference
from utils import convert_flat_to_structured

# Define the desired order for the final output as a constant
FIELD_ORDER = [
    "candidatename", "Father/husbandname", "Dateofbirth", "qualification", "maritalstatus",
    "gender", "nationality", "bloodgroup", "experience", "experience1", "presentaddress",
    "permanentaddress", "AlternateNo", "contactnumber", "languageknown", "referencescmob1",
    "referencescmob2", "aadhaarcard", "pancard", "place", "date"
]

def run_single_image_inference(donut_inferencer, yolo_model, image_path):
    """
    Runs the full inference pipeline for a single image and merges results.
    """
    # Part 1: Donut Model for Text Extraction
    donut_result_flat = donut_inferencer.predict(image_path)
    
    if "error" in donut_result_flat:
        tqdm.write(f"Warning: Donut model failed for {os.path.basename(image_path)}. Error: {donut_result_flat.get('error')}")
        structured_output = {} 
    else:
        structured_output = convert_flat_to_structured(donut_result_flat)

    # Part 2: YOLO Model for Field Detection
    yolo_results = yolo_model(image_path, verbose=False)[0]
    class_names = yolo_model.names
    
    detected_fields = {}
    for box in yolo_results.boxes:
        cls_id = int(box.cls[0])
        class_name = class_names[cls_id]
        coords = [int(x) for x in box.xyxy[0].tolist()]
        detected_fields[class_name] = coords

    # Part 3: Merge Results
    final_output = []
    for field_name in FIELD_ORDER:
        if field_name in detected_fields:
            field_value = structured_output.get(field_name, "")
            final_output.append({
                "Field name": field_name,
                "Field value": field_value,
                "Coordinate": detected_fields[field_name]
            })
            
    return final_output

def main():
    """
    Main execution function.
    """
    # --- Define Paths based on the fixed directory structure ---
    # The script is in 'src', so we navigate relative to its location.
    SRC_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SRC_DIR)
    
    IMAGE_DIR = os.path.join(PROJECT_ROOT, "data", "sample_input")
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "results")
    DONUT_MODEL_PATH = os.path.join(PROJECT_ROOT, "model")
    YOLO_MODEL_PATH = os.path.join(PROJECT_ROOT, "model", "yolo.pt")

    # --- Environment Check ---
    cuda_available = torch.cuda.is_available()
    print(f"CUDA available: {cuda_available}")
    if cuda_available:
        print(f"GPU name: {torch.cuda.get_device_name(0)}")
    
    # --- Initialize Models ---
    print("\n--- Initializing Models ---")
    donut_inferencer = OptimizedDonutInference(DONUT_MODEL_PATH)
    yolo_model = YOLO(YOLO_MODEL_PATH)
    print("Models initialized successfully.")

    # --- Create Output Directory ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Input directory: {IMAGE_DIR}")
    print(f"Output will be saved to: {OUTPUT_DIR}")

    # --- Identify and Process Images ---
    supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    image_files = [f for f in os.listdir(IMAGE_DIR) if os.path.splitext(f)[1].lower() in supported_extensions]

    if not image_files:
        print(f"No images found in directory: {IMAGE_DIR}")
        return

    print(f"\nFound {len(image_files)} images to process.")

    for image_filename in tqdm(image_files, desc="Processing Images"):
        image_path = os.path.join(IMAGE_DIR, image_filename)
        
        try:
            final_result = run_single_image_inference(donut_inferencer, yolo_model, image_path)
            
            # Save result to a JSON file with the same name as the image
            json_filename = os.path.splitext(image_filename)[0] + '.json'
            output_path = os.path.join(OUTPUT_DIR, json_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_result, f, indent=2, ensure_ascii=False)

        except Exception as e:
            tqdm.write(f"FATAL: Failed to process {image_filename}. Error: {e}")
            error_log_path = os.path.join(OUTPUT_DIR, os.path.splitext(image_filename)[0] + '_error.txt')
            with open(error_log_path, 'w') as f:
                f.write(f"An exception occurred during processing:\n{str(e)}")
                
    print("\nProcessing complete.")

if __name__ == "__main__":
    main()