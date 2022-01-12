import json
import uuid

from django.urls import reverse
from rest_framework.test import APITestCase

from experiments.models import Experiment


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
        self.assertEqual(response.json()['result'], 'ERR_NOT_OPEN')

    def test_upload_ok(self):
        self.exp.state = Experiment.OPEN
        self.exp.approved = True
        self.exp.save()

        response = self._upload()
        self.assertEqual(response.status_code, 200)

        j = response.json()
        self.assertEqual(j['result'], 'OK')
        self.assertEqual(j['message'], 'Upload successful')

        self.assertEqual(self.exp.datapoint_set.count(), 1)
        self.assertEqual(json.loads(self.exp.datapoint_set.first().data), {'key': 'value'})

    def test_upload_not_found(self):
        response = self.client.post(reverse('api:upload', args=[uuid.uuid4()]), {}, content_type='text/plain')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['result'], 'ERR_UNKNOWN_ID')

    def test_upload_fail_when_not_approved(self):
        self.exp.state = Experiment.OPEN
        self.exp.approved = False
        self.exp.save()

        response = self._upload()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['result'], 'ERR_NOT_OPEN')

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
        self.assertEqual(response.json()['result'], 'ERR_UNKNOWN_ID')
