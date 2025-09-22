// React Component Integration Example
// Drop this component into your existing React webapp

import React, { useState, useRef } from 'react';
import CFOHelperAPI from './api-integration';

interface CFOHelperWidgetProps {
  companyId: string;
  apiBaseURL?: string;
  onAnalysisComplete?: (result: any) => void;
}

const CFOHelperWidget: React.FC<CFOHelperWidgetProps> = ({ 
  companyId, 
  apiBaseURL = 'http://localhost:8000',
  onAnalysisComplete 
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [scenarioParams, setScenarioParams] = useState({
    spending_change: 0,
    pricing_change: 0,
    hiring_count: 0,
    marketing_budget: 0
  });
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cfoAPI = new CFOHelperAPI(apiBaseURL);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsLoading(true);
    try {
      const result = await cfoAPI.uploadFinancialData(companyId, files);
      console.log('Files uploaded successfully:', result);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const runScenarioAnalysis = async () => {
    setIsLoading(true);
    try {
      const result = await cfoAPI.analyzeScenario({
        company_id: companyId,
        ...scenarioParams
      });
      
      setAnalysisResult(result);
      onAnalysisComplete?.(result);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="cfo-helper-widget p-6 border rounded-lg bg-white shadow-lg">
      <h3 className="text-xl font-bold mb-4">CFO Helper Agent</h3>
      
      {/* File Upload */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Upload Financial Data</label>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.xlsx,.xls,.csv"
          onChange={handleFileUpload}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
      </div>

      {/* Scenario Parameters */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-1">Spending Change (%)</label>
          <input
            type="range"
            min="-50"
            max="50"
            value={scenarioParams.spending_change}
            onChange={(e) => setScenarioParams(prev => ({
              ...prev,
              spending_change: parseInt(e.target.value)
            }))}
            className="w-full"
          />
          <span className="text-sm text-gray-600">{scenarioParams.spending_change}%</span>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Pricing Change (%)</label>
          <input
            type="range"
            min="-30"
            max="30"
            value={scenarioParams.pricing_change}
            onChange={(e) => setScenarioParams(prev => ({
              ...prev,
              pricing_change: parseInt(e.target.value)
            }))}
            className="w-full"
          />
          <span className="text-sm text-gray-600">{scenarioParams.pricing_change}%</span>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">New Hires</label>
          <input
            type="range"
            min="0"
            max="20"
            value={scenarioParams.hiring_count}
            onChange={(e) => setScenarioParams(prev => ({
              ...prev,
              hiring_count: parseInt(e.target.value)
            }))}
            className="w-full"
          />
          <span className="text-sm text-gray-600">{scenarioParams.hiring_count} people</span>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Marketing Budget</label>
          <input
            type="range"
            min="0"
            max="100000"
            step="5000"
            value={scenarioParams.marketing_budget}
            onChange={(e) => setScenarioParams(prev => ({
              ...prev,
              marketing_budget: parseInt(e.target.value)
            }))}
            className="w-full"
          />
          <span className="text-sm text-gray-600">₹{scenarioParams.marketing_budget.toLocaleString()}</span>
        </div>
      </div>

      {/* Analyze Button */}
      <button
        onClick={runScenarioAnalysis}
        disabled={isLoading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {isLoading ? 'Analyzing...' : 'Run Financial Analysis'}
      </button>

      {/* Results */}
      {analysisResult && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold mb-2">Analysis Results</h4>
          <p className="text-sm text-gray-700">{analysisResult.summary}</p>
          
          {analysisResult.recommendations && (
            <div className="mt-3">
              <h5 className="font-medium text-sm">Recommendations:</h5>
              <ul className="text-xs text-gray-600 list-disc list-inside">
                {analysisResult.recommendations.map((rec: string, i: number) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CFOHelperWidget;
