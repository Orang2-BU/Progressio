"""Report whether local persistent demo dependencies and catalog are ready."""
import os

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from apps.assessments.models import Assessment, DiagnosticQuestion
from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.skills.models import Skill


class Command(BaseCommand):
    help = 'Check local demo database and minimum catalog without contacting external providers.'

    def handle(self, *args, **options):
        tracks = CareerTrack.objects.filter(is_active=True).count()
        skills = Skill.objects.filter(competency__career_track__is_active=True).count()
        assessments = Assessment.objects.filter(skill__competency__career_track__is_active=True).count()
        diagnostics = DiagnosticQuestion.objects.filter(is_active=True).count()
        two_skill_competencies = Competency.objects.filter(
            career_track__is_active=True
        ).annotate(skill_count=Count('skills')).filter(skill_count__gte=2).count()
        provider = os.getenv('AI_PROVIDER', 'mock').strip().lower() or 'unset'
        model = os.getenv('AI_MODEL', '').strip() or ('mock' if provider == 'mock' else 'default')
        self.stdout.write(f'Profile: {os.getenv("APP_ENV", "unset")}')
        self.stdout.write(f'AI provider/model: {provider}/{model}')
        self.stdout.write(
            f'Catalog: {tracks} tracks, {skills} skills, {assessments} assessments, '
            f'{diagnostics} diagnostic questions, {two_skill_competencies} two-skill competencies.'
        )
        if not tracks or skills < 2 or not assessments or not diagnostics or not two_skill_competencies:
            raise CommandError('Demo catalog is incomplete; import and review the seed output before starting the demo.')
        self.stdout.write(self.style.SUCCESS('Demo preflight passed.'))
