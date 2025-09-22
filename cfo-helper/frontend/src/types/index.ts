export interface ScenarioInput {
  current_cash: number;
  monthly_revenue: number;
  monthly_expenses: number;
  new_hires: number;
  salary_per_hire: number;
  marketing_spend: number;
  price_increase_percent: number;
  months_to_forecast: number;
}

export interface MonthlyForecast {
  month: number;
  revenue: number;
  expenses: number;
  net_income: number;
  balance: number;
}

export interface ScenarioResult {
  scenario_id: string;
  timestamp: string;
  input: ScenarioInput;
  monthly_forecast: MonthlyForecast[];
  total_months_of_runway: number;
  final_cash_balance: number;
}

export interface UsageStats {
  total_scenarios_run: number;
  scenarios_stored: number;
  last_updated: string;
}
