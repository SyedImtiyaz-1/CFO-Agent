# CFO Helper Agent - Test Data Files

This directory contains sample financial data files for testing the CFO Helper Agent. All files contain realistic financial data that you can upload to test the Pathway integration.

## 📊 Available Test Files

### Excel Files (.xlsx)
1. **`monthly-financials.xlsx`** - 12 months of revenue, expenses, cash flow
2. **`quarterly-pl.xlsx`** - Quarterly P&L statement with EBITDA
3. **`cash-flow.xlsx`** - 6 months of detailed cash flow analysis
4. **`balance-sheet.xlsx`** - Current vs previous month balance sheet
5. **`startup-model.xlsx`** - 18-month startup financial model with runway
6. **`revenue-breakdown.xlsx`** - Product-wise revenue breakdown

### CSV Files (.csv)
1. **`sample-financial-data.csv`** - Monthly financial overview
2. **`expenses-breakdown.csv`** - Category-wise expense tracking

## 🚀 How to Test

### Method 1: Web Interface
1. Start the CFO Helper Agent:
   ```bash
   # Backend
   cd /home/imtiyaz/CFOAgent/cfo-helper/backend
   python main.py
   
   # Frontend  
   cd /home/imtiyaz/CFOAgent/cfo-helper/frontend
   npm start
   ```

2. Go to `http://localhost:3000/agent`
3. Upload any of the test files
4. Run scenario analysis with different parameters

### Method 2: API Testing
```bash
# Test file upload
curl -X POST "http://localhost:8000/api/pathway/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "test-company",
    "files": [...]
  }'

# Test scenario analysis
curl -X POST "http://localhost:8000/api/pathway/scenario" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "test-company",
    "spending_change": -10,
    "pricing_change": 5,
    "hiring_count": 2,
    "marketing_budget": 25000
  }'
```

## 📋 File Contents Overview

| File | Contains | Use Case |
|------|----------|----------|
| `monthly-financials.xlsx` | Revenue, expenses, cash flow | General financial analysis |
| `quarterly-pl.xlsx` | P&L statement | Profitability analysis |
| `cash-flow.xlsx` | Operating, investing, financing CF | Cash management |
| `balance-sheet.xlsx` | Assets, liabilities, equity | Financial position |
| `startup-model.xlsx` | Growth model with runway | Startup planning |
| `revenue-breakdown.xlsx` | Product revenue analysis | Revenue optimization |
| `expenses-breakdown.csv` | Category expenses | Cost management |

## 🎯 Testing Scenarios

Try these scenario combinations:

### Conservative Growth
- Spending Change: -5%
- Pricing Change: +2%
- New Hires: 1
- Marketing Budget: ₹15,000

### Aggressive Expansion  
- Spending Change: +15%
- Pricing Change: +10%
- New Hires: 5
- Marketing Budget: ₹50,000

### Cost Cutting
- Spending Change: -20%
- Pricing Change: 0%
- New Hires: 0
- Marketing Budget: ₹10,000

## 📊 Expected Results

The Pathway AI will analyze these files and provide:
- Financial metric extraction
- Scenario impact analysis
- Cash runway calculations
- AI-powered recommendations
- Real-time insights

All test files are production-ready and contain realistic financial data patterns that businesses typically encounter.
