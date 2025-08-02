from app.utils import extract_pdf_text, chunk_text
from app.model_loader import get_embedding_model, get_llm_model
import numpy as np
import faiss
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_output(text):
    """Remove repetitive sentences and irrelevant content from LLM output."""
    if not text:
        return "No answer generated"
    sentences = re.split(r'[.\n]+', text.strip())
    seen = set()
    cleaned = []
    for s in sentences:
        s = s.strip()
        if s and s not in seen and all(keyword not in s.lower() for keyword in ["maximum amount", "provision of", "surgery", "hospital", "transfer", "policy covers", "pregnant", "period of the policy"]):
            seen.add(s)
            cleaned.append(s)
    return '. '.join(cleaned)[:80] if cleaned else "No answer generated"

def run_pipeline(pdf_url, questions):
    try:
        logger.info("Starting pipeline with PDF URL: %s", pdf_url)
        text = extract_pdf_text(pdf_url)
        if not text:
            logger.error("No text extracted from PDF")
            return {"answers": ["No text extracted from PDF" for _ in questions]}

        logger.info("Text extracted, length: %d characters", len(text))
        chunks = chunk_text(text, max_words=10)
        if not chunks:
            logger.error("No valid chunks created")
            return {"answers": ["No valid chunks created" for _ in questions]}

        logger.info("Created %d chunks", len(chunks))
        embedder = get_embedding_model()
        logger.info("Encoding chunks for embeddings")
        chunk_embeddings = embedder.encode(chunks, show_progress_bar=False, batch_size=256)
        
        logger.info("Initializing FAISS index with dimension: %d", chunk_embeddings.shape[1])
        index = faiss.IndexFlatL2(chunk_embeddings.shape[1])
        index.add(np.array(chunk_embeddings, dtype=np.float32))
        
        llm = get_llm_model()
        logger.info("LLM loaded successfully")
        answers = []
        for q in questions:
            logger.info("Processing question: %s", q)
            q_vec = embedder.encode([q], show_progress_bar=False)
            D, I = index.search(np.array(q_vec, dtype=np.float32), k=1)
            top_chunks = [chunks[i] for i in I[0] if i < len(chunks)]
            
            context = "\n".join(top_chunks)[:80] if top_chunks else "No relevant context found."
            logger.info("Top chunks retrieved: %d, context length: %d", len(top_chunks), len(context))
            prompt = f"Using the context, answer the question in one precise sentence.\nContext: {context}\nQuestion: {q}\nAnswer:"
            try:
                output = llm(
                    prompt,
                    max_new_tokens=20,  # Slightly increased
                    do_sample=False,
                    pad_token_id=llm.tokenizer.eos_token_id,
                    return_full_text=False,
                    temperature=0.1
                )[0]['generated_text'].strip()
                answer = clean_output(output)
                logger.info("Answer generated for question: %s", answer)
                answers.append(answer)
            except Exception as e:
                logger.error("LLM error for question '%s': %s", q, str(e))
                answers.append("Error generating answer")

        return {"answers": answers}
    except Exception as e:
        logger.error("Pipeline error: %s", str(e))
        return {"answers": ["Pipeline error occurred" for _ in questions]}