import os
import logging
from dotenv import load_dotenv
from google import genai

# Load tracking properties configurations
load_dotenv()

# Logger settings framework implementation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate variable availability before initializations
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("System configuration missing: GEMINI_API_KEY is not set in the environment properties.")
    exit(1)

# Initialize standard V1 Google GenAI Client configuration matrix
client = genai.Client(api_key=api_key)

logger.info("Connecting to Google GenAI API core tracking endpoints...")

try:
    # 1. SDK Syntax Sync: Changed from client.models.list() to the modern list_page() generator utility
    models_pager = client.models.list_page()
    
    print("\n=======================================================")
    print("🚀 Active System Validated Production Gemini Models:")
    print("=======================================================\n")
    
    # Iterate dynamically over pages array collection metrics response structure
    for model in models_pager:
        # Filter strings parameters output to highlight production models cleanly
        if "gemini" in model.name.lower():
            print(f"🔹 Model Reference: {model.name}")
            print(f"   Details: {model.description}\n")

    print("=======================================================")

except Exception as e:
    logger.error(f"Failed to query available endpoint architectures registry values: {str(e)}")