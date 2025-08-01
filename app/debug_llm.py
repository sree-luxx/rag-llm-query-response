import logging
import os
from app.model_loader import get_llm_model

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    logger.info("Checking HF_TOKEN")
    hf_token = os.getenv("HF_TOKEN")
    logger.info("HF_TOKEN: %s", "Set" if hf_token else "Not set")
    if not hf_token:
        raise ValueError("HF_TOKEN not set. Run: set HF_TOKEN=your_token in Command Prompt")
    
    logger.info("Starting LLM loading test")
    llm = get_llm_model()
    logger.info("LLM loaded successfully, testing sample inference")
    test_prompt = "Test prompt: What is 1+1? Answer concisely:"
    result = llm(test_prompt, max_new_tokens=50, do_sample=False)[0]['generated_text']
    logger.info("Sample inference result: %s", result)
except Exception as e:
    logger.error("LLM loading test failed: %s", str(e))