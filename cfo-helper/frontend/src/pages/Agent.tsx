import React, { useState, useRef } from 'react';
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent, 
  Button, 
  Label, 
  Slider,
  useToast,
  Toast,
  DownloadIcon
} from '../components/ui';

interface UploadedFile {
  name: string;
  size: number;
  type: string;
  data: string;
  pathwayResult?: any; // Result from Pathway processing
}

interface ScenarioParams {
  spending_change: number;
  pricing_change: number;
  hiring_count: number;
  marketing_budget: number;
}

interface AnalysisResult {
  summary: string;
  current_runway: number;
  projected_runway: number;
  revenue_impact: number;
  expense_impact: number;
  profit_change: number;
  recommendations: string[];
  ai_analysis?: string;
  ai_powered?: boolean;
  charts_data: {
    monthly_cashflow: number[];
    runway_comparison: { current: number; projected: number };
    expense_breakdown: { category: string; amount: number }[];
  };
}

interface UsageStats {
  scenarios_tested: number;
  reports_exported: number;
  last_updated: string;
}

const Agent: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [scenarioParams, setScenarioParams] = useState<ScenarioParams>({
    spending_change: 0,
    pricing_change: 0,
    hiring_count: 0,
    marketing_budget: 0
  });
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [usageStats, setUsageStats] = useState<UsageStats>({
    scenarios_tested: 0,
    reports_exported: 0,
    last_updated: new Date().toISOString()
  });
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast, show } = useToast();

  // Handle file upload with Pathway processing
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    setIsUploading(true);
    const newFiles: UploadedFile[] = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      // Validate file type
      const allowedTypes = [
        'application/pdf',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv'
      ];
      
      if (!allowedTypes.includes(file.type)) {
        show('Error', `File type ${file.type} not supported. Please upload PDF, Excel, or CSV files.`, 'destructive');
        continue;
      }

      // Convert file to base64 and process with Pathway
      const reader = new FileReader();
      reader.onload = async (e) => {
        const result = e.target?.result as string;
        
        try {
          // Send to Pathway backend for processing
          const response = await fetch('http://localhost:8000/api/pathway/upload', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              filename: file.name,
              file_data: result,
              file_type: file.type
            }),
          });

          if (!response.ok) {
            throw new Error('Failed to process file with Pathway');
          }

          const pathwayResult = await response.json();
          
          newFiles.push({
            name: file.name,
            size: file.size,
            type: file.type,
            data: result,
            pathwayResult: pathwayResult.result // Store Pathway processing result
          });

          if (newFiles.length === files.length) {
            setUploadedFiles(prev => [...prev, ...newFiles]);
            show('Success', `${newFiles.length} file(s) processed with Pathway successfully`);
            setIsUploading(false);
          }
        } catch (error) {
          console.error('Pathway processing error:', error);
          // Still add file but mark as unprocessed
          newFiles.push({
            name: file.name,
            size: file.size,
            type: file.type,
            data: result,
            pathwayResult: { error: 'Pathway processing failed' }
          });

          if (newFiles.length === files.length) {
            setUploadedFiles(prev => [...prev, ...newFiles]);
            show('Warning', `${newFiles.length} file(s) uploaded but some failed Pathway processing`, 'destructive');
            setIsUploading(false);
          }
        }
      };
      reader.readAsDataURL(file);
    }
  };

  // Remove uploaded file
  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Handle scenario parameter changes
  const handleParamChange = (param: keyof ScenarioParams, value: number | number[]) => {
    const numValue = Array.isArray(value) ? value[0] : value;
    setScenarioParams(prev => ({
      ...prev,
      [param]: numValue
    }));
  };

  // Analyze scenario using Pathway
  const analyzeScenario = async () => {
    if (uploadedFiles.length === 0) {
      show('Error', 'Please upload at least one financial document before analyzing.', 'destructive');
      return;
    }

    setIsAnalyzing(true);
    
    try {
      // Use Pathway backend for scenario analysis
      const response = await fetch('http://localhost:8000/api/pathway/scenario', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company_id: 'default_company',
          spending_change: scenarioParams.spending_change,
          pricing_change: scenarioParams.pricing_change,
          hiring_count: scenarioParams.hiring_count,
          marketing_budget: scenarioParams.marketing_budget
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze scenario with Pathway');
      }

      const pathwayResult = await response.json();
      
      // Convert Pathway result to our AnalysisResult format
      const analysisResult: AnalysisResult = {
        summary: pathwayResult.summary || `Pathway analysis complete: With ${scenarioParams.spending_change}% spending change, ${scenarioParams.pricing_change}% pricing change, ${scenarioParams.hiring_count} new hires, and ₹${scenarioParams.marketing_budget.toLocaleString()} marketing budget.`,
        current_runway: pathwayResult.original_context?.runway_months || 18,
        projected_runway: pathwayResult.updated_context?.runway_months || 18,
        revenue_impact: pathwayResult.impact_analysis?.revenue_change || 0,
        expense_impact: pathwayResult.impact_analysis?.expense_change || 0,
        profit_change: pathwayResult.impact_analysis?.profit_impact || 0,
        recommendations: pathwayResult.ai_recommendations || [
          "Analysis powered by Pathway's real-time processing",
          "Data freshness ensures accurate projections", 
          "Consider monitoring key metrics regularly"
        ],
        ai_analysis: pathwayResult.ai_analysis || null,
        ai_powered: pathwayResult.ai_powered || false,
        charts_data: {
          monthly_cashflow: Array.from({length: 12}, (_, i) => 
            (pathwayResult.updated_context?.monthly_revenue || 50000) - 
            (pathwayResult.updated_context?.monthly_expenses || 35000) + 
            Math.random() * 5000
          ),
          runway_comparison: {
            current: pathwayResult.original_context?.runway_months || 18,
            projected: pathwayResult.updated_context?.runway_months || 18
          },
          expense_breakdown: [
            { category: "Salaries", amount: 80000 + (scenarioParams.hiring_count * 8000) },
            { category: "Marketing", amount: scenarioParams.marketing_budget },
            { category: "Operations", amount: 25000 + (scenarioParams.spending_change * 500) },
            { category: "Other", amount: 15000 }
          ]
        }
      };

      setAnalysisResult(analysisResult);
      setUsageStats(prev => ({
        ...prev,
        scenarios_tested: prev.scenarios_tested + 1,
        last_updated: new Date().toISOString()
      }));
      
      show('Success', 'Pathway-powered scenario analysis completed successfully!');
    } catch (error) {
      console.error('Pathway analysis error:', error);
      show('Error', 'Failed to analyze scenario with Pathway. Please try again.', 'destructive');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Export report
  const exportReport = () => {
    if (!analysisResult) return;

    const reportContent = `
# CFO Helper Agent - Financial Scenario Report

## Scenario Parameters
- Spending Change: ${scenarioParams.spending_change}%
- Pricing Change: ${scenarioParams.pricing_change}%
- New Hires: ${scenarioParams.hiring_count}
- Marketing Budget: ₹${scenarioParams.marketing_budget.toLocaleString()}

## Analysis Summary
${analysisResult.summary}

## Key Metrics
- Current Runway: ${analysisResult.current_runway} months
- Projected Runway: ${analysisResult.projected_runway} months
- Revenue Impact: ₹${analysisResult.revenue_impact.toLocaleString()}
- Expense Impact: ₹${analysisResult.expense_impact.toLocaleString()}
- Net Profit Change: ₹${analysisResult.profit_change.toLocaleString()}

## Recommendations
${analysisResult.recommendations.map((rec, i) => `${i + 1}. ${rec}`).join('\n')}

## Generated on: ${new Date().toLocaleString()}
`;

    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cfo-helper-report-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    setUsageStats(prev => ({
      ...prev,
      reports_exported: prev.reports_exported + 1,
      last_updated: new Date().toISOString()
    }));

    show('Success', 'Report exported successfully!');
  };

  // Format currency
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1
    }).format(value);
  };

  // Format number with one decimal place
  const formatNumber = (value: number): string => {
    return value.toFixed(1);
  };

  // Generate month labels
  const getMonthLabels = (): string[] => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const currentMonth = new Date().getMonth();
    return Array.from({length: 12}, (_, i) => months[(currentMonth + i) % 12]);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {toast && (
        <Toast
          title={toast.title}
          description={toast.description}
          variant={toast.variant}
          onClose={() => {}}
        />
      )}

      {/* Usage Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{usageStats.scenarios_tested}</div>
              <p className="text-sm text-gray-500">Scenarios Tested</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{usageStats.reports_exported}</div>
              <p className="text-sm text-gray-500">Reports Exported</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{uploadedFiles.length}</div>
              <p className="text-sm text-gray-500">Files Uploaded</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* File Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle>Upload Financial Data</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                multiple
                accept=".pdf,.xlsx,.xls,.csv"
                className="hidden"
              />
              <div className="space-y-2">
                <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <div className="text-sm text-gray-600">
                  <Button 
                    variant="outline" 
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploading}
                  >
                    {isUploading ? 'Uploading...' : 'Choose Files'}
                  </Button>
                  <p className="mt-2">or drag and drop</p>
                </div>
                <p className="text-xs text-gray-500">PDF, Excel, CSV up to 10MB each</p>
              </div>
            </div>

            {uploadedFiles.length > 0 && (
              <div className="space-y-2">
                <Label>Uploaded Files:</Label>
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded">
                    <div className="flex items-center space-x-3">
                      <div className="text-blue-600">
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{file.name}</p>
                        <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeFile(index)}
                    >
                      Remove
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Scenario Parameters */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Scenario Parameters</CardTitle>
            <Button 
              onClick={analyzeScenario}
              disabled={isAnalyzing || uploadedFiles.length === 0}
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Scenario'}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-6">
              <div>
                <Label>Spending Change (%)</Label>
                <div className="flex items-center space-x-4 mt-2">
                  <Slider
                    min={-50}
                    max={100}
                    step={5}
                    value={[scenarioParams.spending_change]}
                    onValueChange={(value) => handleParamChange('spending_change', value)}
                    className="flex-1"
                  />
                  <span className="w-16 text-right font-medium">
                    {scenarioParams.spending_change}%
                  </span>
                </div>
              </div>

              <div>
                <Label>Pricing Change (%)</Label>
                <div className="flex items-center space-x-4 mt-2">
                  <Slider
                    min={-30}
                    max={50}
                    step={1}
                    value={[scenarioParams.pricing_change]}
                    onValueChange={(value) => handleParamChange('pricing_change', value)}
                    className="flex-1"
                  />
                  <span className="w-16 text-right font-medium">
                    {scenarioParams.pricing_change}%
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <Label>New Hires</Label>
                <div className="flex items-center space-x-4 mt-2">
                  <Slider
                    min={0}
                    max={20}
                    step={1}
                    value={[scenarioParams.hiring_count]}
                    onValueChange={(value) => handleParamChange('hiring_count', value)}
                    className="flex-1"
                  />
                  <span className="w-16 text-right font-medium">
                    {scenarioParams.hiring_count}
                  </span>
                </div>
              </div>

              <div>
                <Label>Marketing Budget (₹)</Label>
                <div className="flex items-center space-x-4 mt-2">
                  <Slider
                    min={0}
                    max={100000}
                    step={5000}
                    value={[scenarioParams.marketing_budget]}
                    onValueChange={(value) => handleParamChange('marketing_budget', value)}
                    className="flex-1"
                  />
                  <span className="w-20 text-right font-medium">
                    ₹{scenarioParams.marketing_budget.toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysisResult && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Analysis Results</CardTitle>
              <Button variant="outline" size="sm" onClick={exportReport}>
                <DownloadIcon className="mr-2 h-4 w-4" />
                Export Report
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Summary */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">Executive Summary</h4>
                <p className="text-blue-800 text-sm">{analysisResult.summary}</p>
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {formatNumber(analysisResult.projected_runway)}
                  </div>
                  <p className="text-sm text-gray-600">Projected Runway (months)</p>
                  <p className="text-xs text-gray-500">
                    vs {formatNumber(analysisResult.current_runway)} current
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg text-center">
                  <div className={`text-2xl font-bold ${analysisResult.revenue_impact >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(analysisResult.revenue_impact)}
                  </div>
                  <p className="text-sm text-gray-600">Revenue Impact</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg text-center">
                  <div className={`text-2xl font-bold ${analysisResult.profit_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(analysisResult.profit_change)}
                  </div>
                  <p className="text-sm text-gray-600">Profit Change</p>
                </div>
              </div>

              {/* Charts Placeholder */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-3">Monthly Cash Flow Projection</h4>
                  <div className="h-48 bg-white rounded border p-4">
                    <div className="h-full flex flex-col">
                      <div className="flex-1 relative">
                        <svg className="w-full h-full" viewBox="0 0 400 120">
                          {/* Chart background grid */}
                          <defs>
                            <pattern id="grid" width="33.33" height="20" patternUnits="userSpaceOnUse">
                              <path d="M 33.33 0 L 0 0 0 20" fill="none" stroke="#e5e7eb" strokeWidth="0.5"/>
                            </pattern>
                          </defs>
                          <rect width="100%" height="100%" fill="url(#grid)" />
                          
                          {/* Cash flow line */}
                          <polyline
                            fill="none"
                            stroke="#3b82f6"
                            strokeWidth="2"
                            points={analysisResult.charts_data.monthly_cashflow.map((value, index) => {
                              const x = (index * 400) / 11;
                              const maxValue = Math.max(...analysisResult.charts_data.monthly_cashflow);
                              const minValue = Math.min(...analysisResult.charts_data.monthly_cashflow);
                              const range = maxValue - minValue || 1;
                              const y = 100 - ((value - minValue) / range) * 80;
                              return `${x},${y}`;
                            }).join(' ')}
                          />
                          
                          {/* Data points */}
                          {analysisResult.charts_data.monthly_cashflow.map((value, index) => {
                            const x = (index * 400) / 11;
                            const maxValue = Math.max(...analysisResult.charts_data.monthly_cashflow);
                            const minValue = Math.min(...analysisResult.charts_data.monthly_cashflow);
                            const range = maxValue - minValue || 1;
                            const y = 100 - ((value - minValue) / range) * 80;
                            return (
                              <circle
                                key={index}
                                cx={x}
                                cy={y}
                                r="3"
                                fill="#3b82f6"
                                className="hover:r-4 transition-all"
                              >
                                <title>{getMonthLabels()[index]}: {formatCurrency(value)}</title>
                              </circle>
                            );
                          })}
                        </svg>
                      </div>
                      
                      {/* Month labels */}
                      <div className="flex justify-between text-xs text-gray-500 mt-2">
                        {getMonthLabels().map((month, index) => (
                          <span key={index} className={index % 2 === 0 ? '' : 'opacity-60'}>
                            {month}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-3">Expense Breakdown</h4>
                  <div className="h-48 bg-white rounded border p-4">
                    <div className="h-full flex">
                      {/* Pie Chart */}
                      <div className="flex-1 flex items-center justify-center">
                        <svg className="w-32 h-32" viewBox="0 0 100 100">
                          {(() => {
                            const total = analysisResult.charts_data.expense_breakdown.reduce((sum, item) => sum + item.amount, 0);
                            let cumulativePercentage = 0;
                            const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];
                            
                            return analysisResult.charts_data.expense_breakdown.map((item, index) => {
                              const percentage = (item.amount / total) * 100;
                              const startAngle = (cumulativePercentage / 100) * 360;
                              const endAngle = ((cumulativePercentage + percentage) / 100) * 360;
                              
                              const startAngleRad = (startAngle - 90) * (Math.PI / 180);
                              const endAngleRad = (endAngle - 90) * (Math.PI / 180);
                              
                              const largeArcFlag = percentage > 50 ? 1 : 0;
                              
                              const x1 = 50 + 40 * Math.cos(startAngleRad);
                              const y1 = 50 + 40 * Math.sin(startAngleRad);
                              const x2 = 50 + 40 * Math.cos(endAngleRad);
                              const y2 = 50 + 40 * Math.sin(endAngleRad);
                              
                              const pathData = [
                                `M 50 50`,
                                `L ${x1} ${y1}`,
                                `A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2}`,
                                'Z'
                              ].join(' ');
                              
                              cumulativePercentage += percentage;
                              
                              return (
                                <path
                                  key={index}
                                  d={pathData}
                                  fill={colors[index % colors.length]}
                                  stroke="white"
                                  strokeWidth="1"
                                  className="hover:opacity-80 transition-opacity"
                                >
                                  <title>{item.category}: {formatCurrency(item.amount)} ({percentage.toFixed(1)}%)</title>
                                </path>
                              );
                            });
                          })()}
                        </svg>
                      </div>
                      
                      {/* Legend */}
                      <div className="flex-1 pl-4">
                        <div className="space-y-2">
                          {(() => {
                            const total = analysisResult.charts_data.expense_breakdown.reduce((sum, item) => sum + item.amount, 0);
                            const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];
                            
                            return analysisResult.charts_data.expense_breakdown.map((item, index) => {
                              const percentage = (item.amount / total) * 100;
                              return (
                                <div key={index} className="flex items-center text-sm">
                                  <div 
                                    className="w-3 h-3 rounded-full mr-2 flex-shrink-0"
                                    style={{ backgroundColor: colors[index % colors.length] }}
                                  ></div>
                                  <div className="flex-1 min-w-0">
                                    <div className="font-medium truncate">{item.category}</div>
                                    <div className="text-xs text-gray-500">
                                      {formatCurrency(item.amount)} ({percentage.toFixed(1)}%)
                                    </div>
                                  </div>
                                </div>
                              );
                            });
                          })()}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Analysis Section */}
              {analysisResult.ai_analysis && (
                <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg border border-purple-200">
                  <div className="flex items-center mb-3">
                    <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                    <h4 className="font-semibold text-purple-900">
                      AI-Powered Financial Analysis
                      {analysisResult.ai_powered && (
                        <span className="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                          GROQ Llama-3.1 Enhanced
                        </span>
                      )}
                    </h4>
                  </div>
                  <div className="prose prose-sm max-w-none">
                    <div className="text-purple-800 text-sm whitespace-pre-wrap">
                      {analysisResult.ai_analysis}
                    </div>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h4 className="font-semibold text-yellow-900 mb-3">
                  {analysisResult.ai_powered ? 'AI-Generated Recommendations' : 'Recommendations'}
                </h4>
                <ul className="space-y-2">
                  {analysisResult.recommendations.map((rec, index) => (
                    <li key={index} className="text-yellow-800 text-sm flex items-start">
                      <span className="text-yellow-600 mr-2">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Agent;
