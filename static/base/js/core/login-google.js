/**
 * Created by xiscosastre on 09/06/2017.
 */

function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
      console.log('User signed out.');
    });
}


function onSignIn(googleUser) {
    var id_token = googleUser.getAuthResponse().id_token;
    $('#token').val(id_token);
    $('#form_google').submit();
  };