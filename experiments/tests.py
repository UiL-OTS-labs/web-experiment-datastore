from django.test import TestCase
from django.utils import timezone

import random
import uuid

# Create your tests here.
from .models import Experiment, ParticipantSession, TargetGroup
from main.models import User


class ParticipantSessionSubjectIdTests(TestCase):
    """
    Test the basic assumptions of subject id's in ParticipantSession.
    """

    @classmethod
    def setUpTestData(cls):
        cls.experiment1 = Experiment.objects.create(
            access_id=uuid.uuid4()
        )
        cls.experiment2 = Experiment.objects.create(
            access_id=uuid.uuid4()
        )

    def test_participant_session_subject_id(self):
        """
        Test that subject_id's start at 1 for each experiment
        and are updated incrementally.
        """
        session_e1_s1 = ParticipantSession.objects.create(
            experiment=self.experiment1,
            group=self.experiment1.targetgroup_set.first()
        )
        session_e1_s2 = ParticipantSession.objects.create(
            experiment=self.experiment1,
            group=self.experiment1.targetgroup_set.first()
        )
        session_e2_s1 = ParticipantSession.objects.create(
            experiment=self.experiment2,
            group=self.experiment2.targetgroup_set.first()
        )
        session_e2_s2 = ParticipantSession.objects.create(
            experiment=self.experiment2,
            group = self.experiment2.targetgroup_set.first()
        )

        self.assertEqual(session_e1_s1.subject_id, 1)
        self.assertEqual(session_e1_s2.subject_id, 2)
        self.assertEqual(session_e2_s1.subject_id, 1)
        self.assertEqual(session_e2_s2.subject_id, 2)

        ParticipantSession.objects.all().delete()


    def test_participant_session_unique_subject_id(self):
        """
        Test that an experiment keeps unique session_id's
        when adding and removing sessions from an experiment.
        """

        # Fill with a few items to avoid to deal with a .delete() on an empty set.
        for _ in range(10):
            ParticipantSession.objects.create(
                experiment=self.experiment1,
                group=self.experiment1.targetgroup_set.first()
            )

        for _ in range(100):
            choice = random.choice([1,2,3])
            if choice in [1,2]: # add a session
                ParticipantSession.objects.create(experiment=self.experiment1)
            else:
                sessions = ParticipantSession.objects.all()
                sessions.order_by('?').first().delete()

        ids = [session.subject_id for session in ParticipantSession.objects.all()]
        # test whether the list of id's is identical to the unique set of id's
        self.assertEqual(sorted(ids), sorted(set(ids)))

        # cleanup
        ParticipantSession.objects.all().delete()
