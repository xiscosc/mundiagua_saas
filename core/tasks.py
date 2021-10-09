import uuid
import io
import json

from async_messages import messages
from django.template.loader import get_template
from django.conf import settings

from core.utils import send_data_to_user, create_amazon_client


def send_message(pk, body):
    from core.models import Message
    ins = Message.objects.get(pk=pk)
    result = send_data_to_user(ins.to_user, ins.subject, body, from_user=ins.from_user)
    if result:
        messages.success(ins.from_user, "Mensaje a " + ins.to_user.get_full_name() + " enviado correctamente")
    else:
        messages.warning(ins.from_user, "No se ha podido enviar el mensaje a " + ins.to_user.get_full_name())


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
        logo_type = '1' if budget.get_repair().is_ath() else '0'
        template_props = {'budget': budget, 'logo': '1', 'type': logo_type, 'qr': generate_repair_qr_code(budget.get_repair().online_id)}
        template = 'print_budget.html'
    elif type == "repairath":
        from repair.models import AthRepair
        from repair.utils import generate_repair_qr_code
        repair = AthRepair.objects.get(pk=pk)
        template_props = {'repair': repair, 'logo': '1', 'type': '1', 'qr': generate_repair_qr_code(repair.online_id)}
        template = 'print_repair.html'
    elif type == "repairidegis":
        from repair.models import IdegisRepair
        from repair.utils import generate_repair_qr_code
        repair = IdegisRepair.objects.get(pk=pk)
        template_props = {'repair': repair, 'logo': '1', 'type': '0', 'qr': generate_repair_qr_code(repair.online_id)}
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

    if task_type == 'email' and subject is not None:
        from client.models import Email
        message['subject'] = subject
        message['recipient'] = Email.objects.get(pk=recipient_pk).email
        success_message = "Email con PDF enviado correctamente a " + message['recipient']
    elif task_type == 'whatsapp' and whatsapp_template is not None:
        from client.models import Phone
        message['template'] = whatsapp_template
        message['recipient'] = Phone.objects.get(pk=recipient_pk).full_international_format().replace(' ', '')
        success_message = "Mensaje con PDF enviado correctamente por WhatsApp"
    else:
        raise Exception('Incomplete pdf task body')

    create_amazon_client('sqs').send_message(QueueUrl=settings.PDF_QUEUE, MessageBody=json.dumps(message))
    messages.success(User.objects.get(pk=user_pk), success_message)


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
    try:
        from django.core.mail import EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject,
            body,
            'Mundiagua SL <consultas@mundiaguabalear.com>',
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
