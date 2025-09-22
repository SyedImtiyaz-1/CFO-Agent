"""
Pathway integration for CFO Helper Agent
Handles real-time financial data processing and document analysis
"""

import pathway as pw
import pandas as pd
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import tempfile
import base64
from datetime import datetime

# Document processing imports
try:
    from pathway.xpacks.llm import llms, prompts
    from pathway.xpacks.llm.parsers import ParseUnstructured
    from pathway.xpacks.llm.vector_store import VectorStoreServer
except ImportError:
    print("LLM extensions not available. Install with: pip install 'pathway[xpack-llm,xpack-llm-docs]'")

class PathwayFinancialProcessor:
    """
    Main class for processing financial documents and data using Pathway
    """
    
    def __init__(self, data_dir: str = "/tmp/cfo_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize LLM for financial analysis
        self.llm = llms.OpenAIChat(
            model="gpt-3.5-turbo",
            retry_strategy=llms.ExponentialBackoffRetryStrategy(max_retries=3),
            cache_strategy=llms.DiskCache(),
        )
        
        # Financial analysis prompt
        self.financial_prompt = """
        You are a CFO assistant analyzing financial data. Based on the provided financial information:
        
        1. Extract key financial metrics (revenue, expenses, cash flow, runway)
        2. Identify trends and patterns
        3. Provide insights on financial health
        4. Suggest areas for improvement
        
        Financial Data: {financial_data}
        
        Provide a structured analysis in JSON format with the following keys:
        - monthly_revenue: number
        - monthly_expenses: number  
        - cash_balance: number
        - runway_months: number
        - key_insights: list of strings
        - recommendations: list of strings
        """
        
    def setup_document_pipeline(self) -> pw.Table:
        """
        Set up Pathway pipeline for document processing
        """
        # Monitor the data directory for new files
        documents = pw.io.fs.read(
            self.data_dir,
            format="binary",
            mode="streaming",
            with_metadata=True
        )
        
        # Parse documents using unstructured
        parser = ParseUnstructured(
            mode="single",
            post_processors=[
                # Clean and structure the parsed content
                lambda x: self._clean_financial_text(x)
            ]
        )
        
        parsed_docs = documents.select(
            content=parser(pw.this.data),
            metadata=pw.this._metadata
        )
        
        return parsed_docs
    
    def _clean_financial_text(self, text: str) -> str:
        """Clean and structure financial text data"""
        # Remove extra whitespace and normalize
        cleaned = " ".join(text.split())
        
        # Extract financial keywords and numbers
        financial_keywords = [
            "revenue", "income", "expenses", "profit", "loss", "cash", "flow",
            "balance", "assets", "liabilities", "equity", "budget", "forecast"
        ]
        
        # This is a simplified cleaning - in production, you'd want more sophisticated NLP
        return cleaned
    
    def process_uploaded_file(self, file_data: str, filename: str, file_type: str) -> Dict[str, Any]:
        """
        Process an uploaded file and extract financial data
        """
        try:
            # Decode base64 file data
            file_content = base64.b64decode(file_data.split(',')[1] if ',' in file_data else file_data)
            
            # Save to temporary file
            temp_file = self.data_dir / f"{datetime.now().timestamp()}_{filename}"
            with open(temp_file, 'wb') as f:
                f.write(file_content)
            
            # Process based on file type
            if file_type == 'application/pdf':
                return self._process_pdf(temp_file)
            elif 'excel' in file_type or 'spreadsheet' in file_type:
                return self._process_excel(temp_file)
            elif file_type == 'text/csv':
                return self._process_csv(temp_file)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            return {"error": f"Failed to process file: {str(e)}"}
        finally:
            # Clean up temporary file
            if temp_file.exists():
                temp_file.unlink()
    
    def _process_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Process PDF financial documents"""
        try:
            # Use Pathway's document parser
            parser = ParseUnstructured()
            
            with open(file_path, 'rb') as f:
                content = parser(f.read())
            
            # Extract financial data using LLM
            financial_data = self._extract_financial_metrics(content)
            
            return {
                "type": "pdf",
                "content": content[:1000],  # First 1000 chars for preview
                "financial_data": financial_data,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"PDF processing failed: {str(e)}"}
    
    def _process_excel(self, file_path: Path) -> Dict[str, Any]:
        """Process Excel financial spreadsheets"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=None)  # Read all sheets
            
            financial_data = {}
            
            for sheet_name, sheet_df in df.items():
                # Look for financial columns
                financial_cols = []
                for col in sheet_df.columns:
                    col_lower = str(col).lower()
                    if any(keyword in col_lower for keyword in ['revenue', 'income', 'expense', 'cost', 'profit', 'cash', 'balance']):
                        financial_cols.append(col)
                
                if financial_cols:
                    # Extract numerical data from financial columns
                    sheet_data = {}
                    for col in financial_cols:
                        numeric_data = pd.to_numeric(sheet_df[col], errors='coerce').dropna()
                        if not numeric_data.empty:
                            sheet_data[col] = {
                                "values": numeric_data.tolist(),
                                "sum": float(numeric_data.sum()),
                                "mean": float(numeric_data.mean()),
                                "latest": float(numeric_data.iloc[-1])
                            }
                    
                    financial_data[sheet_name] = sheet_data
            
            # Generate summary
            summary = self._generate_excel_summary(financial_data)
            
            return {
                "type": "excel",
                "sheets": list(df.keys()),
                "financial_data": financial_data,
                "summary": summary,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Excel processing failed: {str(e)}"}
    
    def _process_csv(self, file_path: Path) -> Dict[str, Any]:
        """Process CSV financial data"""
        try:
            df = pd.read_csv(file_path)
            
            # Identify financial columns
            financial_data = {}
            for col in df.columns:
                col_lower = str(col).lower()
                if any(keyword in col_lower for keyword in ['revenue', 'income', 'expense', 'cost', 'profit', 'cash', 'balance']):
                    numeric_data = pd.to_numeric(df[col], errors='coerce').dropna()
                    if not numeric_data.empty:
                        financial_data[col] = {
                            "values": numeric_data.tolist(),
                            "sum": float(numeric_data.sum()),
                            "mean": float(numeric_data.mean()),
                            "latest": float(numeric_data.iloc[-1])
                        }
            
            return {
                "type": "csv",
                "rows": len(df),
                "columns": list(df.columns),
                "financial_data": financial_data,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"CSV processing failed: {str(e)}"}
    
    def _extract_financial_metrics(self, content: str) -> Dict[str, Any]:
        """Extract financial metrics from text using LLM"""
        try:
            # Use LLM to extract structured financial data
            prompt = self.financial_prompt.format(financial_data=content[:2000])
            
            response = self.llm(prompt)
            
            # Try to parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback to basic extraction
                return {
                    "monthly_revenue": 0,
                    "monthly_expenses": 0,
                    "cash_balance": 0,
                    "runway_months": 0,
                    "key_insights": ["Unable to parse structured data from document"],
                    "recommendations": ["Please provide clearer financial data format"]
                }
                
        except Exception as e:
            return {"error": f"Financial extraction failed: {str(e)}"}
    
    def _generate_excel_summary(self, financial_data: Dict) -> Dict[str, Any]:
        """Generate summary from Excel financial data"""
        summary = {
            "total_revenue": 0,
            "total_expenses": 0,
            "net_profit": 0,
            "key_metrics": []
        }
        
        for sheet_name, sheet_data in financial_data.items():
            for col_name, col_data in sheet_data.items():
                col_lower = col_name.lower()
                if 'revenue' in col_lower or 'income' in col_lower:
                    summary["total_revenue"] += col_data.get("sum", 0)
                elif 'expense' in col_lower or 'cost' in col_lower:
                    summary["total_expenses"] += col_data.get("sum", 0)
        
        summary["net_profit"] = summary["total_revenue"] - summary["total_expenses"]
        
        # Calculate runway (simplified)
        if summary["total_expenses"] > 0:
            # Assume we have cash balance info somewhere
            estimated_cash = summary["total_revenue"] * 2  # Rough estimate
            summary["estimated_runway_months"] = estimated_cash / (summary["total_expenses"] / 12)
        
        return summary
    
    def analyze_scenario(self, base_data: Dict, scenario_params: Dict) -> Dict[str, Any]:
        """
        Analyze financial scenario using Pathway's real-time processing
        """
        try:
            # Extract base financial metrics
            base_revenue = base_data.get("monthly_revenue", 0)
            base_expenses = base_data.get("monthly_expenses", 0)
            base_cash = base_data.get("cash_balance", 100000)  # Default assumption
            
            # Apply scenario changes
            revenue_change = scenario_params.get("pricing_change", 0) / 100
            expense_change = scenario_params.get("spending_change", 0) / 100
            hiring_cost = scenario_params.get("hiring_count", 0) * 8000  # 8k per hire per month
            marketing_spend = scenario_params.get("marketing_budget", 0)
            
            # Calculate new metrics
            new_revenue = base_revenue * (1 + revenue_change)
            new_expenses = base_expenses * (1 + expense_change) + hiring_cost + marketing_spend
            
            # Marketing ROI assumption (10% of marketing spend becomes revenue)
            marketing_roi = marketing_spend * 0.1
            new_revenue += marketing_roi
            
            net_change = (new_revenue - new_expenses) - (base_revenue - base_expenses)
            
            # Calculate runway
            current_runway = base_cash / base_expenses if base_expenses > 0 else float('inf')
            projected_runway = base_cash / new_expenses if new_expenses > 0 else float('inf')
            
            # Generate insights using LLM
            scenario_prompt = f"""
            Analyze this financial scenario change:
            
            Base Monthly Revenue: ${base_revenue:,.2f}
            New Monthly Revenue: ${new_revenue:,.2f}
            Base Monthly Expenses: ${base_expenses:,.2f}
            New Monthly Expenses: ${new_expenses:,.2f}
            Net Monthly Change: ${net_change:,.2f}
            Current Runway: {current_runway:.1f} months
            Projected Runway: {projected_runway:.1f} months
            
            Scenario Parameters:
            - Pricing Change: {scenario_params.get('pricing_change', 0)}%
            - Spending Change: {scenario_params.get('spending_change', 0)}%
            - New Hires: {scenario_params.get('hiring_count', 0)}
            - Marketing Budget: ${scenario_params.get('marketing_budget', 0):,.2f}
            
            Provide a brief analysis and 3 key recommendations.
            """
            
            analysis = self.llm(scenario_prompt)
            
            return {
                "summary": analysis,
                "original_context": {
                    "monthly_revenue": base_revenue,
                    "monthly_expenses": base_expenses,
                    "runway_months": current_runway
                },
                "updated_context": {
                    "monthly_revenue": new_revenue,
                    "monthly_expenses": new_expenses,
                    "runway_months": projected_runway
                },
                "impact_analysis": {
                    "revenue_change": new_revenue - base_revenue,
                    "expense_change": new_expenses - base_expenses,
                    "marketing_impact": marketing_roi,
                    "runway_impact": projected_runway - current_runway,
                    "profit_impact": net_change
                },
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Scenario analysis failed: {str(e)}"}

# Global processor instance
pathway_processor = PathwayFinancialProcessor()
