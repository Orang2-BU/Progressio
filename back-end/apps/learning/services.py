from django.utils import timezone
from django.db.models import Avg, Sum
from .models import Lesson, LessonCompletion, SkillProgress, CompetencyProgress
from apps.skills.models import Skill, SkillPrerequisite
from apps.competencies.models import Competency


class ProgressService:
    """
    Handles business logic for XP tracking, mastery recalculation, and domain events.
    """

    XP_PER_LESSON = 50
    XP_PER_ASSESSMENT = 100

    @classmethod
    def complete_lesson(cls, user, lesson):
        """
        Event: LessonCompleted
        1. Marks lesson completed for user.
        2. Awards +50 XP to SkillProgress.
        3. Recalculates skill mastery based on completed lessons ratio.
        4. Updates competency progress.
        """
        completion, created = LessonCompletion.objects.get_or_create(
            user=user,
            lesson=lesson
        )

        xp_earned = 0
        if created:
            xp_earned = cls.XP_PER_LESSON
            skill = lesson.skill

            skill_progress, _ = SkillProgress.objects.get_or_create(
                user=user,
                skill=skill
            )
            skill_progress.xp += xp_earned

            # Calculate mastery from lessons completed
            total_lessons = skill.lessons.count()
            completed_lessons = LessonCompletion.objects.filter(
                user=user,
                lesson__skill=skill
            ).count()

            if total_lessons > 0:
                # Lessons provide up to 70% mastery; remaining 30% requires passing assessment
                lessons_mastery = (completed_lessons / total_lessons) * 70.0
                skill_progress.mastery = max(skill_progress.mastery, round(lessons_mastery, 1))

            skill_progress.save()
            cls.recalculate_competency_progress(user, skill.competency)

        return completion, created, xp_earned

    @classmethod
    def record_assessment_passed(cls, user, skill, score):
        """
        Event: AssessmentPassed
        1. Updates SkillProgress mastery, XP (+100 XP), confidence, and last_assessed_at.
        2. Recalculates CompetencyProgress.
        """
        skill_progress, _ = SkillProgress.objects.get_or_create(
            user=user,
            skill=skill
        )
        skill_progress.xp += cls.XP_PER_ASSESSMENT
        # Assessment score seals mastery up to 100%
        skill_progress.mastery = min(100.0, max(skill_progress.mastery, round(score, 1)))
        skill_progress.confidence = round(min(1.0, max(0.0, score / 100.0)), 2)
        skill_progress.last_assessed_at = timezone.now()
        skill_progress.save()

        cls.recalculate_competency_progress(user, skill.competency)
        return skill_progress

    @classmethod
    def recalculate_competency_progress(cls, user, competency):
        """
        Calculates average mastery of all skills in a competency.
        """
        skills = competency.skills.all()
        if not skills.exists():
            return None

        progresses = SkillProgress.objects.filter(
            user=user,
            skill__in=skills
        )

        total_skills_count = skills.count()
        sum_mastery = sum(p.mastery for p in progresses)
        avg_score = round(sum_mastery / total_skills_count, 1) if total_skills_count > 0 else 0.0
        avg_confidence = round(sum(p.confidence for p in progresses) / total_skills_count, 2) if total_skills_count > 0 else 0.0

        comp_progress, _ = CompetencyProgress.objects.get_or_create(
            user=user,
            competency=competency
        )
        comp_progress.score = avg_score
        comp_progress.confidence = avg_confidence
        comp_progress.save()
        return comp_progress

    @classmethod
    def get_user_progress_overview(cls, user):
        """
        Returns an aggregated summary of the user's progress:
        - Total XP
        - Total completed lessons
        - Competency progresses
        - Skill progresses
        """
        total_xp = SkillProgress.objects.filter(user=user).aggregate(total=Sum('xp'))['total'] or 0
        total_completed_lessons = LessonCompletion.objects.filter(user=user).count()

        competency_progresses = CompetencyProgress.objects.filter(
            user=user
        ).select_related('competency', 'competency__career_track')

        skill_progresses = SkillProgress.objects.filter(
            user=user
        ).select_related('skill', 'skill__competency')

        return {
            'total_xp': total_xp,
            'completed_lessons_count': total_completed_lessons,
            'competency_progresses': competency_progresses,
            'skill_progresses': skill_progresses,
        }


class LearningPathService:
    """
    Computes personalized learning paths based on skill prerequisites graph.
    """

    @classmethod
    def get_learning_path(cls, user):
        """
        Traverses skill graph and classifies each skill's status:
        - 'mastered': mastery >= 85
        - 'in_progress': mastery > 0
        - 'available': all prerequisites mastered / met
        - 'locked': one or more prerequisites unmet
        """
        all_skills = Skill.objects.select_related('competency').prefetch_related(
            'prerequisites__required_skill'
        ).all()

        user_progress_map = {
            p.skill_id: p
            for p in SkillProgress.objects.filter(user=user)
        }

        path_nodes = []
        for skill in all_skills:
            progress = user_progress_map.get(skill.id)
            mastery = progress.mastery if progress else 0.0
            xp = progress.xp if progress else 0

            # Check prerequisites
            prereqs = skill.prerequisites.all()
            missing_prereqs = []
            for prereq in prereqs:
                req_skill = prereq.required_skill
                req_progress = user_progress_map.get(req_skill.id)
                if not req_progress or req_progress.mastery < 70.0:
                    missing_prereqs.append({
                        'id': req_skill.id,
                        'title': req_skill.title,
                        'current_mastery': req_progress.mastery if req_progress else 0.0
                    })

            if mastery >= 85.0:
                status = 'mastered'
            elif mastery > 0.0:
                status = 'in_progress'
            elif len(missing_prereqs) == 0:
                status = 'available'
            else:
                status = 'locked'

            path_nodes.append({
                'skill_id': skill.id,
                'skill_title': skill.title,
                'skill_slug': skill.slug,
                'competency_id': skill.competency_id,
                'competency_title': skill.competency.title,
                'difficulty': skill.difficulty,
                'status': status,
                'mastery': mastery,
                'xp': xp,
                'missing_prerequisites': missing_prereqs,
            })

        return path_nodes
