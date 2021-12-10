import uuid
import io
import json

from async_messages import messages
from django.template.loader import get_template
from django.conf import settings

from core.utils import create_amazon_client


def send_pdf_document_task(attachment_id, user_pk, recipient_pk, task_type, body, subject=None, whatsapp_template=None):
    from core.models import User

    id_data = attachment_id.split("_")
    pk = int(id_data[1])
    type = id_data[0]
    if type == "budget":
        from budget.models import BudgetStandard
        budget = BudgetStandard.objects.get(pk=pk)
        template_props = {'budget': budget, 'logo': '1'}
        template = 'print_budget.html'
    elif type == "budgetrepair":
        from repair.utils import generate_repair_qr_code
        from budget.models import BudgetRepair
        budget = BudgetRepair.objects.get(pk=pk)
        logo_type = budget.get_repair().type.value
        template_props = {'budget': budget, 'logo': '1', 'type': logo_type, 'qr': generate_repair_qr_code(budget.get_repair().online_id)}
        template = 'print_budget.html'
    elif type.startswith('repair'):
        from repair.models import RepairType
        from repair.utils import generate_repair_qr_code, get_repair_by_type
        repair = get_repair_by_type(pk, RepairType(type.replace('repair', '')))
        template_props = {'repair': repair, 'logo': '1', 'type': repair.type.value, 'qr': generate_repair_qr_code(repair.online_id)}
        template = 'print_repair.html'
    else:
        raise Exception('Incorrect attachment type')

    htmly = get_template(template)
    html_content = htmly.render(template_props)
    html_content = html_content.replace("/static/", settings.DOMAIN + '/static/')
    encoded_string = html_content.encode()
    key = uuid.uuid1().__str__()
    create_amazon_client('s3').upload_fileobj(io.BytesIO(encoded_string), settings.S3_PDF_UPLOAD, key)
    message = {
        'type': task_type,
        'bodyKey': key,
        'bodyMessage': body
    }

    user = User.objects.get(pk=user_pk)
    if task_type == 'email' and subject is not None:
        from client.models import Email
        message['subject'] = subject
        if user.has_company_email():
            message['from'] = {'name': user.get_full_name(), 'email': user.email}
        message['recipient'] = Email.objects.get(pk=recipient_pk).email
        success_message = "Email con PDF enviado correctamente a " + message['recipient']
    elif task_type == 'whatsapp' and whatsapp_template is not None:
        from client.models import Phone
        message['template'] = whatsapp_template
        message['recipient'] = Phone.objects.get(pk=recipient_pk).full_international_format().replace(' ', '')
        success_message = "Mensaje con PDF enviado correctamente por WhatsApp"
    else:
        raise Exception('Incomplete pdf task body')

    create_amazon_client('sns').publish(TopicArn=settings.PDF_TOPIC, Message=json.dumps(message))
    messages.success(user, success_message)


def send_mail_client_with_pdf(email_pk, subject, body, user_pk, attachment_id):
    send_pdf_document_task(attachment_id, user_pk, email_pk, 'email', body, subject)


def send_whatsapp_client_with_pdf(phone_pk, placeholders, user_pk, attachment_id):
    body = {'placeholders': placeholders}
    send_pdf_document_task(attachment_id, user_pk, phone_pk, 'whatsapp', body, whatsapp_template='invoice_quote_update')


def send_mail_client(email_pk, subject, body, user_pk):
    from core.models import User
    from client.models import Email
    user = User.objects.get(pk=user_pk)
    address = Email.objects.get(pk=email_pk)
    if user.has_company_email():
        sender = '%s <%s>' % (user.get_full_name(), user.email)
    else:
        sender = 'Consultas Mundiagua <consultas@mundiaguabalear.com>'
    try:
        from django.core.mail import EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject,
            body,
            sender,
            [address.email],
        )
        htmly = get_template('email.html')
        html_content = htmly.render({'subject': subject, 'body': body})
        email.attach_alternative(html_content, "text/html")
        result = email.send()
    except:
        result = False

    if result:
        messages.success(user, "Email enviado correctamente a " + address.email)
    else:
        messages.warning(user, "Error enviando mail a " + address.email)


def notify_sms_received():
    from core.models import User
    users = User.objects.filter(is_officer=True)
    for user in users:
        messages.info(user, "Nuevo SMS recibido")
