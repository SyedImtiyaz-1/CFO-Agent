import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui';

const About: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          CFO Helper Agent
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Your AI-powered financial planning companion that simulates budget scenarios 
          and provides clear, actionable insights for better decision making.
        </p>
      </div>

      {/* Problem Statement */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl text-red-600">The Problem</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 mb-4">
            Managing money is tough — whether for a startup founder, a student fest organizer, 
            or a small business owner. People constantly ask questions like:
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4">
            <li>"If I hire 2 more engineers, can I survive 6 months?"</li>
            <li>"If we spend ₹10,000 extra on marketing, what's left for prizes?"</li>
            <li>"If I increase product price by 10%, what happens to profit?"</li>
          </ul>
          <p className="text-gray-700">
            Most people use Excel sheets, but those are too basic and don't show clear "what if" outcomes.
          </p>
        </CardContent>
      </Card>

      {/* Solution */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl text-green-600">Our Solution</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 mb-4">
            CFO Helper Agent is a Finance Helper that bridges this gap by providing:
          </p>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Interactive Controls</h3>
              <p className="text-gray-600 text-sm">
                Adjust inputs with intuitive sliders for spending, pricing, and hiring decisions.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Visual Forecasts</h3>
              <p className="text-gray-600 text-sm">
                See the impact on your budget and runway through clear charts and text summaries.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Shareable Reports</h3>
              <p className="text-gray-600 text-sm">
                Generate and export detailed reports that you can share with stakeholders.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Features */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl text-blue-600">Key Features</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">📊 Data Upload & Analysis</h4>
              <p className="text-gray-600 text-sm mb-4">
                Upload your financial data in PDF, Excel, or CSV format. Our AI reads and understands your data structure.
              </p>
              
              <h4 className="font-semibold text-gray-900 mb-2">🎛️ Scenario Simulation</h4>
              <p className="text-gray-600 text-sm mb-4">
                Use interactive sliders to adjust spending, pricing, and hiring parameters in real-time.
              </p>
              
              <h4 className="font-semibold text-gray-900 mb-2">📈 Visual Insights</h4>
              <p className="text-gray-600 text-sm">
                Get instant feedback through charts and detailed text analysis showing budget impact.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">📋 Export Reports</h4>
              <p className="text-gray-600 text-sm mb-4">
                Generate professional reports that you can share with investors, team members, or stakeholders.
              </p>
              
              <h4 className="font-semibold text-gray-900 mb-2">📊 Usage Tracking</h4>
              <p className="text-gray-600 text-sm mb-4">
                Monitor how many scenarios you've tested and reports you've generated.
              </p>
              
              <h4 className="font-semibold text-gray-900 mb-2">🔄 Pathway-Powered Real-time Updates</h4>
              <p className="text-gray-600 text-sm">
                Leverages Pathway's Live Data Framework for real-time financial data processing, fresh insights, and continuous monitoring of your financial health.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* How It Works */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl text-indigo-600">How It Works</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="flex items-start space-x-4">
              <div className="bg-indigo-100 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                <span className="text-indigo-600 font-semibold">1</span>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Upload Your Data</h4>
                <p className="text-gray-600 text-sm">
                  Upload your financial documents (Excel, PDF, CSV). Pathway's AI automatically parses and extracts key financial metrics in real-time.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="bg-indigo-100 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                <span className="text-indigo-600 font-semibold">2</span>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Adjust Parameters</h4>
                <p className="text-gray-600 text-sm">
                  Use our intuitive sliders to modify spending levels, pricing strategies, and hiring plans.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="bg-indigo-100 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                <span className="text-indigo-600 font-semibold">3</span>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Get AI-Powered Results</h4>
                <p className="text-gray-600 text-sm">
                  Pathway's Live Data Framework processes your scenarios in real-time, providing instant insights with fresh data and AI-driven recommendations.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="bg-indigo-100 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                <span className="text-indigo-600 font-semibold">4</span>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Export & Share</h4>
                <p className="text-gray-600 text-sm">
                  Generate comprehensive reports and share your findings with stakeholders.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* CTA */}
      <div className="text-center py-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Ready to Make Smarter Financial Decisions?
        </h2>
        <p className="text-gray-600 mb-6">
          Start using CFO Helper Agent today and transform how you plan your finances.
        </p>
        <a 
          href="/agent" 
          className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors inline-block"
        >
          Try CFO Helper Agent
        </a>
      </div>
    </div>
  );
};

export default About;
