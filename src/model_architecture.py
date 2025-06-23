# model_architecture.py

import re
import torch
from PIL import Image
from torchvision import transforms
from transformers import VisionEncoderDecoderModel, DonutProcessor

from utils import extract_fields_from_raw


class OptimizedDonutInference:
    def __init__(self, model_path):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(self.device)
        self.processor = DonutProcessor.from_pretrained(model_path)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_path).to(self.device)
        self.model.eval()
        self.model = self.model.to(self.device).half()

        # Add any needed tokens — optional if already added before training
        special_tokens = [
            "<s_biodata>", "</s_biodata>",
            "<s_candidate>", "</s_candidate>",
            "<s_experience>", "</s_experience>",
            "<s_government_id>", "</s_government_id>"
        ]
        self.processor.tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})

    def predict(self, image_path):
        from torchvision import transforms

        if isinstance(image_path, str):
            image = Image.open(image_path).convert("RGB")
        else:
            image = image_path.convert("RGB")

        # Manual preprocessing to bypass DonutImageProcessor issues
        transform = transforms.Compose([
            transforms.Resize((1280, 960)),  # (height, width) → Donut expects 1280x960
            transforms.ToTensor(),  # converts to [0,1] and shape (C, H, W)
            transforms.Normalize(mean=[0.5], std=[0.5])  # normalize to [-1, 1] for all channels
        ])

       
        pixel_values = transform(image).unsqueeze(0).to(self.device).half()

        with torch.inference_mode():
            outputs = self.model.generate(
                pixel_values,
                max_length=512,
                early_stopping=True,
                pad_token_id=self.processor.tokenizer.pad_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id,
                use_cache=True,
                num_beams=1,
                no_repeat_ngram_size=3,
                bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True
            )

        sequence = self.processor.tokenizer.batch_decode(outputs.sequences)[0]
        match = re.search(r"<s_biodata>(.*?)</s_biodata>", sequence, re.DOTALL)

        if match:
            try:
                parsed = extract_fields_from_raw(match.group(1))
                return parsed
            except Exception as e:
                return {"error": "Failed to parse JSON", "raw": match.group(1), "exception": str(e)}

        return {"error": "No biodata found", "raw": sequence}
