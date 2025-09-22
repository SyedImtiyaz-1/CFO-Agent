import unittest
from datetime import datetime
from app.services.rag_agent import RAGAgent, FinancialContext, UserScenario
import time

class TestRAGAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the RAG agent once for all tests"""
        cls.rag_agent = RAGAgent(llm_model="gpt2")  # Using a small model for testing
        
        # Add some test data
        cls.test_company_id = "test_company_123"
        
        # Create a test financial context
        cls.test_context = FinancialContext(
            id="test_ctx_1",
            company_id=cls.test_company_id,
            current_cash=1000000.0,
            monthly_revenue=500000.0,
            monthly_expenses=300000.0,
            marketing_spend=50000.0,
            team_size=10,
            average_salary=50000.0,
            price_per_unit=100.0,
            units_sold=5000,
            runway_months=5.0
        )
        
        # Add the context to the agent
        cls.rag_agent.add_financial_context(cls.test_context)
    
    def test_add_financial_context(self):
        """Test adding a financial context"""
        context = self.rag_agent.get_financial_context(self.test_company_id)
        self.assertIsNotNone(context)
        self.assertEqual(context.company_id, self.test_company_id)
    
    def test_create_scenario(self):
        """Test creating a financial scenario"""
        scenario_changes = {
            "monthly_revenue": 100000.0,  # Increase revenue by 100k
            "monthly_expenses": 50000.0,   # Increase expenses by 50k
            "team_size": 2                 # Add 2 employees
        }
        
        scenario_id = self.rag_agent.create_scenario(
            company_id=self.test_company_id,
            changes=scenario_changes
        )
        
        self.assertIsNotNone(scenario_id)
        self.assertIn(scenario_id, self.rag_agent.scenario_store)
        
        return scenario_id
    
    def test_analyze_scenario(self):
        """Test analyzing a financial scenario"""
        # First create a scenario
        scenario_changes = {
            "monthly_revenue": 100000.0,  # Increase revenue by 100k
            "monthly_expenses": 50000.0,   # Increase expenses by 50k
            "team_size": 2                 # Add 2 employees
        }
        
        scenario_id = self.rag_agent.create_scenario(
            company_id=self.test_company_id,
            changes=scenario_changes
        )
        
        # Now analyze it
        analysis = self.rag_agent.analyze_scenario(scenario_id)
        
        # Check the analysis structure
        self.assertIsNotNone(analysis)
        self.assertIn("analysis_id", analysis.dict())
        self.assertIn("summary", analysis.dict())
        self.assertIn("impact_analysis", analysis.dict())
        
        # Check that the summary contains key sections
        summary = analysis.summary.lower()
        self.assertTrue(any(section in summary for section in ["financial impact analysis", "key observations", "recommendations"]))
        
        return analysis
    
    def test_llm_integration(self):
        """Test that the LLM is properly integrated"""
        # This is a simple test to verify the LLM is responding
        # Note: This test might be slow as it loads the LLM
        
        # Create a simple scenario
        scenario_changes = {
            "monthly_revenue": 50000.0,  # Small change to test LLM
            "monthly_expenses": 20000.0
        }
        
        scenario_id = self.rag_agent.create_scenario(
            company_id=self.test_company_id,
            changes=scenario_changes
        )
        
        # Get the analysis
        analysis = self.rag_agent.analyze_scenario(scenario_id)
        
        # Check that we got a reasonable response from the LLM
        self.assertGreater(len(analysis.summary), 100)  # Should be a detailed response
        self.assertIn("financial", analysis.summary.lower())  # Should mention finance

if __name__ == "__main__":
    unittest.main()
