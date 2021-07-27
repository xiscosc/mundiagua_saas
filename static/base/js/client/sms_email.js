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

$('#whatsapp_send').on('click', function () {
    $(this).prop('disabled', true).html("Enviando...");
    $('#form_whatsapp').submit();
});

$('.btn-email').on('click', function () {
    try {
        //$('#email_field').val($('#email_source').html());
        $('#email_body').val(default_sms);
        $('#email_subject').val(default_subject);
    } catch (err) {
        console.log(err);
    }
    $('#modal_mail').modal('show');
});

function createPlaceholders(num) {
    $('#whatsapp_placeholders').html("");
    for (let i = 0; i < num; i++) {
        let id = i + 1;
        let label = '<label for="whatsapp_placeholder_' + id + '">Campo {{' + id + '}}:</label>';
        let field = '<input required="" type="text" class="form-control" id="whatsapp_placeholder_' + id + '" name="whatsapp_placeholder_' + id + '" />';
        $('#whatsapp_placeholders').append(label + field);
    }
}

$('.btn-whatsapp').on('click', function () {
    templates = [];
    $('#whatsapp_template_pk').html("");
    $('#modal_whatsapp').modal('show');
    $('#whatsapp_phone_pk').val($(this).data('phone'));
    $.get("/client/whatsapp/templates/", function (data) {
        data.forEach(function (t) {
            templates[t.id] = t
            let option = '<option value="' + t.id + '">' + t.name + '</option>';
            $('#whatsapp_template_pk').append(option);
        });
        let id = $('#whatsapp_template_pk').val();
        let t = templates[id];
        $('#whatsapp_body').html(t.template);
        createPlaceholders(t.placeholders);
    });
});

$('#whatsapp_template_pk').on('change', function () {
    let id = $(this).val();
    let t = templates[id];
    $('#whatsapp_body').html(t.template);
    createPlaceholders(t.placeholders);
});