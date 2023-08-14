/**
 * Created by xiscosastre on 5/5/16.
 */
let templates = [];

$('#sms_body').keyup(function () {
    var val = $(this).val();
    $('#sms_count').html((160 - val.length));
});

$('.btn-sms').on('click', function () {
    try {
        $('#sms_body').val(default_sms);
        $('#sms_count').html((160 - default_sms.length));
    } catch (err) {
    }
    try {
        $('#from_model').val(from_model_val);
        $('#from_model_id').val(from_model_id_val);
    } catch (err) {
        $('#from_model').remove();
        $('#from_model_id').remove();
    }

    $('#phone_pk').val($(this).data('phone'));
    $('#modal_sms').modal('show');
});

$('.sms_close').on('click', function () {
    $('#sms_body').val("");
    $('#phone_pk').val("");
    $('#sms_count').html(160);
    $('#sms_send').prop('disabled', false).html("Enviar");
});

$('#sms_send').on('click', function () {
    $(this).prop('disabled', true).html("Enviando...");
    $('#form_sms').submit();
});

$('#email_send_button').on('click', function () {
    $(this).prop('disabled', true).html("Enviando...");
    $('#form_email').submit();
});

$('.btn-email').on('click', function () {
    $('#email_body').val("");
    $('#mail-attachment-group').hide();
    $('#email_subject').val("");
    $('#attachment_id').val("");
    $('#mail-attachment-name').html("");
    try {
        $('#email_body').val(default_sms);
        $('#email_subject').val(default_subject);
    } catch (err) {
        console.log(err);
    }
    $('#modal_mail').modal('show');
});

$('#btn-pdf-mail').on('click', function () {
    try {
        $('#mail-attachment-group').show();
        $('#mail-attachment-name').html(a_default_attachment_name);
        $('#email_body').val(a_default_email_body);
        $('#email_subject').val(a_default_email_subject);
        $('#attachment_id').val(a_default_attachment_id);
    } catch (err) {
        console.log(err);
    }
    $('#modal_mail').modal('show');
});
