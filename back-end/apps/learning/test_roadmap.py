"""
Roadmap tests, run against the real Backend Engineering curriculum package so
the route reflects the graph the product actually ships.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.curriculum.importer import import_track
from apps.skills.models import Skill

from .models import SkillProgress
from .services import LearningPathService

User = get_user_model()


class RoadmapTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_track('backend-engineering')
        cls.track = CareerTrack.objects.get(slug='backend-engineering')

    def setUp(self):
        self.user = User.objects.create_user(
            username='student', email='student@example.com', password='pw'
        )

    def master(self, slug, mastery=90.0):
        SkillProgress.objects.update_or_create(
            user=self.user,
            skill=Skill.objects.get(slug=slug),
            defaults={'mastery': mastery},
        )

    def slugs(self, roadmap):
        return [step['skill_slug'] for step in roadmap['steps']]


class RoadmapRouteTests(RoadmapTestCase):
    def test_route_to_a_skill_includes_every_transitive_prerequisite(self):
        target = Skill.objects.get(slug='api-input-validation')

        roadmap = LearningPathService.get_roadmap(self.user, target_skill=target)

        self.assertEqual(
            set(self.slugs(roadmap)),
            {
                'program-control-flow',
                'functions-and-modules',
                'client-server-model',
                'http-messages-and-semantics',
                'api-contract-design',
                'api-input-validation',
            },
        )
        # git-change-workflow is in the track but nothing on this route needs it.
        self.assertNotIn('git-change-workflow', self.slugs(roadmap))

    def test_prerequisites_always_come_before_the_skill_that_needs_them(self):
        target = Skill.objects.get(slug='api-input-validation')

        order = self.slugs(LearningPathService.get_roadmap(self.user, target_skill=target))

        self.assertLess(order.index('program-control-flow'), order.index('functions-and-modules'))
        self.assertLess(order.index('client-server-model'), order.index('http-messages-and-semantics'))
        self.assertLess(order.index('functions-and-modules'), order.index('api-contract-design'))
        self.assertLess(order.index('http-messages-and-semantics'), order.index('api-contract-design'))
        self.assertLess(order.index('api-contract-design'), order.index('api-input-validation'))

    def test_held_skills_drop_out_of_the_route(self):
        self.master('program-control-flow')
        self.master('client-server-model')
        target = Skill.objects.get(slug='api-input-validation')

        roadmap = LearningPathService.get_roadmap(self.user, target_skill=target)

        self.assertNotIn('program-control-flow', self.slugs(roadmap))
        self.assertNotIn('client-server-model', self.slugs(roadmap))
        self.assertEqual(
            {item['skill_slug'] for item in roadmap['already_satisfied']},
            {'program-control-flow', 'client-server-model'},
        )

    def test_remaining_effort_shrinks_as_skills_are_held(self):
        target = Skill.objects.get(slug='api-input-validation')
        before = LearningPathService.get_roadmap(self.user, target_skill=target)

        self.master('program-control-flow')
        after = LearningPathService.get_roadmap(self.user, target_skill=target)

        # program-control-flow is 300 minutes in the curriculum.
        self.assertEqual(before['remaining_minutes'] - after['remaining_minutes'], 300)
        self.assertEqual(before['total_steps'] - after['total_steps'], 1)

    def test_partial_mastery_below_the_bar_still_counts_as_remaining_work(self):
        self.master('program-control-flow', mastery=69.9)
        target = Skill.objects.get(slug='api-input-validation')

        roadmap = LearningPathService.get_roadmap(self.user, target_skill=target)

        self.assertIn('program-control-flow', self.slugs(roadmap))

    def test_route_to_a_competency_covers_all_of_its_skills(self):
        competency = Competency.objects.get(slug='api-development')

        roadmap = LearningPathService.get_roadmap(self.user, target_competency=competency)

        self.assertEqual(roadmap['target']['type'], 'competency')
        self.assertTrue({'api-contract-design', 'api-input-validation'} <= set(self.slugs(roadmap)))

    def test_route_to_a_track_covers_every_skill_in_it(self):
        roadmap = LearningPathService.get_roadmap(self.user, career_track=self.track)

        self.assertEqual(len(roadmap['steps']), 7)
        self.assertEqual(roadmap['remaining_minutes'], 2340)

    def test_completed_target_produces_an_empty_route(self):
        for slug in Skill.objects.values_list('slug', flat=True):
            self.master(slug)
        target = Skill.objects.get(slug='api-input-validation')

        roadmap = LearningPathService.get_roadmap(self.user, target_skill=target)

        self.assertEqual(roadmap['steps'], [])
        self.assertEqual(roadmap['remaining_minutes'], 0)

    def test_exactly_one_target_is_required(self):
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            LearningPathService.get_roadmap(self.user)
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            LearningPathService.get_roadmap(
                self.user,
                target_skill=Skill.objects.get(slug='api-contract-design'),
                career_track=self.track,
            )

    def test_target_step_is_flagged(self):
        target = Skill.objects.get(slug='api-contract-design')

        roadmap = LearningPathService.get_roadmap(self.user, target_skill=target)

        flagged = [step['skill_slug'] for step in roadmap['steps'] if step['is_target']]
        self.assertEqual(flagged, ['api-contract-design'])


class LearningPathScopingTests(RoadmapTestCase):
    def test_learning_path_can_be_scoped_to_one_track(self):
        other = CareerTrack.objects.create(slug='data-science', title='Data Science')
        competency = Competency.objects.create(
            career_track=other, slug='ds-foundations', title='DS Foundations'
        )
        Skill.objects.create(competency=competency, slug='pandas', title='Pandas')

        scoped = LearningPathService.get_learning_path(self.user, career_track=self.track)
        unscoped = LearningPathService.get_learning_path(self.user)

        self.assertNotIn('pandas', [node['skill_slug'] for node in scoped])
        self.assertIn('pandas', [node['skill_slug'] for node in unscoped])


class RoadmapEndpointTests(RoadmapTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_endpoint_returns_the_route(self):
        response = self.client.get(reverse('roadmap'), {'skill': 'api-contract-design'})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['target']['slug'], 'api-contract-design')
        self.assertEqual(body['total_steps'], 5)
        self.assertGreater(body['remaining_hours'], 0)

    def test_endpoint_requires_authentication(self):
        self.client.logout()

        response = self.client.get(reverse('roadmap'), {'skill': 'api-contract-design'})

        self.assertEqual(response.status_code, 401)

    def test_endpoint_rejects_zero_or_multiple_targets(self):
        self.assertEqual(self.client.get(reverse('roadmap')).status_code, 400)
        self.assertEqual(
            self.client.get(
                reverse('roadmap'),
                {'skill': 'api-contract-design', 'career_track': 'backend-engineering'},
            ).status_code,
            400,
        )

    def test_endpoint_404s_on_an_unknown_target(self):
        response = self.client.get(reverse('roadmap'), {'skill': 'quantum-computing'})

        self.assertEqual(response.status_code, 404)
