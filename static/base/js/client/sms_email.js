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
    let id = $('#whatsapp_template_pk').val();
    let t = templates[id];
    if (t.has_attachment) {
        $(this).prop('disabled', true).html("Cargando fichero...");
        triggerS3Upload();
    } else {
        $(this).prop('disabled', true).html("Enviando...");
        $('#form_whatsapp').submit();
    }

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

function createPlaceholders(num, has_attachment) {
    $('#whatsapp_placeholders').html("");
    $('#whatsapp_file_placeholder').html("");
    for (let i = 0; i < num; i++) {
        let id = i + 1;
        let label = '<label for="whatsapp_placeholder_' + id + '">Campo {{' + id + '}}:</label>';
        let field = '<input required="" type="text" class="form-control" id="whatsapp_placeholder_' + id + '" name="whatsapp_placeholder_' + id + '" />';
        $('#whatsapp_placeholders').append(label + field);
    }

    if (has_attachment) {
        let label = '<label for="whatsapp_file">Archivo adjunto:</label>';
        let field = '<input required="" accept="application/pdf" type="file" class="form-control" id="whatsapp_file" name="whatsapp_file" />';
        let field_name = '<input required="" type="hidden" class="form-control" id="whatsapp_file_name" name="whatsapp_file_name" />';
        let field_key = '<input required="" type="hidden" class="form-control" id="whatsapp_file_key" name="whatsapp_file_key" />';
        $('#whatsapp_placeholders').append(field_name);
        $('#whatsapp_placeholders').append(field_key);
        $('#whatsapp_file_placeholder').append(label + field);
    }
}

function triggerS3Upload() {
    let url = $('#whatsapp_file_placeholder').data('url');
    let token = $('#whatsapp_file_placeholder').data('token');
    let fileName = $('#whatsapp_file').val().replace(/C:\\fakepath\\/i, '');
    $.post(url, {whatsapp_file_name: fileName, csrfmiddlewaretoken: token})
        .done(function( data ) {
            $('#whatsapp_file_name').val(fileName);
            $('#whatsapp_file_key').val(data.key);
            uploadWhatsAppFileToS3(data.s3Data)
        })
        .fail(function (data) {
            alert("Ha ocurrido un error, recargue la página");
        });
}

function uploadWhatsAppFileToS3(s3Data) {
    var formData = new FormData();
    formData.append('AWSAccessKeyId', s3Data.fields.AWSAccessKeyId)
    formData.append('key', s3Data.fields.key)
    formData.append('policy', s3Data.fields.policy)
    formData.append('signature', s3Data.fields.signature)
    formData.append('Content-Type', s3Data.fields["Content-Type"])
    formData.append('file', $('#whatsapp_file')[0].files[0])

    $.ajax({
        type: 'POST',
        url: s3Data.url,
        // Content type must much with the parameter you signed your URL with
        contentType: false,
        // this flag is important, if not set, it will try to send data as a form
        processData: false,
        // the actual file is sent raw
        data: formData,
        success: function() { $('#form_whatsapp').submit(); },
        error: function () { alert("Ha ocurrido un error, recargue la página"); },
    })
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
        createPlaceholders(t.placeholders, t.has_attachment);
    });
});

$('#whatsapp_template_pk').on('change', function () {
    let id = $(this).val();
    let t = templates[id];
    $('#whatsapp_body').html(t.template);
    createPlaceholders(t.placeholders, t.has_attachment);
});