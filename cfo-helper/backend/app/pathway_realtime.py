"""
Real-time data processing with Pathway for CFO Helper Agent
Implements live data streams and real-time financial monitoring
"""

import pathway as pw
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random

class PathwayRealtimeProcessor:
    """
    Real-time financial data processor using Pathway's live data framework
    """
    
    def __init__(self):
        self.is_running = False
        self.financial_stream = None
        self.market_stream = None
        self.subscribers = []
        
    def setup_financial_data_stream(self):
        """
        Set up a live financial data stream using Pathway
        """
        # Create a mock financial data stream
        # In production, this would connect to real financial data sources
        
        class FinancialDataSource(pw.io.python.ConnectorSubject):
            def run(self):
                while True:
                    # Generate mock real-time financial data
                    current_time = datetime.now()
                    
                    # Simulate market conditions affecting financial metrics
                    market_volatility = random.uniform(0.95, 1.05)
                    
                    financial_update = {
                        "timestamp": current_time.isoformat(),
                        "company_id": "default_company",
                        "monthly_revenue": 50000 * market_volatility,
                        "monthly_expenses": 35000 * random.uniform(0.98, 1.02),
                        "cash_balance": 200000 + random.uniform(-10000, 10000),
                        "market_conditions": {
                            "volatility": market_volatility,
                            "trend": "up" if market_volatility > 1.0 else "down",
                            "confidence": random.uniform(0.7, 0.95)
                        },
                        "key_metrics": {
                            "burn_rate": 35000 * random.uniform(0.98, 1.02),
                            "growth_rate": (market_volatility - 1) * 100,
                            "runway_months": 200000 / (35000 * random.uniform(0.98, 1.02))
                        }
                    }
                    
                    self.next(financial_update)
                    
                    # Update every 30 seconds
                    asyncio.sleep(30)
        
        # Create the financial data stream
        financial_source = FinancialDataSource()
        self.financial_stream = pw.io.python.read(
            financial_source,
            schema=pw.schema_from_dict({
                "timestamp": str,
                "company_id": str,
                "data": str  # JSON string of financial data
            })
        )
        
        return self.financial_stream
    
    def setup_market_data_stream(self):
        """
        Set up a live market data stream for external factors
        """
        class MarketDataSource(pw.io.python.ConnectorSubject):
            def run(self):
                while True:
                    current_time = datetime.now()
                    
                    # Simulate market indicators
                    market_data = {
                        "timestamp": current_time.isoformat(),
                        "indicators": {
                            "interest_rates": random.uniform(3.0, 7.0),
                            "inflation_rate": random.uniform(2.0, 5.0),
                            "market_sentiment": random.choice(["bullish", "bearish", "neutral"]),
                            "sector_performance": random.uniform(-5.0, 10.0)
                        },
                        "recommendations": self._generate_market_recommendations()
                    }
                    
                    self.next(market_data)
                    asyncio.sleep(60)  # Update every minute
        
        market_source = MarketDataSource()
        self.market_stream = pw.io.python.read(
            market_source,
            schema=pw.schema_from_dict({
                "timestamp": str,
                "data": str  # JSON string of market data
            })
        )
        
        return self.market_stream
    
    def _generate_market_recommendations(self) -> List[str]:
        """Generate market-based recommendations"""
        recommendations = [
            "Monitor interest rate changes for financing decisions",
            "Consider inflation impact on operational costs",
            "Review pricing strategy based on market conditions",
            "Evaluate cash flow timing with market volatility",
            "Assess competitive positioning in current market"
        ]
        
        return random.sample(recommendations, 3)
    
    def create_real_time_dashboard_data(self):
        """
        Create a real-time dashboard using Pathway's streaming capabilities
        """
        if not self.financial_stream:
            self.setup_financial_data_stream()
        
        if not self.market_stream:
            self.setup_market_data_stream()
        
        # Combine financial and market data streams
        combined_stream = self.financial_stream.join(
            self.market_stream,
            pw.left.timestamp == pw.right.timestamp
        ).select(
            timestamp=pw.left.timestamp,
            financial_data=pw.left.data,
            market_data=pw.right.data
        )
        
        # Process combined data for insights
        insights_stream = combined_stream.select(
            timestamp=pw.this.timestamp,
            insights=pw.apply(self._generate_insights, pw.this.financial_data, pw.this.market_data)
        )
        
        return insights_stream
    
    def _generate_insights(self, financial_data: str, market_data: str) -> str:
        """Generate insights from combined financial and market data"""
        try:
            fin_data = json.loads(financial_data)
            mkt_data = json.loads(market_data)
            
            insights = {
                "timestamp": datetime.now().isoformat(),
                "financial_health": self._assess_financial_health(fin_data),
                "market_impact": self._assess_market_impact(mkt_data),
                "recommendations": self._generate_combined_recommendations(fin_data, mkt_data),
                "alerts": self._generate_alerts(fin_data, mkt_data)
            }
            
            return json.dumps(insights)
        except Exception as e:
            return json.dumps({"error": str(e), "timestamp": datetime.now().isoformat()})
    
    def _assess_financial_health(self, financial_data: Dict) -> Dict:
        """Assess financial health from real-time data"""
        runway = financial_data.get("key_metrics", {}).get("runway_months", 0)
        burn_rate = financial_data.get("key_metrics", {}).get("burn_rate", 0)
        growth_rate = financial_data.get("key_metrics", {}).get("growth_rate", 0)
        
        if runway > 18:
            health_status = "excellent"
        elif runway > 12:
            health_status = "good"
        elif runway > 6:
            health_status = "concerning"
        else:
            health_status = "critical"
        
        return {
            "status": health_status,
            "runway_months": runway,
            "burn_rate": burn_rate,
            "growth_rate": growth_rate,
            "score": min(100, max(0, (runway / 18) * 100))
        }
    
    def _assess_market_impact(self, market_data: Dict) -> Dict:
        """Assess market impact on financial projections"""
        indicators = market_data.get("indicators", {})
        sentiment = indicators.get("market_sentiment", "neutral")
        
        impact_score = 0
        if sentiment == "bullish":
            impact_score = 75
        elif sentiment == "bearish":
            impact_score = 25
        else:
            impact_score = 50
        
        return {
            "sentiment": sentiment,
            "impact_score": impact_score,
            "interest_rates": indicators.get("interest_rates", 0),
            "inflation_rate": indicators.get("inflation_rate", 0)
        }
    
    def _generate_combined_recommendations(self, financial_data: Dict, market_data: Dict) -> List[str]:
        """Generate recommendations based on combined data"""
        recommendations = []
        
        runway = financial_data.get("key_metrics", {}).get("runway_months", 0)
        sentiment = market_data.get("indicators", {}).get("market_sentiment", "neutral")
        
        if runway < 12 and sentiment == "bearish":
            recommendations.append("Consider aggressive cost reduction due to low runway and poor market conditions")
        elif runway > 18 and sentiment == "bullish":
            recommendations.append("Good time to consider strategic investments or expansion")
        
        if financial_data.get("key_metrics", {}).get("growth_rate", 0) < 0:
            recommendations.append("Focus on revenue recovery strategies")
        
        recommendations.extend([
            "Monitor real-time metrics for early warning signs",
            "Adjust forecasts based on live market data",
            "Consider scenario planning for different market conditions"
        ])
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _generate_alerts(self, financial_data: Dict, market_data: Dict) -> List[Dict]:
        """Generate real-time alerts"""
        alerts = []
        
        runway = financial_data.get("key_metrics", {}).get("runway_months", 0)
        if runway < 6:
            alerts.append({
                "level": "critical",
                "message": f"Critical: Only {runway:.1f} months of runway remaining",
                "action": "Immediate action required"
            })
        elif runway < 12:
            alerts.append({
                "level": "warning",
                "message": f"Warning: {runway:.1f} months of runway remaining",
                "action": "Consider cost optimization"
            })
        
        growth_rate = financial_data.get("key_metrics", {}).get("growth_rate", 0)
        if growth_rate < -10:
            alerts.append({
                "level": "warning",
                "message": f"Revenue declining by {abs(growth_rate):.1f}%",
                "action": "Review revenue strategies"
            })
        
        return alerts
    
    async def get_latest_insights(self, company_id: str = "default_company") -> Dict[str, Any]:
        """Get the latest real-time insights for a company"""
        # Simulate real-time data retrieval
        current_time = datetime.now()
        
        # Generate current financial snapshot
        market_volatility = random.uniform(0.95, 1.05)
        
        financial_data = {
            "monthly_revenue": 50000 * market_volatility,
            "monthly_expenses": 35000 * random.uniform(0.98, 1.02),
            "cash_balance": 200000 + random.uniform(-10000, 10000),
            "runway_months": 200000 / (35000 * random.uniform(0.98, 1.02)),
            "last_updated": current_time.isoformat()
        }
        
        market_data = {
            "sentiment": random.choice(["bullish", "bearish", "neutral"]),
            "volatility": market_volatility,
            "interest_rates": random.uniform(3.0, 7.0),
            "last_updated": current_time.isoformat()
        }
        
        insights = {
            "company_id": company_id,
            "timestamp": current_time.isoformat(),
            "financial_snapshot": financial_data,
            "market_conditions": market_data,
            "health_score": min(100, max(0, (financial_data["runway_months"] / 18) * 100)),
            "recommendations": self._generate_combined_recommendations(
                {"key_metrics": financial_data}, 
                {"indicators": market_data}
            ),
            "alerts": self._generate_alerts(
                {"key_metrics": financial_data}, 
                {"indicators": market_data}
            ),
            "pathway_powered": True
        }
        
        return insights

# Global real-time processor instance
realtime_processor = PathwayRealtimeProcessor()
