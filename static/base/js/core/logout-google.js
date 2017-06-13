/**
 * Created by xiscosastre on 09/06/2017.
 */

function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
      console.log('User signed out.');
    });
    auth2.disconnect();
}


$(function () {
    gapi.load('auth2', function() {
        gapi.auth2.init().then(function () {
            signOut();
        });
      });
});