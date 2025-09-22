from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime
import uuid

from app.services.rag_agent import RAGAgent, FinancialContext, UserScenario, FinancialAnalysis

router = APIRouter()
rag_agent = RAGAgent()

@router.post("/context", response_model=Dict[str, str])
async def update_financial_context(context_data: Dict[str, Any]):
    """
    Update the financial context for a company
    """
    try:
        # Generate a unique ID if not provided
        if 'id' not in context_data:
            context_data['id'] = f"ctx_{uuid.uuid4().hex[:8]}"
        
        # Ensure company_id is provided
        if 'company_id' not in context_data:
            raise ValueError("company_id is required")
        
        # Create FinancialContext object
        context = FinancialContext(**context_data)
        
        # Add/update context in the RAG agent
        rag_agent.add_financial_context(context)
        
        return {"status": "success", "context_id": context.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/scenario", response_model=Dict[str, str])
async def create_scenario(company_id: str, changes: Dict[str, Any]):
    """
    Create a new financial scenario for analysis
    """
    try:
        # Create a new scenario
        scenario_id = rag_agent.create_scenario(company_id, changes)
        
        return {"status": "success", "scenario_id": scenario_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analyze/{scenario_id}", response_model=Dict[str, Any])
async def analyze_scenario(scenario_id: str):
    """
    Analyze a financial scenario and return the results
    """
    try:
        # Analyze the scenario
        analysis = rag_agent.analyze_scenario(scenario_id)
        
        # Convert to dict for JSON serialization
        result = analysis.dict()
        
        # Convert datetime objects to ISO format
        for field in ['last_updated', 'timestamp', 'created_at']:
            if field in result and result[field]:
                result[field] = result[field].isoformat()
            if 'original_context' in result and field in result['original_context']:
                result['original_context'][field] = result['original_context'][field].isoformat()
            if 'updated_context' in result and field in result['updated_context']:
                result['updated_context'][field] = result['updated_context'][field].isoformat()
        
        return {"status": "success", "analysis": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{scenario_id}", response_model=Dict[str, str])
async def get_analysis_summary(scenario_id: str):
    """
    Get a human-readable summary of a financial analysis
    """
    try:
        # Analyze the scenario
        analysis = rag_agent.analyze_scenario(scenario_id)
        
        return {
            "status": "success", 
            "summary": analysis.summary,
            "scenario_id": scenario_id,
            "company_id": analysis.company_id,
            "created_at": analysis.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
