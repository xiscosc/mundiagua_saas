from async_messages import messages
from celery import shared_task


@shared_task
def send_intervention_assigned(pk):
    from intervention.models import Intervention
    intervention = Intervention.objects.get(pk=pk)
    result_send = intervention.send_to_user(intervention.assigned)
    if not result_send:
        messages.warning(intervention._current_user, "Error enviando " + str(intervention) + " a " + intervention.assigned.get_full_name())


@shared_task
def send_intervention(pk, pkto, pkuser):
    from intervention.models import Intervention
    from core.models import User
    intervention = Intervention.objects.get(pk=pk)
    userto = User.objects.get(pk=pkto)
    result_send = intervention.send_to_user(userto)
    if not result_send:
        user = User.objects.get(pk=pkuser)
        messages.warning(user,
                         "Error enviando " + str(intervention) + " a " + intervention.assigned.get_full_name())