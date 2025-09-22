export interface FinancialContext {
  company_id: string;
  current_cash: number;
  monthly_revenue: number;
  monthly_expenses: number;
  marketing_spend: number;
  team_size: number;
  average_salary: number;
  price_per_unit: number;
  units_sold: number;
  runway_months: number;
}

export interface ScenarioChanges {
  monthly_revenue?: number;
  monthly_expenses?: number;
  marketing_spend?: number;
  team_size?: number;
  salary_change_percent?: number;
  price_change_percent?: number;
}

export interface ImpactAnalysis {
  revenue_change: number;
  expense_change: number;
  marketing_impact: number;
  runway_impact: number;
  profit_impact: number;
  [key: string]: number; // Index signature for dynamic access
}

export interface AnalysisResult {
  summary: string;
  impact_analysis: ImpactAnalysis;
  original_context: FinancialContext;
  updated_context: FinancialContext;
}
