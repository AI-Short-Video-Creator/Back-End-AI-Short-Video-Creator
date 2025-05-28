import os
import base64
import requests
from app.image.dto import ImageGenerateDTO
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

class ImageService:
    _instance = None
    
    # Hugging Face Stable Diffusion endpoint
    HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    HF_TOKEN = os.getenv("HF_TOKEN")

    # Get API token from environment variable

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        if not self.HF_TOKEN:
            print("Warning: HF_TOKEN environment variable not set. Please set it to use the API.")
    
    def generate_image(self, dto: ImageGenerateDTO) -> list[str]:
        """
        Generate images from a long script by splitting it into sentences.
        
        Args:
            dto: Data Transfer Object containing the script to use as prompt
            
        Returns:
            list[str]: List of paths to the generated image files
        """
        if not self.HF_TOKEN:
            raise ValueError("API token not configured. Please set the HF_TOKEN environment variable.")
        
        # Extract script from DTO and split by period
        full_script = dto.script
        sentences = [s.strip() for s in full_script.split('.') if s.strip()]
        
        print(f"Split script into {len(sentences)} sentences")
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        image_paths = []
        
        # Generate an image for each sentence
        for i, sentence in enumerate(sentences):
            if len(sentence) < 10:  # Skip very short sentences
                continue
                
            headers = {
                "Authorization": f"Bearer {self.HF_TOKEN}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "inputs": sentence,
                "parameters": {
                    "num_inference_steps": 50,
                    "guidance_scale": 7.5
                }
            }
            
            try:
                print(f"Generating image for sentence {i+1}/{len(sentences)}: {sentence[:50]}...")
                response = requests.post(self.HF_API_URL, headers=headers, json=payload)
                response.raise_for_status()
                
                # Generate unique filename
                image_filename = f"output/image_{i+1}_{uuid.uuid4()}.png"
                
                # The API returns the image bytes directly
                if response.headers.get("content-type", "").startswith("image/"):
                    # Save the image to a file
                    with open(image_filename, "wb") as f:
                        f.write(response.content)
                    image_paths.append(image_filename)
                    print(f"Image saved to {image_filename}")
                else:
                    # If we get JSON response, it might be an error
                    result = response.json()
                    if isinstance(result, dict) and "error" in result:
                        print(f"API Error for sentence {i+1}: {result['error']}")
                    else:
                        print(f"Unexpected response format for sentence {i+1}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Error calling API for sentence {i+1}: {str(e)}")
                continue  # Continue with next sentence even if one fails
        
        return image_paths