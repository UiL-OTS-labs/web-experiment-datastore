from django.test import TestCase
from django.utils import timezone

import uuid

# Create your tests here.
from .models import Experiment, ParticipantSession, TargetGroup
from main.models import User


class ParticipantSessionTests(TestCase):
    """
    Test the basic assumptions of a ParticipantSession.
    """

    @classmethod
    def setUpTestData(cls):
        access_id = uuid.uuid4()
        cls.experiment = Experiment.objects.create(
            access_id=access_id
        )

    def setUp(self) -> None:
        self.default_group = self.experiment.targetgroup_set.create(
            name='A',
            completion_target=2
        )

    def test_participant_sessions_subject_id(self):
        session1 = ParticipantSession.objects.create(
            experiment=self.experiment, group=self.default_group
        )
        session2 = ParticipantSession.objects.create(
            experiment=self.experiment, group=self.default_group
        )
        self.assertEqual(session1.subject_id, 1)
        self.assertEqual(session2.subject_id, 2)
