from django.test import TestCase, modify_settings
from django.urls import reverse
from unittest.mock import patch, ANY

from main.models import User
from auditlog.enums import Event

import random
import uuid

# Create your tests here.
from .models import Experiment, ParticipantSession, TargetGroup, DataPoint


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
            choice = random.choice([1, 2, 3])
            if choice in [1, 2]: # add a session
                ParticipantSession.objects.create(
                    experiment=self.experiment1,
                    group=self.experiment1.targetgroup_set.first()
                )
            else:
                sessions = ParticipantSession.objects.all()
                sessions.order_by('?').first().delete()

        ids = [session.subject_id for session in ParticipantSession.objects.all()]
        # test whether the list of id's is identical to the unique set of id's
        self.assertEqual(sorted(ids), sorted(set(ids)))

        # cleanup
        ParticipantSession.objects.all().delete()


class TestDeleteData(TestCase):
    databases = '__all__'  # required for login because of auditlog

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='test', password='test')
        cls.exp = Experiment.objects.create(access_id=uuid.uuid4())
        cls.exp.users.add(cls.user)

    def test_data_point_delete_with_session(self):
        group = self.exp.targetgroup_set.create(name='A', completion_target=2)
        session = self.exp.participantsession_set.create(group=group)
        dp = DataPoint.objects.create(
            experiment=self.exp,
            session=session
        )

        self.client.force_login(self.user)
        self.client.delete(reverse('experiments:delete_datapoint', args=[self.exp.pk, dp.pk]))
        self.assertEqual(group.participantsession_set.count(), 0)


class TestAuditLog(TestCase):
    databases = '__all__'  # required for login because of auditlog

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='test', password='test')

    @patch('experiments.views.log')
    def test_delete_experiment(self, log):
        exp = Experiment.objects.create(access_id=uuid.uuid4())
        exp.users.add(self.user)
        self.client.force_login(self.user)
        self.client.post(reverse('experiments:delete_experiment', args=[exp.pk]))
        self.assertEqual(self.user.experiment_set.count(), 0)
        self.assertEqual(log.called, True)
        log.assert_called_with(Event.DELETE_DATA, ANY, self.user, ANY)
