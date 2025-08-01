from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer
import torch
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_embedding_model():
    try:
        logger.info("Loading embedding model 'all-MiniLM-L6-v2'")
        model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda' if torch.cuda.is_available() else 'cpu')
        logger.info("Embedding model loaded successfully")
        return model
    except Exception as e:
        logger.error("Error loading embedding model: %s", str(e))
        raise

def get_llm_model():
    model_name = "distilgpt2"
    try:
        logger.info("Loading tokenizer for %s", model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        logger.info("Tokenizer loaded successfully")

        logger.info("Loading model %s", model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True
        )
        logger.info("Model loaded successfully")

        logger.info("Creating text-generation pipeline")
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            return_full_text=False
        )
        logger.info("Pipeline created successfully")
        return pipe
    except Exception as e:
        logger.error("Error loading LLM: %s", str(e))
        raise