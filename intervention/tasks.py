from async_messages import messages
from celery import shared_task


@shared_task
def send_intervention_assigned(intervention):
    result_send = intervention.send_to_user(intervention.assigned)
    if not result_send:
        messages.warning(intervention._current_user, "Error enviando " + str(intervention) + " a " + intervention.assigned.get_full_name())
