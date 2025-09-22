import unittest
import os
from dotenv import load_dotenv
from app.services.llm_rag_agent import OpenLLMRAGAgent

class TestGROQIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the RAG agent with GROQ API"""
        load_dotenv()
        cls.api_key = os.getenv("GROQ_API_KEY")
        if not cls.api_key:
            raise unittest.SkipTest("GROQ_API_KEY not found in environment variables")
            
        cls.rag_agent = OpenLLMRAGAgent(model_name="mixtral-8x7b-32768")
        
    def test_generate_response(self):
        """Test generating a response using GROQ API"""
        query = "What are the key financial metrics for a SaaS business?"
        response = self.rag_agent.generate_response(query, max_tokens=300)
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 50)  # Should be a meaningful response
        print("\nGROQ API Response:")
        print("-" * 50)
        print(response)
        print("-" * 50)
    
    def test_analyze_financial_scenario(self):
        """Test financial scenario analysis"""
        scenario = {
            "company_name": "TestTech Inc.",
            "revenue": 1000000.0,
            "expenses": 800000.0,
            "cash_balance": 500000.0,
            "monthly_burn_rate": 100000.0,
            "growth_rate": 0.15,
            "industry": "SaaS"
        }
        
        result = self.rag_agent.analyze_financial_scenario(scenario)
        
        self.assertIn("analysis", result)
        self.assertIn("recommendations", result)
        self.assertIn("key_metrics", result)
        
        print("\nFinancial Scenario Analysis:")
        print("=" * 50)
        print(f"Analysis: {result['analysis'][:200]}...")
        print(f"\nRecommendations: {result['recommendations'][:200]}...")
        print(f"\nKey Metrics: {result['key_metrics']}")
        print("=" * 50)

if __name__ == "__main__":
    unittest.main()
