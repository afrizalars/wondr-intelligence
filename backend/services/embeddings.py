import torch
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.device = 'cpu'  # Force CPU as per requirements
        self.model = None
        self._model_loaded = False
    
    def _initialize_model(self):
        if self._model_loaded:
            return
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device
            )
            # Set to eval mode for inference
            self.model.eval()
            self._model_loaded = True
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def embed_text(self, text: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        self._initialize_model()  # Load model on first use
        if isinstance(text, str):
            text = [text]
        
        with torch.no_grad():
            embeddings = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=normalize,
                show_progress_bar=False,
                batch_size=32
            )
        
        return embeddings
    
    def embed_batch(self, texts: List[str], batch_size: int = 32, normalize: bool = True) -> np.ndarray:
        self._initialize_model()  # Load model on first use
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.embed_text(batch, normalize=normalize)
            all_embeddings.append(embeddings)
        
        return np.vstack(all_embeddings)
    
    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        # Assuming normalized embeddings, cosine similarity is just dot product
        return float(np.dot(embedding1, embedding2))
    
    def prepare_text_for_embedding(self, data: dict, source_table: str) -> str:
        if source_table == 'transactions_raw':
            text = f"Transaction: {data.get('description', '')} "
            if data.get('merchant_name'):
                text += f"at {data['merchant_name']} "
            text += f"for amount {data.get('amount', 0)} {data.get('currency', 'IDR')} "
            text += f"on {data.get('transaction_date', '')} "
            if data.get('category'):
                text += f"category: {data['category']}"
            return text.strip()
        
        elif source_table == 'transfer_contacts':
            return f"Contact: {data.get('contact_name', '')} at {data.get('bank_name', '')} " \
                   f"account {data.get('account_number', '')} type: {data.get('contact_type', '')}"
        
        elif source_table == 'promos':
            return f"Promo: {data.get('title', '')} {data.get('description', '')} " \
                   f"code: {data.get('promo_code', '')} valid until {data.get('valid_until', '')}"
        
        elif source_table == 'customer_profiles':
            return f"Customer profile: {data.get('age', '')} years old, " \
                   f"{data.get('gender', '')}, {data.get('occupation', '')}, " \
                   f"income: {data.get('income_range', '')}, risk: {data.get('risk_profile', '')}"
        
        return str(data)

embedding_service = EmbeddingService()