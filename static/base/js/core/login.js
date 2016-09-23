/**
 * Created by xiscosastre on 23/09/16.
 */

$('#btn-log').on('click', function () {
   $('#id_username').val($('#id_username').val().toLowerCase());
   $('#form-log').submit();
});