import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt

class IHEPFinancialModel:
    """
    Comprehensive 30-year financial model for the Integrated Health 
    Empowerment Program with amortization, NPV, IRR, and sensitivity analysis.
    
    This model implements morphogenetic financial forecasting where each
    phase's parameters recursively inform subsequent phase assumptions,
    creating a self-validating projection framework.
    """
    
    def __init__(self, discount_rate: float = 0.10):
        """
        Initialize the financial model with core parameters.
        
        Args:
            discount_rate: The discount rate for NPV calculations (default 10%)
        """
        self.discount_rate = discount_rate
        self.tax_rate = 0.27  # Blended federal and state corporate tax rate
        self.useful_life = 15  # Amortization period for capitalized development
        
        # Phase I parameters (Year 1)
        self.phase1_personnel = 2_450_000
        self.phase1_infrastructure = 150_000
        self.phase1_other = 400_000  # Compliance, software, community combined
        self.phase1_contingency = 0.15
        
        # Phase II parameters (Years 2-5)
        self.phase2_growth_rate = 0.18  # 18% annual growth
        self.phase2_years = 4
        
        # Phase III parameters (Years 6-10)
        self.phase3_growth_rate = 0.12  # 12% annual growth
        self.phase3_years = 5
        
        # Commercial phase parameters (Years 11-20)
        self.commercial_base_cost_year11 = 14_000_000
        self.commercial_cost_growth_early = 0.10  # Years 11-13
        self.commercial_cost_growth_mid = 0.08    # Years 14-17
        self.commercial_cost_growth_late = 0.06   # Years 18-20
        
        # Maturity phase parameters (Years 21-30)
        self.maturity_cost_growth = 0.05  # 5% annual growth
        
        # Revenue model parameters
        self.initial_members_year11 = 5_000
        self.member_growth_rate = 0.40  # 40% annual growth in members
        self.pmpm_rate = 225  # Per member per month reimbursement
        
        # Storage for calculated values
        self.annual_costs = np.zeros(30)
        self.annual_revenues = np.zeros(30)
        self.annual_cash_flows = np.zeros(30)
        self.cumulative_cash_flows = np.zeros(30)
        
    def calculate_phase_costs(self, 
                             phase_name: str,
                             start_year: int,
                             duration: int,
                             initial_personnel: float,
                             initial_infra: float,
                             initial_other: float,
                             growth_rate: float) -> float:
        """
        Calculate total costs for a development phase using compounded growth.
        
        This implements the mathematical formula:
        Total = P * ((1 + g)^n - 1) / g
        
        Args:
            phase_name: Name of the phase for logging
            start_year: Starting year (1-indexed)
            duration: Number of years in phase
            initial_personnel: Personnel cost in first year of phase
            initial_infra: Infrastructure cost in first year of phase
            initial_other: Other costs in first year of phase
            growth_rate: Annual compounded growth rate
            
        Returns:
            Total phase cost including contingency
        """
        print(f"\n{'='*60}")
        print(f"Calculating {phase_name}")
        print(f"Years {start_year} through {start_year + duration - 1}")
        print(f"{'='*60}")
        
        phase_subtotal = 0.0
        
        for year_offset in range(duration):
            year = start_year + year_offset
            
            # Apply compounded growth for each year after the first in the phase
            if year_offset > 0:
                growth_factor = (1 + growth_rate) ** year_offset
            else:
                growth_factor = 1.0
            
            personnel = initial_personnel * growth_factor
            infrastructure = initial_infra * growth_factor
            other = initial_other * growth_factor
            
            annual_total = personnel + infrastructure + other
            phase_subtotal += annual_total
            
            # Store in annual costs array (0-indexed)
            self.annual_costs[year - 1] = annual_total
            
            print(f"\nYear {year}:")
            print(f"  Personnel: ${personnel:,.2f}")
            print(f"  Infrastructure: ${infrastructure:,.2f}")
            print(f"  Other Costs: ${other:,.2f}")
            print(f"  Annual Total: ${annual_total:,.2f}")
        
        # Apply contingency to phase total
        phase_with_contingency = phase_subtotal * (1 + self.phase1_contingency)
        
        print(f"\n{'-'*60}")
        print(f"Phase Subtotal: ${phase_subtotal:,.2f}")
        print(f"Contingency ({self.phase1_contingency:.1%}): "
              f"${phase_subtotal * self.phase1_contingency:,.2f}")
        print(f"Phase Total: ${phase_with_contingency:,.2f}")
        
        return phase_with_contingency
    
    def calculate_development_phases(self) -> Dict[str, float]:
        """
        Calculate costs for all three development phases (Years 1-10).
        
        Returns:
            Dictionary with phase totals and cumulative 10-year cost
        """
        results = {}
        
        # Phase I: Year 1
        results['phase1'] = self.calculate_phase_costs(
            phase_name="Phase I - Pilot & Feasibility",
            start_year=1,
            duration=1,
            initial_personnel=self.phase1_personnel,
            initial_infra=self.phase1_infrastructure,
            initial_other=self.phase1_other,
            growth_rate=0.0  # Single year, no growth
        )
        
        # Phase II: Years 2-5
        # Scale up initial costs for Phase II based on expansion
        phase2_personnel_base = self.phase1_personnel * 2.0
        phase2_infra_base = self.phase1_infrastructure * 3.0
        phase2_other_base = self.phase1_other * 1.5
        
        results['phase2'] = self.calculate_phase_costs(
            phase_name="Phase II - Expansion & Validation",
            start_year=2,
            duration=self.phase2_years,
            initial_personnel=phase2_personnel_base,
            initial_infra=phase2_infra_base,
            initial_other=phase2_other_base,
            growth_rate=self.phase2_growth_rate
        )
        
        # Phase III: Years 6-10
        # Further scale up for national commercialization
        phase3_personnel_base = phase2_personnel_base * 1.6
        phase3_infra_base = phase2_infra_base * 2.0
        phase3_other_base = phase2_other_base * 1.8
        
        results['phase3'] = self.calculate_phase_costs(
            phase_name="Phase III - Commercialization & Cure Roadmap",
            start_year=6,
            duration=self.phase3_years,
            initial_personnel=phase3_personnel_base,
            initial_infra=phase3_infra_base,
            initial_other=phase3_other_base,
            growth_rate=self.phase3_growth_rate
        )
        
        results['total_10year'] = sum(results.values())
        
        print(f"\n{'='*60}")
        print(f"CUMULATIVE 10-YEAR INVESTMENT REQUIRED")
        print(f"{'='*60}")
        print(f"Total: ${results['total_10year']:,.2f}")
        
        return results
    
    def calculate_commercial_phase(self) -> None:
        """
        Calculate costs and revenues for Years 11-20 commercial phase.
        
        This phase introduces revenue streams and varying cost growth rates
        as the platform matures and achieves economies of scale.
        """
        print(f"\n{'='*60}")
        print(f"Commercial Phase - Years 11-20")
        print(f"{'='*60}")
        
        for year in range(11, 21):
            # Determine growth rate based on maturity
            if year <= 13:
                growth_rate = self.commercial_cost_growth_early
            elif year <= 17:
                growth_rate = self.commercial_cost_growth_mid
            else:
                growth_rate = self.commercial_cost_growth_late
            
            # Calculate operating cost with declining growth rate
            years_from_base = year - 11
            cost = self.commercial_base_cost_year11 * ((1 + growth_rate) ** years_from_base)
            self.annual_costs[year - 1] = cost
            
            # Calculate revenue streams
            revenue = self._calculate_revenue_year(year)
            self.annual_revenues[year - 1] = revenue
            
            print(f"\nYear {year}:")
            print(f"  Operating Cost: ${cost:,.2f}")
            print(f"  Revenue: ${revenue:,.2f}")
            print(f"  Net Cash Flow: ${revenue - cost:,.2f}")
    
    def calculate_maturity_phase(self) -> None:
        """
        Calculate costs and revenues for Years 21-30 maturity phase.
        
        This phase shows stabilized cost growth with accelerating revenue
        as the platform achieves global scale and delivers cure breakthroughs.
        """
        print(f"\n{'='*60}")
        print(f"Maturity Phase - Years 21-30")
        print(f"{'='*60}")
        
        year_20_cost = self.annual_costs[19]  # Get Year 20 cost as base
        
        for year in range(21, 31):
            years_from_20 = year - 20
            cost = year_20_cost * ((1 + self.maturity_cost_growth) ** years_from_20)
            self.annual_costs[year - 1] = cost
            
            revenue = self._calculate_revenue_year(year)
            self.annual_revenues[year - 1] = revenue
            
            print(f"\nYear {year}:")
            print(f"  Operating Cost: ${cost:,.2f}")
            print(f"  Revenue: ${revenue:,.2f}")
            print(f"  Net Cash Flow: ${revenue - cost:,.2f}")
    
    def _calculate_revenue_year(self, year: int) -> float:
        """
        Calculate total revenue for a given year across all streams.
        
        Args:
            year: The year to calculate revenue for
            
        Returns:
            Total revenue for that year
        """
        # No revenue in Years 1-10
        if year <= 10:
            return 0.0
        
        # Insurance reimbursement revenue
        years_from_11 = year - 11
        members = self.initial_members_year11 * (
            (1 + self.member_growth_rate) ** years_from_11
        )
        insurance_revenue = members * self.pmpm_rate * 12
        
        # EHR licensing (starts Year 11, grows at 15% after initial ramp)
        if year == 11:
            ehr_revenue = 1_500_000
        else:
            ehr_revenue = 1_500_000 * (1.15 ** years_from_11)
        
        # Federal contracts (starts Year 12)
        if year < 12:
            federal_revenue = 0
        else:
            federal_revenue = 2_000_000 * (1.20 ** (year - 12))
        
        # International partnerships (starts Year 14)
        if year < 14:
            intl_revenue = 0
        else:
            intl_revenue = 1_000_000 * (1.35 ** (year - 14))
        
        # Digital twin research services (starts Year 13)
        if year < 13:
            research_revenue = 0
        else:
            research_revenue = 500_000 * (1.40 ** (year - 13))
        
        # Cure research milestone payments (Years 25-30)
        if year >= 25:
            cure_revenue = 25_000_000 if year == 25 else 10_000_000
        else:
            cure_revenue = 0
        
        # Accelerated growth in Years 21-30 from global expansion
        if year >= 21:
            # Apply additional 25% growth multiplier for Years 21-25
            if year <= 25:
                growth_multiplier = 1.25 ** (year - 20)
            else:
                # Then 15% growth for Years 26-30
                growth_multiplier = (1.25 ** 5) * (1.15 ** (year - 25))
            
            total_base = (insurance_revenue + ehr_revenue + federal_revenue + 
                         intl_revenue + research_revenue)
            total_revenue = total_base * growth_multiplier + cure_revenue
        else:
            total_revenue = (insurance_revenue + ehr_revenue + federal_revenue + 
                           intl_revenue + research_revenue + cure_revenue)
        
        return total_revenue
    
    def calculate_npv(self) -> float:
        """
        Calculate Net Present Value of all cash flows over 30 years.
        
        NPV = Σ(CF_t / (1 + r)^t) for t = 1 to 30
        
        Returns:
            Net Present Value in dollars
        """
        npv = 0.0
        for year in range(30):
            cash_flow = self.annual_revenues[year] - self.annual_costs[year]
            discount_factor = (1 + self.discount_rate) ** (year + 1)
            npv += cash_flow / discount_factor
        
        return npv
    
    def calculate_irr(self) -> float:
        """
        Calculate Internal Rate of Return using Newton-Raphson method.
        
        IRR is the discount rate that makes NPV = 0.
        
        Returns:
            Internal Rate of Return as a percentage
        """
        # Use numpy's financial function for accurate IRR calculation
        cash_flows = self.annual_revenues - self.annual_costs
        irr = np.irr(cash_flows)
        return irr * 100  # Convert to percentage
    
    def calculate_amortization(self) -> pd.DataFrame:
        """
        Calculate amortization schedule for capitalized development costs.
        
        Returns:
            DataFrame with annual amortization expense and cumulative amortization
        """
        # Identify capitalizable costs from Years 1-5 (60% of total)
        total_years_1_5 = sum(self.annual_costs[0:5])
        capitalizable_percentage = 0.60
        capitalized_amount = total_years_1_5 * capitalizable_percentage
        
        annual_amortization = capitalized_amount / self.useful_life
        
        amortization_schedule = []
        cumulative = 0
        
        for year in range(1, 31):
            if 6 <= year <= 20:  # Amortization occurs Years 6-20
                amortization = annual_amortization
                cumulative += amortization
                tax_benefit = amortization * self.tax_rate
            else:
                amortization = 0
                tax_benefit = 0
            
            amortization_schedule.append({
                'Year': year,
                'Annual_Amortization': amortization,
                'Cumulative_Amortization': cumulative,
                'Tax_Benefit': tax_benefit,
                'Net_Book_Value': max(0, capitalized_amount - cumulative)
            })
        
        return pd.DataFrame(amortization_schedule)
    
    def run_complete_analysis(self) -> Dict:
        """
        Execute the complete 30-year financial analysis.
        
        Returns:
            Dictionary containing all key financial metrics
        """
        print("\n" + "="*60)
        print("IHEP 30-YEAR FINANCIAL MODEL")
        print("="*60)
        
        # Calculate all phases
        development_results = self.calculate_development_phases()
        self.calculate_commercial_phase()
        self.calculate_maturity_phase()
        
        # Calculate cash flows
        self.annual_cash_flows = self.annual_revenues - self.annual_costs
        self.cumulative_cash_flows = np.cumsum(self.annual_cash_flows)
        
        # Find break-even year
        break_even_year = None
        for year in range(30):
            if self.cumulative_cash_flows[year] >= 0:
                break_even_year = year + 1
                break
        
        # Calculate financial metrics
        npv = self.calculate_npv()
        irr = self.calculate_irr()
        amortization_df = self.calculate_amortization()
        
        # Calculate benefit-cost ratio
        total_benefits = sum(self.annual_revenues)
        total_costs = sum(self.annual_costs)
        bcr = total_benefits / total_costs if total_costs > 0 else 0
        
        # Summary results
        results = {
            'development_phases': development_results,
            'total_30year_costs': sum(self.annual_costs),
            'total_30year_revenue': sum(self.annual_revenues),
            'cumulative_operating_margin': sum(self.annual_cash_flows),
            'npv': npv,
            'irr': irr,
            'break_even_year': break_even_year,
            'benefit_cost_ratio': bcr,
            'amortization_schedule': amortization_df,
            'annual_costs': self.annual_costs,
            'annual_revenues': self.annual_revenues,
            'annual_cash_flows': self.annual_cash_flows,
            'cumulative_cash_flows': self.cumulative_cash_flows
        }
        
        self._print_summary(results)
        
        return results
    
    def _print_summary(self, results: Dict) -> None:
        """Print executive summary of financial analysis."""
        print(f"\n{'='*60}")
        print("30-YEAR FINANCIAL SUMMARY")
        print(f"{'='*60}")
        print(f"\nTotal Investment Required (Years 1-10): "
              f"${results['development_phases']['total_10year']:,.2f}")
        print(f"Total Operating Costs (30 years): "
              f"${results['total_30year_costs']:,.2f}")
        print(f"Total Revenue Generated (30 years): "
              f"${results['total_30year_revenue']:,.2f}")
        print(f"Cumulative Operating Margin: "
              f"${results['cumulative_operating_margin']:,.2f}")
        print(f"\nNet Present Value (at {self.discount_rate:.1%}): "
              f"${results['npv']:,.2f}")
        print(f"Internal Rate of Return: {results['irr']:.2f}%")
        print(f"Break-Even Year: Year {results['break_even_year']}")
        print(f"Benefit-Cost Ratio: {results['benefit_cost_ratio']:.1f} to 1")
        
        print(f"\n{'='*60}")
        print("AMORTIZATION SUMMARY")
        print(f"{'='*60}")
        amort_df = results['amortization_schedule']
        total_amortization = amort_df['Annual_Amortization'].sum()
        total_tax_benefit = amort_df['Tax_Benefit'].sum()
        print(f"Total Capitalized Development: ${total_amortization:,.2f}")
        print(f"Amortization Period: Years 6-20")
        print(f"Annual Amortization Expense: "
              f"${amort_df.loc[5, 'Annual_Amortization']:,.2f}")
        print(f"Total Tax Benefits: ${total_tax_benefit:,.2f}")


# Execute the complete financial model
if __name__ == "__main__":
    model = IHEPFinancialModel(discount_rate=0.10)
    results = model.run_complete_analysis()
    
    # Export results to CSV for further analysis
    pd.DataFrame({
        'Year': range(1, 31),
        'Annual_Costs': results['annual_costs'],
        'Annual_Revenue': results['annual_revenues'],
        'Annual_Cash_Flow': results['annual_cash_flows'],
        'Cumulative_Cash_Flow': results['cumulative_cash_flows']
    }).to_csv('ihep_30year_financial_model.csv', index=False)
    
    print("\n\nFinancial model results exported to 'ihep_30year_financial_model.csv'")