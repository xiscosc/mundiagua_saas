/**
 * Created by xiscosastre on 5/5/16.
 */

$('#sms_body').keyup(function () {
   var val = $(this).val();
    $('#sms_count').html((160-val.length));
});

$('.btn_sms').on('click', function () {
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