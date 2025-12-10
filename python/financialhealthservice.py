# financialhealthservice.py
class FinancialHealthEngine:
    def calculate_stability_score(self, participant_id):
        income_stability = self.assess_income_streams()
        expense_volatility = self.analyze_spending_patterns()
        benefits_optimization = self.check_unclaimed_benefits()
        debt_burden = self.calculate_debt_to_income()
        
        return weighted_score(
            income_stability * 0.30,
            expense_volatility * 0.20,
            benefits_optimization * 0.25,
            debt_burden * 0.25
        )
    
    def generate_income_opportunities(self, participant_profile):
        eligible_gigs = self.match_skills_to_tasks()
        training_programs = self.recommend_career_paths()
        benefits_to_claim = self.identify_unclaimed_benefits()
        
        return prioritized_action_plan(
            immediate_income=eligible_gigs,
            medium_term=training_programs,
            long_term=benefits_to_claim
        )
