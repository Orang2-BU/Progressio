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
        # Deterministic offline rubric. This never trusts a client-supplied score.
        evidence_parts = []
        for key in ('code', 'repository_summary', 'readme', 'test_output'):
            value = submission_content.get(key, '')
            if isinstance(value, str):
                evidence_parts.append(value)
        files = submission_content.get('files', {})
        if isinstance(files, dict):
            evidence_parts.extend(str(value) for value in files.values())

        evidence = '\n'.join(evidence_parts)
        lowered = evidence.casefold()
        score = 0.0
        if len(evidence.strip()) >= 80:
            score += 25.0
        if len(evidence.strip()) >= 300:
            score += 15.0
        if any(token in lowered for token in ('test_', 'pytest', 'unittest', 'assert ')):
            score += 20.0
        if any(token in lowered for token in ('jwt', 'authentication', 'authorization', 'permission')):
            score += 20.0
        if any(token in lowered for token in ('try:', 'except ', 'error', 'status_code')):
            score += 10.0
        if any(token in lowered for token in ('readme', 'documentation', 'usage')):
            score += 10.0
        score = min(score, float(assessment.max_score))
        is_passed = score >= assessment.passing_score

        feedback = (
            f"Mock evaluation: the submitted evidence scored {score}/{assessment.max_score}. "
            "The offline rubric found sufficient implementation and validation evidence."
            if is_passed else
            f"Mock evaluation: score {score}/{assessment.max_score}. Add concrete code, automated tests, "
            "security handling, and documentation before retrying."
        )

        return {
            'score': score,
            'is_passed': is_passed,
            'feedback': feedback,
            'strengths': ["Submitted evidence was evaluated deterministically"],
            'areas_for_improvement': ["Add automated tests", "Document security and error handling"]
        }
