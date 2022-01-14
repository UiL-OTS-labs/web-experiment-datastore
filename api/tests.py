import json
import math
import random
import uuid

from django.urls import reverse
from rest_framework.test import APITestCase

from experiments.models import Experiment
from .views import ResultCodes


class TestExperimentApi(APITestCase):
    @classmethod
    def setUpTestData(cls):
        access_id = uuid.uuid4()
        cls.exp = Experiment.objects.create(access_id=access_id)

    def _upload(self):
        data = json.dumps({'key': 'value'})
        return self.client.post(reverse('api:upload', args=[self.exp.access_id]), data, content_type='text/plain')

    def test_upload_default_fail(self):
        response = self._upload()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['result'], ResultCodes.ERR_NOT_OPEN)

    def test_upload_ok(self):
        self.exp.state = Experiment.OPEN
        self.exp.approved = True
        self.exp.save()

        response = self._upload()
        self.assertEqual(response.status_code, 200)

        j = response.json()
        self.assertEqual(j['result'], ResultCodes.OK)
        self.assertEqual(j['message'], 'Upload successful')

        self.assertEqual(self.exp.datapoint_set.count(), 1)
        self.assertEqual(json.loads(self.exp.datapoint_set.first().data), {'key': 'value'})

    def test_upload_not_found(self):
        response = self.client.post(reverse('api:upload', args=[uuid.uuid4()]), {}, content_type='text/plain')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['result'], ResultCodes.ERR_UNKNOWN_ID)

    def test_upload_fail_when_not_approved(self):
        self.exp.state = Experiment.OPEN
        self.exp.approved = False
        self.exp.save()

        response = self._upload()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['result'], ResultCodes.ERR_NOT_OPEN)

    def test_get_metadata(self):
        self.exp.state = Experiment.OPEN
        self.exp.approved = True
        self.exp.save()

        response = self.client.get(reverse('api:metadata', args=[self.exp.access_id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['state'], 'Open')

    def test_get_metadata_not_found(self):
        response = self.client.get(reverse('api:metadata', args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['result'], ResultCodes.ERR_UNKNOWN_ID)


class TestTargetGroupAllocation(APITestCase):
    @classmethod
    def setUpTestData(cls):
        access_id = uuid.uuid4()
        cls.exp = Experiment.objects.create(
            access_id=access_id,
            state=Experiment.OPEN,
            approved=True
        )
        cls.group_a = cls.exp.targetgroup_set.create(name='A', completion_target=2)
        cls.group_b = cls.exp.targetgroup_set.create(name='B', completion_target=2)

    def test_create_participant(self):
        response = self.client.post(reverse('api:participant', args=[self.exp.access_id]))
        self.assertEqual(response.json()['group_name'], 'A')

    def test_create_participant_fail_without_groups(self):
        access_id = uuid.uuid4()
        self.exp = Experiment.objects.create(
            access_id=access_id,
            state=Experiment.OPEN,
            approved=True
        )
        response = self.client.post(reverse('api:participant', args=[self.exp.access_id]))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['result'], ResultCodes.ERR_GROUP_ASSIGN_FAIL)

    def test_upload_with_participant_ok(self):
        session = self.exp.participantsession_set.create(group=self.group_a)
        data = json.dumps({'key': 'value'})
        response = self.client.post(reverse('api:upload', args=[self.exp.access_id, session.uuid]),
                                    data,
                                    content_type='text/plain')
        self.assertEqual(response.status_code, 200)

        j = response.json()
        self.assertEqual(j['result'], 'OK')
        self.assertEqual(j['message'], 'Upload successful')

        self.assertEqual(self.exp.datapoint_set.count(), 1)
        dp = self.exp.datapoint_set.first()
        self.assertEqual(json.loads(dp.data), {'key': 'value'})
        self.assertEqual(dp.session, session)

    def test_create_participant_fail_when_not_open(self):
        self.exp.state = Experiment.CLOSED
        self.exp.save()
        response = self.client.post(reverse('api:participant', args=[self.exp.access_id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['result'], 'ERR_NOT_OPEN')

        self.exp.state = Experiment.OPEN
        self.exp.approved = False
        self.exp.save()
        response = self.client.post(reverse('api:participant', args=[self.exp.access_id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['result'], 'ERR_NOT_OPEN')

    def test_target_group_round_robin(self):
        response = self.client.post(reverse('api:participant', args=[self.exp.access_id]))
        self.assertEqual(response.json()['group_name'], 'A')
        response = self.client.post(reverse('api:participant', args=[self.exp.access_id]))
        self.assertEqual(response.json()['group_name'], 'B')
        response = self.client.post(reverse('api:participant', args=[self.exp.access_id]))
        self.assertEqual(response.json()['group_name'], 'A')

    def test_target_group_rebalance_on_complete(self):
        self.assertEqual(self.exp.assign_to_group(), self.group_a)
        p1 = self.exp.participantsession_set.create(group=self.group_a)
        p2 = self.exp.participantsession_set.create(group=self.group_a)  # noqa
        self.assertEqual(self.exp.assign_to_group(), self.group_b)
        p3 = self.exp.participantsession_set.create(group=self.group_b)  # noqa

        # round-robin should point next participant to A
        self.assertEqual(self.exp.assign_to_group(), self.group_a)
        # but when one of the A sessions is complete, we should assign to B because it has less sessiosn
        p1.complete()
        self.assertEqual(self.exp.assign_to_group(), self.group_b)

    def test_target_group_full(self):
        self.group_a.completed = self.group_a.completion_target
        self.group_a.save()

        group = self.exp.assign_to_group()
        # should assign to group B if group A is full
        self.assertEqual(group, self.group_b)

    def test_target_group_eventual_balance(self):
        # BB: not sure if this is actually necessary...
        rand = random.Random(0)

        N = 40
        completion_rate = 0.3
        total_runs = math.ceil(N / (completion_rate / 2))
        self.group_a.completion_target = N / 2
        self.group_b.completion_target = N / 2
        self.group_a.save()
        self.group_b.save()

        def _participant_session():
            group = self.exp.assign_to_group()
            if not group:
                # exhausted
                return

            participant = self.exp.participantsession_set.create(group=group)
            if rand.random() < completion_rate:
                participant.complete()
            return participant

        # run some sessions
        for i in range(total_runs // 2):
            _participant_session()
        self.group_a.refresh_from_db()
        self.group_b.refresh_from_db()

        # check that the groups don't diverge too much
        self.assertLess(abs(self.group_a.completed - self.group_b.completed), N * 0.1)

        # run the rest of the sessions
        for i in range(total_runs // 2):
            _participant_session()
        self.group_a.refresh_from_db()
        self.group_b.refresh_from_db()

        self.assertEqual(abs(self.group_a.completed - self.group_b.completed), 0)

    def test_target_group_recover_from_skew(self):
        self.group_a.completion_target = 10
        self.group_a.completed = 0
        self.group_b.completion_target = 10
        self.group_b.completed = 0
        self.group_a.save()
        self.group_b.save()

        for i in range(10):
            participant = self.exp.participantsession_set.create(group=self.group_a)
            if i % 3 == 0:
                participant.complete()

            # should keep trying to assign us to B
            self.assertEqual(self.exp.assign_to_group(), self.group_b)
