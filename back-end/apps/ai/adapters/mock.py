from .base import BaseAIAdapter


class MockAIAdapter(BaseAIAdapter):
    """
    Intelligent simulation AI adapter for offline development and automated testing.
    Produces deterministic, structured, high-quality responses without requiring API keys.
    """

    def analyze_skill_gap(self, user_profile, target_career_track, user_skills, required_skills):
        user_skill_ids = {s['id'] for s in user_skills if s.get('mastery', 0) >= 70.0}

        missing_skills = []
        acquired_skills = []

        for req in required_skills:
            if req['id'] in user_skill_ids:
                acquired_skills.append(req)
            else:
                user_prog = next((s for s in user_skills if s['id'] == req['id']), None)
                current_mastery = user_prog['mastery'] if user_prog else 0.0
                missing_skills.append({
                    'id': req['id'],
                    'title': req['title'],
                    'difficulty': req.get('difficulty', 'beginner'),
                    'current_mastery': current_mastery,
                    'estimated_minutes': req.get('estimated_learning_minutes', 60),
                })

        match_percentage = round((len(acquired_skills) / max(len(required_skills), 1)) * 100.0, 1)

        summary = (
            f"You have acquired {len(acquired_skills)} out of {len(required_skills)} required skills "
            f"({match_percentage}% match) for the {target_career_track['title']} pathway."
        )

        return {
            'target_career_track': target_career_track['title'],
            'match_percentage': match_percentage,
            'summary': summary,
            'missing_skills': missing_skills,
            'acquired_skills': acquired_skills,
            'recommended_priority_skill': missing_skills[0]['title'] if missing_skills else None,
            'ai_insights': [
                "Focus on foundational skills with prerequisites before moving to intermediate topics.",
                "Completing practical projects will accelerate mastery by up to 40%."
            ]
        }

    def generate_learning_recommendations(self, user_profile, current_progress, weak_areas):
        recommendations = []

        if weak_areas:
            for weak in weak_areas[:3]:
                recommendations.append({
                    'type': 'reinforce',
                    'title': f"Reinforce: {weak['title']}",
                    'reason': f"Your current mastery is {weak.get('mastery', 0)}%. Reviewing exercises will boost confidence.",
                    'action_url': f"/api/v1/skills/{weak['id']}/lessons"
                })
        else:
            recommendations.append({
                'type': 'explore',
                'title': "Explore Next Competency",
                'reason': "You are on track with your foundational skills. Proceed to the next career milestone.",
                'action_url': "/api/v1/learning-path"
            })

        return {
            'student_name': user_profile.get('username', 'Learner'),
            'focus_area': weak_areas[0]['title'] if weak_areas else 'Next Milestone',
            'recommendations': recommendations,
            'estimated_weekly_study_hours': 4.5
        }

    def evaluate_submission(self, assessment, submission_content):
        # Intelligent evaluation rule-engine
        answers = submission_content.get('answers', {})
        answers_count = len(answers) if isinstance(answers, dict) else 0

        score = min(float(assessment.passing_score + (answers_count * 5)), float(assessment.max_score))
        is_passed = score >= assessment.passing_score

        feedback = (
            f"AI Evaluation: Good attempt! The submission scored {score}/{assessment.max_score}. "
            "Code structure and conceptual understanding meet the expected criteria."
            if is_passed else
            f"AI Evaluation: Score {score}/{assessment.max_score}. Review key prerequisites before retrying."
        )

        return {
            'score': score,
            'is_passed': is_passed,
            'feedback': feedback,
            'strengths': ["Accurate syntax usage", "Logical problem breakdown"],
            'areas_for_improvement': ["Add automated unit tests", "Optimize error handling"]
        }
