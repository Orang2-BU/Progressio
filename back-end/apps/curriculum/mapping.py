"""
Translation between the curriculum vocabulary and the Django domain vocabulary.

The curriculum is written for humans and for review; the models were written for
the runtime. Where the two disagree, the mapping lives here rather than being
spread through the importer.
"""
from apps.assessments.models import Assessment
from apps.careers.models import CareerTrack
from apps.learning.models import Lesson
from apps.skills.models import Skill

# Curriculum uses title case, the models use lowercase enum values.
DIFFICULTY = {
    'Beginner': Skill.Difficulty.BEGINNER,
    'Intermediate': Skill.Difficulty.INTERMEDIATE,
    'Advanced': Skill.Difficulty.ADVANCED,
}

TRACK_DIFFICULTY = {
    'Beginner': CareerTrack.Difficulty.BEGINNER,
    'Intermediate': CareerTrack.Difficulty.INTERMEDIATE,
    'Advanced': CareerTrack.Difficulty.ADVANCED,
}

# A curriculum resource is a pointer to external material. The closest runtime
# concept is a Lesson whose content lives at content_url.
RESOURCE_CONTENT_TYPE = {
    'documentation': Lesson.ContentType.READING,
    'standard': Lesson.ContentType.READING,
    'reference': Lesson.ContentType.READING,
    'tutorial': Lesson.ContentType.ARTICLE,
    'article': Lesson.ContentType.ARTICLE,
    'exercise': Lesson.ContentType.EXERCISE,
}

# Study order within a skill: read the primary source first, keep practice last.
RESOURCE_ROLE_ORDER = {
    'primary': 0,
    'reference': 1,
    'practice': 2,
    'supplementary': 3,
}

# The curriculum distinguishes five assessment shapes; the runtime grades three.
# Everything that is not a fixed-answer quiz needs a judgement, so it routes to
# the AI evaluation mode.
ASSESSMENT_TYPE = {
    'quiz': (Assessment.AssessmentType.QUIZ, Assessment.EvaluationMode.RULES),
    'coding-challenge': (Assessment.AssessmentType.CHALLENGE, Assessment.EvaluationMode.AI),
    'debugging-task': (Assessment.AssessmentType.CHALLENGE, Assessment.EvaluationMode.AI),
    'practical-exercise': (Assessment.AssessmentType.PROJECT, Assessment.EvaluationMode.AI),
    'mini-project': (Assessment.AssessmentType.PROJECT, Assessment.EvaluationMode.AI),
}


def difficulty(value, table=DIFFICULTY):
    try:
        return table[value]
    except KeyError:
        raise ValueError(f"Unmapped curriculum difficulty '{value}'.") from None


def content_type(resource_type):
    try:
        return RESOURCE_CONTENT_TYPE[resource_type]
    except KeyError:
        raise ValueError(f"Unmapped curriculum resource type '{resource_type}'.") from None


def role_order(role):
    try:
        return RESOURCE_ROLE_ORDER[role]
    except KeyError:
        raise ValueError(f"Unmapped curriculum resource role '{role}'.") from None


def assessment_type(value):
    try:
        return ASSESSMENT_TYPE[value]
    except KeyError:
        raise ValueError(f"Unmapped curriculum assessment type '{value}'.") from None
