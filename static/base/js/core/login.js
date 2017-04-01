/**
 * Created by xiscosastre on 23/09/16.
 */


$('form#form-log').on('submit', function (e) {
    var self = this;
    e.preventDefault();
    $('#btn-log').html('<span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span> Entrando...');
    $('#form-data').hide('slow', function () {
        $('#id_username').val($('#id_username').val().toLowerCase());
        self.submit();
    });
    return false;
});