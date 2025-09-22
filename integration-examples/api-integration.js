// CFO Helper Agent API Integration Example
// Add this to your existing webapp

class CFOHelperAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  // Upload financial documents
  async uploadFinancialData(companyId, files) {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    const response = await fetch(`${this.baseURL}/api/pathway/upload`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_id: companyId,
        files: await this.convertFilesToBase64(files)
      })
    });
    
    return response.json();
  }

  // Get financial context
  async getFinancialContext(companyId) {
    const response = await fetch(`${this.baseURL}/api/pathway/context/${companyId}`);
    return response.json();
  }

  // Run scenario analysis
  async analyzeScenario(scenarioData) {
    const response = await fetch(`${this.baseURL}/api/pathway/scenario`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(scenarioData)
    });
    
    return response.json();
  }

  // Get real-time insights
  async getRealTimeInsights(companyId) {
    const response = await fetch(`${this.baseURL}/api/pathway/realtime/${companyId}`);
    return response.json();
  }

  // Check Pathway health
  async checkHealth() {
    const response = await fetch(`${this.baseURL}/api/pathway/health`);
    return response.json();
  }

  // Helper method to convert files to base64
  async convertFilesToBase64(files) {
    const filePromises = Array.from(files).map(file => {
      return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = () => {
          resolve({
            filename: file.name,
            content: reader.result.split(',')[1], // Remove data:type;base64, prefix
            file_type: this.getFileType(file.name)
          });
        };
        reader.readAsDataURL(file);
      });
    });
    
    return Promise.all(filePromises);
  }

  getFileType(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const typeMap = {
      'xlsx': 'excel',
      'xls': 'excel',
      'csv': 'csv',
      'pdf': 'pdf'
    };
    return typeMap[ext] || 'unknown';
  }
}

// Usage in your webapp
const cfoAPI = new CFOHelperAPI();

// Example: Upload files and analyze scenario
async function integrateFinancialAnalysis() {
  try {
    // 1. Upload financial data
    const fileInput = document.getElementById('financial-files');
    const uploadResult = await cfoAPI.uploadFinancialData('your-company-id', fileInput.files);
    console.log('Upload result:', uploadResult);

    // 2. Get financial context
    const context = await cfoAPI.getFinancialContext('your-company-id');
    console.log('Financial context:', context);

    // 3. Run scenario analysis
    const scenarioResult = await cfoAPI.analyzeScenario({
      company_id: 'your-company-id',
      spending_change: -10,
      pricing_change: 5,
      hiring_count: 2,
      marketing_budget: 25000
    });
    console.log('Scenario analysis:', scenarioResult);

    // 4. Get real-time insights
    const insights = await cfoAPI.getRealTimeInsights('your-company-id');
    console.log('Real-time insights:', insights);

  } catch (error) {
    console.error('CFO Helper integration error:', error);
  }
}

export default CFOHelperAPI;
