from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os
import json
import requests
from pathlib import Path
from openai import OpenAI
import logging

# Import configuration
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """Simple vector store for document embeddings"""
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
        
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector store"""
        if not documents:
            return
            
        # Extract text and metadata
        texts = [doc['text'] for doc in documents]
        self.documents.extend(documents)
        
        # Generate embeddings (dummy implementation - replace with actual embedding model)
        embeddings = np.random.rand(len(texts), self.dimension).astype('float32')
        
        # Add to FAISS index
        if self.index.ntotal == 0:
            self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)
    
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if not self.documents:
            return []
            
        # Generate query embedding (dummy implementation)
        query_embedding = np.random.rand(1, self.dimension).astype('float32')
        
        # Search in FAISS
        distances, indices = self.index.search(query_embedding, k)
        
        # Return top k documents
        return [self.documents[idx] for idx in indices[0] if idx < len(self.documents)]

class OpenLLMRAGAgent:
    """
    RAG Agent using GROQ API for financial analysis with document processing capabilities.
    
    This agent provides:
    - Document processing and analysis
    - Financial scenario modeling
    - Natural language querying of financial data
    - Context-aware recommendations
    """
    
    def __init__(self, model_name: str = None):
        """Initialize the RAG agent with configuration"""
        self.model_name = model_name or settings.GROQ_MODEL
        self.vector_store = VectorStore(dimension=settings.VECTOR_STORE_DIMENSION)
        self.embedding_model = None
        self.client = None
        self.initialize_models()
        
    def initialize_models(self):
        """Initialize the embedding model and GROQ client"""
        try:
            logger.info("Initializing embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize GROQ client
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not configured in settings")
                
            logger.info("Initializing GROQ client...")
            self.client = OpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
            
            # Test the connection
            self._test_groq_connection()
            logger.info("RAG Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Agent: {str(e)}")
            raise
    
    def _test_groq_connection(self):
        """Test the connection to GROQ API"""
        try:
            self.client.models.list()
        except Exception as e:
            logger.error(f"Failed to connect to GROQ API: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the knowledge base"""
        if not self.embedding_model:
            self.initialize_models()
            
        # Generate embeddings
        texts = [doc['text'] for doc in documents]
        embeddings = self.embedding_model.encode(texts, convert_to_tensor=True)
        
        # Update vector store
        for doc, embedding in zip(documents, embeddings):
            doc['embedding'] = embedding.cpu().numpy()
        
        self.vector_store.add_documents(documents)
    
    def generate_response(self, query: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        """
        Generate a response using GROQ API with RAG
        
        Args:
            query: The user's query
            max_tokens: Maximum number of tokens in the response
            temperature: Controls randomness (0.0 to 1.0)
            
        Returns:
            str: Generated response
        """
        if not self.client:
            self.initialize_models()
        
        try:
            # Retrieve relevant context from vector store
            context_docs = self.vector_store.search(query, k=settings.SIMILARITY_TOP_K)
            context = "\n".join([doc['text'] for doc in context_docs])
            
            # Create system message with financial analysis instructions
            system_prompt = """You are an expert financial analyst with deep knowledge of business finance, 
            accounting principles, and strategic planning. Your role is to provide:
            
            1. Data-driven financial insights
            2. Actionable recommendations
            3. Risk assessment and mitigation
            4. Industry benchmarks and best practices
            5. Clear explanations of financial concepts
            
            Always format your response with markdown for better readability. Use tables, bullet points, 
            and section headers to organize information clearly.
            """
            
            # Create messages for the chat completion
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""Context:
    {context}

    User Query: {query}

    Please provide a comprehensive financial analysis and recommendations. Include:
    1. Key insights from the data
    2. Actionable recommendations
    3. Potential risks and opportunities
    4. Relevant financial metrics
    """}
            ]
            
            logger.info(f"Sending request to GROQ API with model: {self.model_name}")
            
            # Call GROQ API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                timeout=30  # 30 seconds timeout
            )
            
            result = response.choices[0].message.content.strip()
            logger.debug(f"Received response from GROQ API: {result[:200]}...")
            
            return result
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def analyze_financial_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a financial scenario using GROQ API with RAG"""
        # Convert scenario to natural language
        scenario_text = "\n".join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in scenario.items()])
        
        # Generate comprehensive analysis
        analysis = self.generate_response(
            f"""Analyze this financial scenario in detail. For each aspect, provide:
            1. Current status and trends
            2. Impact on financial health
            3. Potential risks and opportunities
            4. Industry benchmarks if available
            
            Scenario:
            {scenario_text}"""
        )
        
        # Generate specific recommendations
        recommendations = self.generate_response(
            f"""Based on this financial scenario analysis, provide specific, 
            actionable recommendations. Include:
            1. Immediate actions
            2. Short-term strategies (1-3 months)
            3. Long-term considerations (3-12 months)
            4. Key performance indicators to monitor
            
            Scenario:
            {scenario_text}"""
        )
        
        return {
            "scenario": scenario,
            "analysis": analysis,
            "recommendations": recommendations,
            "key_metrics": self._extract_key_metrics(analysis + "\n" + recommendations)
        }
    
    def _extract_key_metrics(self, text: str) -> Dict[str, Any]:
        """Extract key financial metrics from the analysis"""
        prompt = f"""Extract key financial metrics and their values from the following text. 
        Return only a JSON object with metric names as keys and values as numbers or strings.
        
        Text: {text}
        
        Example output:
        {{
            "revenue_growth": 15.5,
            "profit_margin": 20.0,
            "runway_months": 8.5
        }}
        
        Extracted metrics:"""
        
        try:
            response = self.generate_response(prompt)
            # Clean and parse the response
            response = response.strip().strip('`').replace('json\n', '').strip()
            return json.loads(response)
        except Exception as e:
            return {"error": f"Failed to extract metrics: {str(e)}"}
    
    def process_uploaded_document(self, file_path: str) -> Dict[str, Any]:
        """Process an uploaded financial document"""
        try:
            # Simple text extraction (in a real app, you'd use proper document parsing)
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract financial data using the LLM
            analysis = self.generate_response(
                f"""Extract key financial information from this document. 
                Include revenue, expenses, profit, and any other relevant metrics.
                
                Document content:
                {content[:10000]}  # Limit content size for the API
                """
            )
            
            # Generate insights
            insights = self.generate_response(
                f"""Based on this financial data, provide key insights and recommendations:
                
                {analysis}"""
            )
            
            return {
                "status": "success",
                "analysis": analysis,
                "insights": insights,
                "metrics": self._extract_key_metrics(analysis)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to process document: {str(e)}"
            }

# Example usage
if __name__ == "__main__":
    # Initialize RAG agent with a small open-source model
    rag_agent = OpenLLMRAGAgent(model_name="gpt2")
    
    # Add some financial documents to the knowledge base
    documents = [
        {"text": "A company with high revenue growth but negative cash flow may face liquidity issues."},
        {"text": "Reducing marketing spend can improve short-term cash flow but may impact long-term growth."},
        {"text": "Hiring more employees increases fixed costs but can drive revenue growth if managed properly."}
    ]
    rag_agent.add_documents(documents)
    
    # Analyze a financial scenario
    scenario = {
        "revenue_growth": "15%",
        "cash_flow": "negative",
        "marketing_spend": "increasing",
        "employee_count": "growing"
    }
    
    result = rag_agent.analyze_financial_scenario(scenario)
    print("\nAnalysis:", result["analysis"])
    print("\nRecommendations:", result["recommendations"])
