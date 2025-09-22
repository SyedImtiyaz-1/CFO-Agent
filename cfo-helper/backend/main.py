from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import file processor
from app.utils.file_processor import FileProcessor

# Import API endpoints
from app.api.endpoints import rag as rag_endpoints
from app.api.endpoints import documents as document_endpoints

# Import Pathway integration with fallback
try:
    from app.pathway_integration import pathway_processor
    from app.pathway_realtime import realtime_processor
    PATHWAY_AVAILABLE = True
except ImportError:
    print("Pathway not available - using fallback mode")
    PATHWAY_AVAILABLE = False
    pathway_processor = None
    realtime_processor = None

app = FastAPI(title="CFO Helper API",
             description="API for financial scenario planning and analysis",
             version="1.0.0")

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:8000",
    os.getenv("FRONTEND_URL", ""),
]

# CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# In-memory storage (replace with database in production)
scenarios_db = []
usage_counter = 0

# Initialize file processor
file_processor = FileProcessor()

# Include API endpoints
routers = [
    {
        "router": rag_endpoints.router,
        "prefix": "/api/rag",
        "tags": ["RAG Agent"]
    },
    {
        "router": document_endpoints.router,
        "prefix": "/api/documents",
        "tags": ["Documents"]
    }
]

for route in routers:
    app.include_router(
        route["router"],
        prefix=route["prefix"],
        tags=route["tags"],
        responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
    )

class ScenarioInput(BaseModel):
    current_cash: float
    monthly_revenue: float
    monthly_expenses: float
    new_hires: int = 0
    salary_per_hire: float = 0
    marketing_spend: float = 0
    price_increase_percent: float = 0
    months_to_forecast: int = 12

# New Pathway-based models
class FileUploadRequest(BaseModel):
    filename: str
    file_data: str  # base64 encoded
    file_type: str

class PathwayScenarioRequest(BaseModel):
    company_id: str = "default_company"
    spending_change: float = 0
    pricing_change: float = 0
    hiring_count: int = 0
    marketing_budget: float = 0

class ScenarioResult(BaseModel):
    scenario_id: str
    timestamp: str
    input: ScenarioInput
    monthly_forecast: List[dict]
    total_months_of_runway: int
    final_cash_balance: float

# Helper functions
def calculate_runway(scenario: ScenarioInput) -> ScenarioResult:
    """Calculate financial forecast based on scenario inputs"""
    global usage_counter
    usage_counter += 1
    
    monthly_data = []
    current_balance = scenario.current_cash
    months_of_runway = 0
    
    # Calculate adjusted revenue with price increase
    adjusted_revenue = scenario.monthly_revenue * (1 + scenario.price_increase_percent / 100)
    
    # Calculate additional expenses from new hires
    hiring_costs = scenario.new_hires * scenario.salary_per_hire
    
    for month in range(1, scenario.months_to_forecast + 1):
        # Calculate monthly cash flow
        monthly_net = (adjusted_revenue - scenario.monthly_expenses - hiring_costs - scenario.marketing_spend)
        current_balance += monthly_net
        
        monthly_data.append({
            "month": month,
            "revenue": adjusted_revenue,
            "expenses": scenario.monthly_expenses + hiring_costs + scenario.marketing_spend,
            "net_income": monthly_net,
            "balance": current_balance
        })
        
        # Track how many months until we run out of money
        if current_balance > 0:
            months_of_runway = month
        
        # Stop if we run out of money
        if current_balance <= 0:
            break
    
    # Generate a unique ID for this scenario
    scenario_id = f"scn_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return ScenarioResult(
        scenario_id=scenario_id,
        timestamp=datetime.now().isoformat(),
        input=scenario.dict(),
        monthly_forecast=monthly_data,
        total_months_of_runway=months_of_runway,
        final_cash_balance=current_balance
    )

# API Endpoints
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CFO Helper API",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/scenarios/analyze", response_model=ScenarioResult)
async def analyze_scenario(scenario: ScenarioInput):
    """Analyze a financial scenario"""
    try:
        result = calculate_runway(scenario)
        scenarios_db.append(result.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload and process multiple files"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    results = []
    for file in files:
        try:
            result = await file_processor.process_upload(file)
            results.append({
                "filename": file.filename,
                "status": "processed",
                "data": result
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "message": f"Processed {len([r for r in results if r['status'] == 'processed'])} files successfully",
        "results": results
    }

@app.post("/api/analyze")
async def analyze_files(files: List[UploadFile] = File(...)):
    """Analyze data from uploaded files"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    processed_data = []
    for file in files:
        try:
            result = await file_processor.process_upload(file)
            processed_data.append({
                "filename": file.filename,
                "data": result
            })
        except Exception as e:
            continue  # Skip files that can't be processed
    
    if not processed_data:
        raise HTTPException(status_code=400, detail="Could not process any of the provided files")
    
    # Combine data from all files (simple concatenation for demonstration)
    combined_data = {
        "columns": processed_data[0]["data"]["columns"] if processed_data else [],
        "data": [],
        "stats": {}
    }
    
    for item in processed_data:
        combined_data["data"].extend(item["data"]["data"])
        # Combine statistics (simple merge for demonstration)
        for col, stats in item["data"].get("stats", {}).items():
            if col not in combined_data["stats"]:
                combined_data["stats"][col] = stats
    
    return {
        "message": f"Analyzed data from {len(processed_data)} files",
        "total_rows": len(combined_data["data"]),
        "columns": combined_data["columns"],
        "stats": combined_data["stats"],
        "data": combined_data["data"]
    }

@app.get("/api/usage")
async def get_usage():
    """Get usage statistics"""
    global usage_counter
    return {
        "total_scenarios_run": len(scenarios_db),
        "api_calls": usage_counter,
        "last_scenario_time": scenarios_db[-1]["timestamp"] if scenarios_db else None
    }

# New Pathway-powered endpoints
@app.post("/api/pathway/upload")
async def pathway_upload_file(request: FileUploadRequest):
    """Upload and process file using Pathway"""
    if not PATHWAY_AVAILABLE:
        # Fallback processing without Pathway
        return {
            "status": "success",
            "filename": request.filename,
            "result": {
                "type": "fallback",
                "message": "File uploaded successfully. Pathway processing will be available once installation completes.",
                "processed_at": datetime.now().isoformat()
            }
        }
    
    try:
        result = pathway_processor.process_uploaded_file(
            request.file_data,
            request.filename,
            request.file_type
        )
        return {
            "status": "success",
            "filename": request.filename,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File processing failed: {str(e)}")

@app.get("/api/pathway/context/{company_id}")
async def get_financial_context(company_id: str):
    """Get financial context for a company using Pathway"""
    try:
        # Mock financial context - in production, this would come from Pathway's real-time data
        context = {
            "monthly_revenue": 50000,
            "monthly_expenses": 35000,
            "cash_balance": 200000,
            "runway_months": 13,
            "last_updated": datetime.now().isoformat(),
            "data_sources": ["uploaded_files", "pathway_stream"]
        }
        return context
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Context retrieval failed: {str(e)}")

@app.post("/api/pathway/scenario")
async def analyze_pathway_scenario(request: PathwayScenarioRequest):
    """Analyze scenario using Pathway's real-time processing"""
    global usage_counter
    
    if not PATHWAY_AVAILABLE:
        # Fallback scenario analysis
        base_data = {
            "monthly_revenue": 50000,
            "monthly_expenses": 35000,
            "cash_balance": 200000,
            "runway_months": 13
        }
        
        # Simple calculation without Pathway
        new_revenue = base_data["monthly_revenue"] * (1 + request.pricing_change / 100)
        new_expenses = base_data["monthly_expenses"] * (1 + request.spending_change / 100) + (request.hiring_count * 8000) + request.marketing_budget
        new_runway = base_data["cash_balance"] / new_expenses if new_expenses > 0 else float('inf')
        
        # Generate AI-powered executive summary
        try:
            scenario_context = {
                "current_revenue": base_data["monthly_revenue"],
                "current_expenses": base_data["monthly_expenses"],
                "current_cash": base_data["cash_balance"],
                "current_runway": base_data["runway_months"],
                "spending_change": request.spending_change,
                "pricing_change": request.pricing_change,
                "new_hires": request.hiring_count,
                "marketing_budget": request.marketing_budget,
                "projected_revenue": new_revenue,
                "projected_expenses": new_expenses,
                "projected_runway": new_runway
            }
            
            ai_summary = llm_rag_agent.generate_response(f"""
            Generate a comprehensive executive summary for this financial scenario analysis. 
            Make it narrative, professional, and actionable. Include:
            
            1. Current financial position overview
            2. Impact of proposed changes
            3. Key risks and opportunities
            4. Strategic recommendations
            
            Scenario Data:
            - Current Monthly Revenue: ₹{scenario_context['current_revenue']:,.0f}
            - Current Monthly Expenses: ₹{scenario_context['current_expenses']:,.0f}
            - Current Cash Balance: ₹{scenario_context['current_cash']:,.0f}
            - Current Runway: {scenario_context['current_runway']:.1f} months
            - Spending Change: {scenario_context['spending_change']}%
            - Pricing Change: {scenario_context['pricing_change']}%
            - New Hires: {scenario_context['new_hires']}
            - Marketing Budget: ₹{scenario_context['marketing_budget']:,.0f}
            - Projected Revenue: ₹{scenario_context['projected_revenue']:,.0f}
            - Projected Expenses: ₹{scenario_context['projected_expenses']:,.0f}
            - Projected Runway: {scenario_context['projected_runway']:.1f} months
            
            Write this as a CFO would present to the board - clear, concise, and strategic.
            """, max_tokens=512, temperature=0.7)
            
            executive_summary = ai_summary
            
        except Exception as e:
            print(f"AI summary generation failed: {str(e)}")
            executive_summary = f"Financial scenario analysis: With {request.spending_change}% spending change, {request.pricing_change}% pricing change, {request.hiring_count} new hires, and ₹{request.marketing_budget:,.0f} marketing budget. Projected runway: {new_runway:.1f} months."
        
        usage_counter += 1
        
        return {
            "summary": executive_summary,
            "original_context": base_data,
            "updated_context": {
                "monthly_revenue": new_revenue,
                "monthly_expenses": new_expenses,
                "runway_months": new_runway
            },
            "impact_analysis": {
                "revenue_change": new_revenue - base_data["monthly_revenue"],
                "expense_change": new_expenses - base_data["monthly_expenses"],
                "marketing_impact": request.marketing_budget * 0.1,
                "runway_impact": new_runway - base_data["runway_months"],
                "profit_impact": (new_revenue - new_expenses) - (base_data["monthly_revenue"] - base_data["monthly_expenses"])
            },
            "processed_at": datetime.now().isoformat(),
            "pathway_powered": False
        }
    
    try:
        # Get base financial data (mock for now)
        base_data = {
            "monthly_revenue": 50000,
            "monthly_expenses": 35000,
            "cash_balance": 200000,
            "runway_months": 13
        }
        
        # Convert request to scenario parameters
        scenario_params = {
            "spending_change": request.spending_change,
            "pricing_change": request.pricing_change,
            "hiring_count": request.hiring_count,
            "marketing_budget": request.marketing_budget
        }
        
        # Use Pathway processor for analysis with AI enhancement
        result = pathway_processor.analyze_scenario(base_data, scenario_params)
        
        # Enhance with AI analysis using GROQ
        try:
            ai_scenario_data = {
                "monthly_revenue": base_data["monthly_revenue"],
                "monthly_expenses": base_data["monthly_expenses"], 
                "cash_balance": base_data["cash_balance"],
                "spending_change": scenario_params["spending_change"],
                "pricing_change": scenario_params["pricing_change"],
                "hiring_count": scenario_params["hiring_count"],
                "marketing_budget": scenario_params["marketing_budget"],
                "projected_runway": result.get("updated_context", {}).get("runway_months", 0),
                "revenue_impact": result.get("impact_analysis", {}).get("revenue_change", 0),
                "expense_impact": result.get("impact_analysis", {}).get("expense_change", 0)
            }
            
            ai_analysis = llm_rag_agent.analyze_financial_scenario(ai_scenario_data)
            
            # Merge AI insights with Pathway results
            result["ai_analysis"] = ai_analysis["analysis"]
            result["ai_recommendations"] = ai_analysis["recommendations"]
            result["key_metrics"] = ai_analysis.get("key_metrics", {})
            result["ai_powered"] = True
            
        except Exception as e:
            print(f"AI analysis failed, using fallback: {str(e)}")
            result["ai_analysis"] = "AI analysis temporarily unavailable. Using standard financial calculations."
            result["ai_recommendations"] = [
                "Monitor cash flow closely with current scenario parameters",
                "Consider adjusting spending levels based on runway projections", 
                "Review hiring plans against revenue growth targets"
            ]
            result["ai_powered"] = False
        
        usage_counter += 1
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scenario analysis failed: {str(e)}")

@app.get("/api/pathway/realtime/{company_id}")
async def get_realtime_insights(company_id: str):
    """Get real-time financial insights using Pathway's live data framework"""
    if not PATHWAY_AVAILABLE:
        # Fallback real-time insights
        return {
            "company_id": company_id,
            "timestamp": datetime.now().isoformat(),
            "financial_snapshot": {
                "monthly_revenue": 50000,
                "monthly_expenses": 35000,
                "cash_balance": 200000,
                "runway_months": 13,
                "last_updated": datetime.now().isoformat()
            },
            "market_conditions": {
                "sentiment": "neutral",
                "volatility": 1.0,
                "last_updated": datetime.now().isoformat()
            },
            "health_score": 75,
            "recommendations": [
                "Real-time insights will be available once Pathway installation completes",
                "Current fallback mode provides basic analysis",
                "Enhanced AI-powered recommendations coming soon"
            ],
            "alerts": [],
            "pathway_powered": False
        }
    
    try:
        insights = await realtime_processor.get_latest_insights(company_id)
        return insights
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Real-time insights failed: {str(e)}")

@app.get("/api/pathway/health")
async def pathway_health_check():
    """Health check for Pathway integration"""
    return {
        "status": "healthy" if PATHWAY_AVAILABLE else "installing",
        "pathway_available": PATHWAY_AVAILABLE,
        "pathway_version": "latest" if PATHWAY_AVAILABLE else "installing",
        "features": ["document_processing", "scenario_analysis", "real_time_insights"] if PATHWAY_AVAILABLE else ["fallback_mode"],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save scenarios to file on shutdown
    import atexit
    def save_scenarios():
        with open("data/scenarios.json", "w") as f:
            json.dump({"scenarios": scenarios_db, "usage": usage_counter}, f)
    atexit.register(save_scenarios)
    
    # Load previous scenarios if they exist
    try:
        if os.path.exists("data/scenarios.json"):
            with open("data/scenarios.json", "r") as f:
                data = json.load(f)
                scenarios_db = data.get("scenarios", [])
                usage_counter = data.get("usage", 0)
    except Exception as e:
        print(f"Warning: Could not load previous scenarios: {e}")
    
    # Start the server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
