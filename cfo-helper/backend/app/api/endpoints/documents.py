from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import os
import tempfile
from pathlib import Path
from app.services.llm_rag_agent import OpenLLMRAGAgent
from app.core.config import settings

router = APIRouter()

# Initialize the RAG agent
rag_agent = OpenLLMRAGAgent(model_name="mixtral-8x7b-32768")

@router.post("/upload/", response_model=Dict[str, Any])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a financial document.
    
    Supported formats: .txt, .pdf, .csv, .xlsx
    """
    try:
        # Create a temporary file to save the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process the document
        result = rag_agent.process_uploaded_document(temp_file_path)
        
        # Clean up the temporary file
        try:
            os.unlink(temp_file_path)
        except Exception as e:
            print(f"Warning: Could not delete temporary file {temp_file_path}: {e}")
        
        return result
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.post("/analyze-text/", response_model=Dict[str, Any])
async def analyze_text(text_data: Dict[str, str]):
    """
    Analyze financial text data directly.
    
    Expects a JSON with a 'text' field containing the financial data to analyze.
    """
    try:
        if 'text' not in text_data:
            raise HTTPException(status_code=400, detail="No 'text' field provided in the request")
        
        # Create a temporary file with the text content
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(text_data['text'])
            temp_file_path = temp_file.name
        
        # Process the text file
        result = rag_agent.process_uploaded_document(temp_file_path)
        
        # Clean up
        try:
            os.unlink(temp_file_path)
        except Exception as e:
            print(f"Warning: Could not delete temporary file {temp_file_path}: {e}")
        
        return result
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error analyzing text: {str(e)}")

@router.get("/supported-formats/")
async def get_supported_formats():
    """
    Get a list of supported document formats.
    """
    return {
        "supported_formats": [
            {"extension": ".txt", "type": "Text File"},
            {"extension": ".pdf", "type": "PDF Document"},
            {"extension": ".csv", "type": "CSV File"},
            {"extension": ".xlsx", "type": "Excel Spreadsheet"},
            {"extension": ".docx", "type": "Word Document"}
        ]
    }
