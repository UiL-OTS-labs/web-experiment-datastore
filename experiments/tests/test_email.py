from main.models import User
from ..models import Experiment
from ..utils import send_new_experiment_mail


def test_new_experiment_mail(db, rf, mailoutbox):
    experiment = Experiment.objects.create(title='CoolExp')
    user = User.objects.create(first_name='John', last_name='Doe')
    request = rf.get('/')
    send_new_experiment_mail(experiment, user, request)
    assert len(mailoutbox) == 1
    assert 'CoolExp' in mailoutbox[0].body
    assert 'John Doe' in mailoutbox[0].body
