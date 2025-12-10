# opportunitymatcher.py
class OpportunityMatchingEngine:
    def match_participant_to_income(self, participant_profile):
        skills = self.extract_skills(participant_profile)
        availability = self.get_availability(participant_profile)
        interests = self.get_preferences(participant_profile)
        location = self.get_location(participant_profile)
        
        # ML-powered matching
        gig_matches = self.rank_gig_opportunities(skills, availability)
        navigator_fit = self.assess_navigator_potential(profile)
        research_eligibility = self.check_study_criteria(profile)
        training_readiness = self.evaluate_career_programs(skills, interests)
        
        return {
            'immediate_opportunities': gig_matches[:5],
            'career_pathways': training_readiness,
            'research_studies': research_eligibility,
            'navigator_track': navigator_fit
        }
