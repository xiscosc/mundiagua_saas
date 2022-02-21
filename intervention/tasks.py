from async_messages import messages


def send_intervention_assigned(intervention, current_user_id):
    result_send = intervention.send_to_user(intervention.assigned)
    if not result_send:
        from core.models import User
        messages.warning(User.objects.get(pk=current_user_id), "Error enviando " + str(intervention) + " a " + intervention.assigned.get_full_name())


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

