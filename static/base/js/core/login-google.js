/**
 * Created by xiscosastre on 09/06/2017.
 */


function onSignIn(googleUser) {
    var id_token = googleUser.getAuthResponse().id_token;
    $('#token').val(id_token);
    $('#form_google').submit();
  };