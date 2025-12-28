"""
Image Captioner Module
Generates ELABORATE descriptions for extracted images using BLIP model
"""
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch


class ImageCaptioner:
    """Generate elaborate captions for images using BLIP model"""
    
    def __init__(self, model_name="Salesforce/blip-image-captioning-large"):
        """
        Initialize the BLIP model for image captioning
        Using LARGE model for more detailed descriptions
        
        Args:
            model_name: Hugging Face model identifier
        """
        print("Loading BLIP model... This may take a moment on first run.")
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name)
        
        # Use GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        print(f"Model loaded on {self.device}")
    
    def generate_caption(self, image_path, max_length=100, num_beams=5):
        """
        Generate an ELABORATE caption for a single image
        
        Args:
            image_path: Path to the image file
            max_length: Maximum length of generated caption
            num_beams: Number of beams for beam search (higher = better quality)
            
        Returns:
            str: Generated elaborate caption
        """
        try:
            # Load image
            image = Image.open(image_path).convert("RGB")
            
            # Process image
            inputs = self.processor(image, return_tensors="pt").to(self.device)
            
            # Generate caption with enhanced parameters for better descriptions
            outputs = self.model.generate(
                **inputs, 
                max_length=max_length,
                num_beams=num_beams,
                length_penalty=1.0,
                early_stopping=True,
                repetition_penalty=1.5
            )
            
            # Decode caption
            caption = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            return caption
            
        except Exception as e:
            print(f"Error generating caption for {image_path}: {e}")
            return "Caption generation failed"
    
    def generate_detailed_caption(self, image_path, max_length=150):
        """
        Generate a highly detailed caption with multiple prompts
        Combines unconditional and conditional captions for richer descriptions
        
        Args:
            image_path: Path to the image file
            max_length: Maximum length of generated caption
            
        Returns:
            str: Detailed combined caption
        """
        try:
            # Load image
            image = Image.open(image_path).convert("RGB")
            
            # Generate unconditional caption (what is in the image)
            inputs = self.processor(image, return_tensors="pt").to(self.device)
            outputs = self.model.generate(
                **inputs, 
                max_length=max_length,
                num_beams=5,
                length_penalty=1.0,
                repetition_penalty=1.5
            )
            base_caption = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            # Generate conditional caption with descriptive prompt
            prompts = [
                "a detailed description of",
                "this image shows"
            ]
            
            conditional_captions = []
            for prompt in prompts:
                inputs = self.processor(image, prompt, return_tensors="pt").to(self.device)
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=5,
                    length_penalty=1.0,
                    repetition_penalty=1.5
                )
                caption = self.processor.decode(outputs[0], skip_special_tokens=True)
                if caption and caption != base_caption:
                    conditional_captions.append(caption)
            
            # Combine captions for richer description
            if conditional_captions:
                # Use the most detailed caption
                all_captions = [base_caption] + conditional_captions
                detailed_caption = max(all_captions, key=len)
                return detailed_caption
            else:
                return base_caption
            
        except Exception as e:
            print(f"Error generating detailed caption: {e}")
            return self.generate_caption(image_path)
    
    def generate_captions_batch(self, image_paths, max_length=200, detailed=True):
        """
        Generate elaborate captions for multiple images
        
        Args:
            image_paths: List of image file paths
            max_length: Maximum length of generated captions
            detailed: Whether to use detailed caption generation
            
        Returns:
            list: List of dictionaries with image paths and captions
        """
        results = []
        
        for img_path in image_paths:
            print(f"Generating elaborate description for: {img_path}")
            
            if detailed:
                caption = self.generate_detailed_caption(img_path, max_length)
            else:
                caption = self.generate_caption(img_path, max_length, num_beams=5)
            
            results.append({
                "image_path": img_path,
                "caption": caption
            })
        
        return results
    
    def conditional_caption(self, image_path, prompt="A detailed description of", max_length=100):
        """
        Generate a caption with a custom text prompt for more control
        
        Args:
            image_path: Path to the image file
            prompt: Text prompt to guide caption generation
            max_length: Maximum length of generated caption
            
        Returns:
            str: Generated caption
        """
        try:
            # Load image
            image = Image.open(image_path).convert("RGB")
            
            # Process image with text prompt
            inputs = self.processor(image, prompt, return_tensors="pt").to(self.device)
            
            # Generate caption
            outputs = self.model.generate(
                **inputs, 
                max_length=max_length,
                num_beams=5,
                length_penalty=1.0,
                repetition_penalty=1.5
            )
            
            # Decode caption
            caption = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            return caption
            
        except Exception as e:
            print(f"Error generating conditional caption: {e}")
            return "Caption generation failed"
