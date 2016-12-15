/**
 * Created by xiscosastre on 23/09/16.
 */

$('#btn-log').on('click', function () {
    $(this).html('<span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span> Entrando...');
    $('#form-data').hide('slow', function () {
        $('#id_username').val($('#id_username').val().toLowerCase());
        $('#form-log').submit();
    });
});