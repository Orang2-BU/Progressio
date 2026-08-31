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

    # A prerequisite counts as satisfied at this mastery, matching the bar the
    # diagnostic uses to decide whether a skill is weak.
    PREREQUISITE_THRESHOLD = 70.0
    MASTERED_THRESHOLD = 85.0

    @classmethod
    def get_learning_path(cls, user, career_track=None):
        """
        Traverses skill graph and classifies each skill's status:
        - 'mastered': mastery >= 85
        - 'in_progress': mastery > 0
        - 'available': all prerequisites mastered / met
        - 'locked': one or more prerequisites unmet

        Pass ``career_track`` to scope the graph to one track. Without it every
        track in the database is returned, which is only meaningful while a
        single track exists.
        """
        all_skills = Skill.objects.select_related('competency').prefetch_related(
            'prerequisites__required_skill'
        ).all()
        if career_track is not None:
            all_skills = all_skills.filter(competency__career_track=career_track)

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

    @classmethod
    def get_roadmap(cls, user, target_skill=None, target_competency=None, career_track=None):
        """
        Computes the ordered route from where the learner is now to a target
        they chose.

        ``get_learning_path`` answers "what does the whole map look like".
        This answers "what is left for me to reach that", which is a different
        question: it walks the prerequisite graph backwards from the target,
        stops descending wherever a skill is already held, and returns only the
        remaining work in an order that respects prerequisites.

        Exactly one target must be given.
        """
        targets = [target_skill, target_competency, career_track]
        if sum(item is not None for item in targets) != 1:
            raise ValueError('Provide exactly one of target_skill, target_competency, or career_track.')

        if target_skill is not None:
            goal_skills = [target_skill]
            target_info = {
                'type': 'skill',
                'slug': target_skill.slug,
                'title': target_skill.title,
            }
        elif target_competency is not None:
            goal_skills = list(target_competency.skills.all())
            target_info = {
                'type': 'competency',
                'slug': target_competency.slug,
                'title': target_competency.title,
            }
        else:
            goal_skills = list(Skill.objects.filter(competency__career_track=career_track))
            target_info = {
                'type': 'career_track',
                'slug': career_track.slug,
                'title': career_track.title,
            }

        if not goal_skills:
            raise ValueError(f"Target '{target_info['slug']}' contains no skills.")

        graph = cls._prerequisite_graph(goal_skills[0].competency.career_track_id)
        mastery = {
            progress.skill_id: progress.mastery
            for progress in SkillProgress.objects.filter(user=user)
        }

        required, satisfied = cls._walk_back(goal_skills, graph, mastery)
        ordered = cls._topological_order(required, graph)

        steps = []
        for position, skill in enumerate(ordered, start=1):
            steps.append({
                'order': position,
                'skill_id': skill.id,
                'skill_slug': skill.slug,
                'skill_title': skill.title,
                'competency_title': skill.competency.title,
                'difficulty': skill.difficulty,
                'estimated_minutes': skill.estimated_learning_minutes,
                'mastery': mastery.get(skill.id, 0.0),
                'prerequisites': sorted(item.slug for item in graph[skill.id]['requires']),
                'is_target': skill.id in {item.id for item in goal_skills},
            })

        remaining_minutes = sum(step['estimated_minutes'] for step in steps)
        return {
            'target': target_info,
            'total_steps': len(steps),
            'remaining_minutes': remaining_minutes,
            'remaining_hours': round(remaining_minutes / 60.0, 1),
            'already_satisfied': [
                {
                    'skill_slug': skill.slug,
                    'skill_title': skill.title,
                    'mastery': mastery.get(skill.id, 0.0),
                }
                for skill in sorted(satisfied.values(), key=lambda item: item.slug)
            ],
            'steps': steps,
        }

    @classmethod
    def _prerequisite_graph(cls, career_track_id):
        """Adjacency map of one track's skill graph, keyed by skill ID."""
        skills = Skill.objects.filter(
            competency__career_track_id=career_track_id
        ).select_related('competency').prefetch_related('prerequisites__required_skill')

        graph = {}
        for skill in skills:
            graph[skill.id] = {
                'skill': skill,
                'requires': [item.required_skill for item in skill.prerequisites.all()],
            }
        return graph

    @classmethod
    def _walk_back(cls, goal_skills, graph, mastery):
        """
        Collect what still has to be learned to reach the goals.

        A skill already held at the prerequisite bar is treated as satisfied and
        its own prerequisites are not revisited — holding a skill implies its
        foundations are good enough for this route.
        """
        required = {}
        satisfied = {}
        active = set()

        def visit(skill):
            if skill.id in required or skill.id in satisfied:
                return
            if skill.id in active:
                raise ValueError(
                    f"Prerequisite cycle detected at skill '{skill.slug}'. "
                    'The curriculum validator forbids cycles, so this indicates '
                    'hand-edited data in the database.'
                )
            if mastery.get(skill.id, 0.0) >= cls.PREREQUISITE_THRESHOLD:
                satisfied[skill.id] = skill
                return

            active.add(skill.id)
            for parent in graph.get(skill.id, {}).get('requires', []):
                visit(parent)
            active.discard(skill.id)
            required[skill.id] = skill

        for goal in goal_skills:
            visit(goal)
        return required, satisfied

    @classmethod
    def _topological_order(cls, required, graph):
        """
        Order the remaining skills so every prerequisite comes before the skill
        that needs it. Ties break on competency order then title, so the same
        input always produces the same route.
        """
        placed = {}
        ordered = []

        def depth(skill_id):
            if skill_id in placed:
                return placed[skill_id]
            parents = [
                parent.id
                for parent in graph.get(skill_id, {}).get('requires', [])
                if parent.id in required
            ]
            placed[skill_id] = 1 + max((depth(parent) for parent in parents), default=0)
            return placed[skill_id]

        for skill_id in required:
            depth(skill_id)

        for skill_id in sorted(
            required,
            key=lambda item: (
                placed[item],
                required[item].competency.order,
                required[item].title,
            ),
        ):
            ordered.append(required[skill_id])
        return ordered
