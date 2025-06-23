
# Document Information Extraction Pipeline

This project provides a complete pipeline for extracting structured information from document images. It uses a sophisticated two-stage approach to read a document and identify key-value pairs.

1.  **Donut Model**: A Vision Transformer-based model for Optical Character Recognition (OCR) that reads the text content of the document.
2.  **YOLO Model**: An object detection model used to identify the location (bounding boxes) of specific fields within the document (e.g., `candidatename`, `date`, etc.).

The `inference.py` script combines the outputs of these two models to produce a final, structured JSON file containing both the extracted text and its location.

##  Project Structure

```
project_folder/
├── data/
│   ├── sample_input/     # <-- PLACE YOUR INPUT IMAGES HERE
│   └── results/          # <-- OUTPUT JSON FILES WILL BE SAVED HERE
│
├── model/
│   ├── ... (donut model files) # <-- PLACE DONUT MODEL FILES HERE
│   └── yolo.pt           # <-- PLACE YOLO MODEL FILE HERE
│
├── src/
│   ├── inference.py      # Main script to run
│   ├── model_architecture.py
│   └── utils.py
│
└── README.md             # This file
```

##  Setup and Installation

Follow these steps to set up your environment to run the inference script.

### Prerequisites
- Python 3.10.6
- `pip` for package management
- A CUDA-enabled GPU is highly recommended for faster processing.

### Installation Steps

#### 1. Create a Virtual Environment (Highly Recommended)
Using a virtual environment prevents conflicts with other Python projects on your system.

```bash
# Create the virtual environment in your project folder
python -m venv venv

# Activate the environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 2. Install Required Libraries

With your virtual environment active, install all the required libraries by running this command in your terminal:

```bash
pip install -r requirements.txt
```

##  How to Run Inference

The script is designed to be simple to run. It will automatically process all images found in the `data/sample_input/` folder.

#### Step 1: Place Your Input Images
Copy all the document images you want to process (e.g., `.jpg`, `.png`, `.bmp`) into the `data/sample_input/` directory.

#### Step 2: Run the Script
1.  Navigate to the `src` directory in your terminal:
    ```bash
    cd src
    ```

2.  Execute the inference script:
    ```bash
    python inference.py
    ```

You will see status messages in the console as the models are loaded, followed by a progress bar that tracks the processing of your images.

## Understanding the Output

#### Accessing the Results
The processed results are saved as individual JSON files in the `data/results/` directory. The output filename will match the input image filename.
-   **Example:** An input image `data/sample_input/doc123.jpg` will produce an output file `data/results/doc123.json`.

#### Output Format
Each JSON file contains a list of fields detected in the document. Each field is an object with three keys:

-   `"Field name"`: The name of the detected field (e.g., `"candidatename"`).
-   `"Field value"`: The text extracted by the model for that field.
-   `"Coordinate"`: A list of four numbers `[x_min, y_min, x_max, y_max]` representing the bounding box coordinates of the field on the image.

**Example `doc123.json`:**
```json
[
  {
    "Field name": "candidatename",
    "Field value": "Dayita Bokshi",
    "Coordinate": [
      915,
      380,
      1559,
      481
    ]
  },
  {
    "Field name": "Father/husbandname",
    "Field value": "Laksh Bakshi",
    "Coordinate": [
      953,
      483,
      1615,
      581
    ]
  },
  {
    "Field name": "date",
    "Field value": "16/17/2023",
    "Coordinate": [
      635,
      2514,
      1101,
      2614
    ]
  }
]
```