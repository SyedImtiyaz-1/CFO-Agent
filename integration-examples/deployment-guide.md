# CFO Helper Agent - Integration Guide

## How to Use CFO Helper Agent in Your Webapp

There are multiple ways to integrate the CFO Helper Agent into your existing web application:

## 🚀 Quick Start Options

### 1. **API Integration** (Recommended)
Best for: Custom integrations, existing React/Vue/Angular apps

```javascript
// Install and use the API client
import CFOHelperAPI from './api-integration.js';

const cfoAPI = new CFOHelperAPI('http://localhost:8000');
const result = await cfoAPI.analyzeScenario(scenarioData);
```

### 2. **React Component**
Best for: React applications

```jsx
import CFOHelperWidget from './react-component';

<CFOHelperWidget 
  companyId="your-company" 
  onAnalysisComplete={(result) => console.log(result)} 
/>
```

### 3. **Iframe Embedding**
Best for: Quick integration, any framework

```html
<iframe 
  src="http://localhost:3000/agent" 
  width="100%" 
  height="800px">
</iframe>
```

### 4. **Vanilla JavaScript**
Best for: Non-framework applications

```html
<!-- Include the vanilla-js-integration.html file -->
<script src="cfo-helper-integration.js"></script>
```

## 📋 Integration Steps

### Step 1: Start the Services
```bash
# Backend (Terminal 1)
cd /home/imtiyaz/CFOAgent/cfo-helper/backend
python main.py

# Frontend (Terminal 2) 
cd /home/imtiyaz/CFOAgent/cfo-helper/frontend
npm start
```

### Step 2: Choose Integration Method
Pick one of the 4 methods above based on your tech stack.

### Step 3: Configure API Endpoints
Update the base URL in your integration:
- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

### Step 4: Handle Authentication (Optional)
Add authentication headers if needed:
```javascript
const response = await fetch(url, {
  headers: {
    'Authorization': 'Bearer your-token',
    'Content-Type': 'application/json'
  }
});
```

## 🔧 Available API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/pathway/upload` | POST | Upload financial documents |
| `/api/pathway/context/{company_id}` | GET | Get financial context |
| `/api/pathway/scenario` | POST | Run scenario analysis |
| `/api/pathway/realtime/{company_id}` | GET | Get real-time insights |
| `/api/pathway/health` | GET | Check system health |

## 💡 Usage Examples

### Upload Financial Data
```javascript
const files = document.getElementById('fileInput').files;
const result = await cfoAPI.uploadFinancialData('company-123', files);
```

### Run Scenario Analysis
```javascript
const analysis = await cfoAPI.analyzeScenario({
  company_id: 'company-123',
  spending_change: -10,
  pricing_change: 5,
  hiring_count: 2,
  marketing_budget: 25000
});
```

### Get Real-time Insights
```javascript
const insights = await cfoAPI.getRealTimeInsights('company-123');
```

## 🚀 Deployment Options

### Option 1: Same Server
Deploy both frontend and backend on the same server.

### Option 2: Separate Services
- Backend: Deploy on cloud service (AWS, GCP, Azure)
- Frontend: Deploy on CDN (Netlify, Vercel)

### Option 3: Microservice
Use CFO Helper as a microservice in your existing architecture.

### Option 4: Docker Container
```dockerfile
# Use the provided Docker setup
docker-compose up -d
```

## 🔒 Security Considerations

1. **API Keys**: Store Pathway API keys in environment variables
2. **CORS**: Configure CORS for your domain
3. **Authentication**: Add user authentication if needed
4. **Rate Limiting**: Implement rate limiting for API calls
5. **File Validation**: Validate uploaded files on server side

## 📊 Monitoring & Analytics

Track usage with built-in counters:
- Files uploaded
- Scenarios analyzed  
- Reports exported
- API calls made

## 🛠️ Customization

### Custom Styling
Override CSS classes:
```css
.cfo-helper-widget {
  /* Your custom styles */
}
```

### Custom Logic
Extend the API client:
```javascript
class CustomCFOAPI extends CFOHelperAPI {
  async customAnalysis(data) {
    // Your custom logic
  }
}
```

## 📞 Support

For integration support:
1. Check the example files in `/integration-examples/`
2. Review API documentation at `/docs` endpoint
3. Test with the health check endpoint
4. Use browser dev tools to debug API calls

## 🎯 Next Steps

1. Choose your integration method
2. Copy the relevant example file
3. Update configuration (URLs, company ID)
4. Test with sample data
5. Deploy to production

The CFO Helper Agent is designed to be flexible and easy to integrate into any web application architecture.
