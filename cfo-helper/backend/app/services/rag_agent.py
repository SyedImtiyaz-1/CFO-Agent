from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
import json
from pathlib import Path

# Import the OpenLLM RAG agent
from .llm_rag_agent import OpenLLMRAGAgent, VectorStore

class FinancialContext(BaseModel):
    """Schema for storing financial context data"""
    id: str
    company_id: str
    current_cash: float
    monthly_revenue: float
    monthly_expenses: float
    marketing_spend: float
    team_size: int
    average_salary: float
    price_per_unit: float
    units_sold: int
    runway_months: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}

class UserScenario(BaseModel):
    """Schema for user scenario inputs"""
    scenario_id: str
    company_id: str
    changes: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class FinancialAnalysis(BaseModel):
    """Schema for financial analysis results"""
    analysis_id: str
    scenario_id: str
    company_id: str
    original_context: FinancialContext
    updated_context: FinancialContext
    impact_analysis: Dict[str, Any]
    summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RAGAgent:
    def __init__(self, llm_model: str = "gpt2"):
        self.context_store = {}
        self.scenario_store = {}
        self.analysis_store = {}
        self.llm_rag_agent = OpenLLMRAGAgent(model_name=llm_model)
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base with financial domain knowledge"""
        financial_knowledge = [
            {"text": "A company's runway is calculated as cash balance divided by monthly burn rate."},
            {"text": "Increasing marketing spend typically leads to higher customer acquisition but reduces short-term profitability."},
            {"text": "Hiring more employees increases fixed costs but can drive revenue growth if managed properly."},
            {"text": "Reducing expenses improves short-term cash flow but may impact long-term growth if critical areas are cut."},
            {"text": "Pricing strategy significantly impacts both revenue and customer acquisition costs."}
        ]
        self.llm_rag_agent.add_documents(financial_knowledge)
    
    def add_financial_context(self, context: FinancialContext) -> str:
        """Add or update financial context for a company"""
        self.context_store[context.company_id] = context
        return context.id
    
    def get_financial_context(self, company_id: str) -> Optional[FinancialContext]:
        """Retrieve financial context for a company"""
        return self.context_store.get(company_id)
    
    def create_scenario(self, company_id: str, changes: Dict[str, Any]) -> str:
        """Create a new scenario for analysis"""
        scenario_id = f"scenario_{len(self.scenario_store) + 1}"
        scenario = UserScenario(
            scenario_id=scenario_id,
            company_id=company_id,
            changes=changes
        )
        self.scenario_store[scenario_id] = scenario
        return scenario_id
    
    def analyze_scenario(self, scenario_id: str) -> FinancialAnalysis:
        """Analyze the financial impact of a scenario"""
        scenario = self.scenario_store.get(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        context = self.get_financial_context(scenario.company_id)
        if not context:
            raise ValueError(f"No financial context found for company {scenario.company_id}")
        
        # Create updated context based on scenario changes
        updated_data = context.dict()
        for key, value in scenario.changes.items():
            if key in updated_data:
                if isinstance(updated_data[key], (int, float)):
                    updated_data[key] += value
                else:
                    updated_data[key] = value
        
        updated_context = FinancialContext(**updated_data)
        
        # Calculate impact analysis
        impact = self._calculate_impact(context, updated_context)
        
        # Generate summary
        summary = self._generate_summary(context, updated_context, impact)
        
        # Create analysis record
        analysis_id = f"analysis_{len(self.analysis_store) + 1}"
        analysis = FinancialAnalysis(
            analysis_id=analysis_id,
            scenario_id=scenario_id,
            company_id=scenario.company_id,
            original_context=context,
            updated_context=updated_context,
            impact_analysis=impact,
            summary=summary
        )
        
        self.analysis_store[analysis_id] = analysis
        return analysis
    
    def _calculate_impact(self, original: FinancialContext, updated: FinancialContext) -> Dict[str, Any]:
        """Calculate the financial impact of changes"""
        impact = {
            "revenue_change": updated.monthly_revenue - original.monthly_revenue,
            "expense_change": updated.monthly_expenses - original.monthly_expenses,
            "marketing_impact": updated.marketing_spend - original.marketing_spend,
            "runway_impact": updated.runway_months - original.runway_months,
            "profit_impact": (updated.monthly_revenue - updated.monthly_expenses) - 
                            (original.monthly_revenue - original.monthly_expenses)
        }
        return impact
    
    def _generate_summary(self, original: FinancialContext, updated: FinancialContext, impact: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the financial impact using LLM"""
        # Prepare the context for the LLM
        context = {
            "current": original.dict(),
            "proposed": updated.dict(),
            "impact": impact
        }
        
        # Generate analysis using the LLM
        prompt = f"""
        Analyze this financial scenario and provide a detailed summary:
        
        Current Financial Status:
        - Monthly Revenue: ₹{original.monthly_revenue:,.2f}
        - Monthly Expenses: ₹{original.monthly_expenses:,.2f}
        - Current Runway: {original.runway_months:.1f} months
        - Marketing Spend: ₹{original.marketing_spend:,.2f}
        - Team Size: {original.team_size} employees
        
        Proposed Changes:
        """
        
        # Add changes
        changes = []
        if updated.monthly_revenue != original.monthly_revenue:
            change = updated.monthly_revenue - original.monthly_revenue
            pct_change = (change / original.monthly_revenue) * 100
            changes.append(f"- Revenue: ₹{change:+,.2f} ({pct_change:+.1f}%)")
            
        if updated.monthly_expenses != original.monthly_expenses:
            change = updated.monthly_expenses - original.monthly_expenses
            pct_change = (change / original.monthly_expenses) * 100 if original.monthly_expenses != 0 else float('inf')
            changes.append(f"- Expenses: ₹{change:+,.2f} ({pct_change:+.1f}%)")
            
        if updated.marketing_spend != original.marketing_spend:
            change = updated.marketing_spend - original.marketing_spend
            pct_change = (change / original.marketing_spend) * 100 if original.marketing_spend != 0 else float('inf')
            changes.append(f"- Marketing Spend: ₹{change:+,.2f} ({pct_change:+.1f}%)")
            
        if updated.team_size != original.team_size:
            change = updated.team_size - original.team_size
            pct_change = (change / original.team_size) * 100 if original.team_size != 0 else float('inf')
            changes.append(f"- Team Size: {change:+,.0f} employees ({pct_change:+,.1f}%)")
        
        prompt += "\n".join(changes) if changes else "No significant changes"
        prompt += f"\n\nImpact Analysis:\n"
        
        # Add impact analysis
        prompt += f"""
        - Revenue Change: ₹{impact['revenue_change']:+,.2f} ({(impact['revenue_change']/original.monthly_revenue*100) if original.monthly_revenue != 0 else 0:+.1f}%)
        - Expense Change: ₹{impact['expense_change']:+,.2f} ({(impact['expense_change']/original.monthly_expenses*100) if original.monthly_expenses != 0 else 0:+.1f}%)
        - New Runway: {updated.runway_months:.1f} months ({impact['runway_impact']:+.1f} months)
        - Monthly Profit Impact: ₹{impact['profit_impact']:+,.2f}
        """
        
        # Get analysis from LLM
        analysis = self.llm_rag_agent.generate_response(
            f"""
            {prompt}
            
            Please provide a detailed financial analysis including:
            1. Key observations about the proposed changes
            2. Impact on financial health
            3. Potential risks and opportunities
            4. Data-driven recommendations
            
            Format the response in markdown with clear sections.
            """
        )
        
        return f"# Financial Impact Analysis\n\n{analysis}"
