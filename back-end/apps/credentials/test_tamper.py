"""The credential's integrity check must actually detect edits to the record."""
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.assessments.models import Assessment
from apps.assessments.services import AssessmentEvaluationService
from apps.blockchain.services import BlockchainService
from apps.competencies.models import Competency
from apps.credentials.services import CredentialService
from apps.curriculum.importer import import_track
from apps.learning.models import Lesson
from apps.learning.services import ProgressService
from apps.skills.models import Skill

User = get_user_model()


class CredentialIntegrityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_track('backend-engineering')

    def setUp(self):
        self.user = User.objects.create_user(
            username='student', email='student@example.com', password='pw'
        )
        self.competency = Competency.objects.get(slug='api-development')

        for skill in Skill.objects.filter(competency=self.competency):
            for lesson in Lesson.objects.filter(skill=skill):
                ProgressService.complete_lesson(self.user, lesson)
            assessment = Assessment.objects.get(skill=skill)
            evidence = ' '.join(
                item['criterion'] for item in assessment.grading_config['rubric']
            )
            AssessmentEvaluationService.submit_and_evaluate(
                self.user, assessment, {'code': evidence, 'readme': evidence}
            )

        self.credential = CredentialService.issue_credential(self.user, self.competency)

    def test_credential_is_issued_and_intact(self):
        self.assertEqual(self.credential.status, 'issued')
        self.assertTrue(BlockchainService.verify_credential_integrity(self.credential)[0])

    def test_credential_pins_the_curriculum_it_was_graded_against(self):
        metadata = self.credential.metadata
        self.assertEqual(metadata['curriculum_version'], '0.1.0')
        self.assertEqual(metadata['curriculum_schema_version'], 1)
        self.assertEqual(metadata['competency_id'], 'api-development')
        self.assertTrue(metadata['observable_behaviors'])

    def test_editing_the_score_in_the_database_breaks_integrity(self):
        self.credential.score = self.credential.score - 20.0
        self.credential.save(update_fields=['score'])

        self.assertFalse(BlockchainService.verify_credential_integrity(self.credential)[0])

    def test_editing_the_pinned_curriculum_version_breaks_integrity(self):
        self.credential.metadata['curriculum_version'] = '9.9.9'
        self.credential.save(update_fields=['metadata'])

        self.assertFalse(BlockchainService.verify_credential_integrity(self.credential)[0])

    def test_revoking_a_credential_makes_it_invalid(self):
        CredentialService.revoke_credential(self.credential.id, reason='test')
        self.credential.refresh_from_db()

        self.assertEqual(self.credential.status, 'revoked')
        self.assertFalse(self.credential.is_valid)
