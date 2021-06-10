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


@shared_task
def upload_file(t, pk):
    from django.conf import settings
    from intervention.models import InterventionImage, InterventionDocument
    if t == "document":
        instance = InterventionDocument.objects.get(pk=pk)
    else:
        instance = InterventionImage.objects.get(pk=pk)

    instance.upload_to_s3()
    if instance.intervention.status_id == settings.ASSIGNED_STATUS:
        send_file_telegram_task.delay(instance.pk, t)


@shared_task
def send_file_telegram_task(pk, t):
    from intervention.models import InterventionDocument, InterventionImage
    if t == 'document':
        instance = InterventionDocument.objects.get(pk=pk)
    else:
        instance = InterventionImage.objects.get(pk=pk)
    instance.send_file_to_telegram()


@shared_task
def delete_telegram_messages_from_intervention(pk, pk_assigned_old):
    from intervention.models import Intervention
    from core.models import User
    from core.utils import delete_telegram_messages
    if pk_assigned_old:
        instance = Intervention.objects.get(pk=pk)
        user = User.objects.get(pk=pk_assigned_old)
        if user.telegram_token:
            ids = []
            files = instance.get_images()
            for f in files:
                if f.telegram_message:
                    ids.append(f.telegram_message)
                    f.telegram_message = None
                    f.save()
            files = instance.get_documents()
            for f in files:
                if f.telegram_message:
                    ids.append(f.telegram_message)
                    f.telegram_message = None
                    f.save()
            if not user.is_officer:
                delete_telegram_messages(user.telegram_token, ids, instance)

@shared_task
def delete_file_from_telegram(token, message_id, instance_pk):
    from core.utils import delete_telegram_messages
    from intervention.models import Intervention
    instance = Intervention.objects.get(pk=instance_pk)
    delete_telegram_messages(token, [message_id], instance)
