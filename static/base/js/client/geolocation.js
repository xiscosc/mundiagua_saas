/**
 * Created by xiscosastre on 24/5/16.
 */
function getLocation() {
    if (navigator.geolocation) {
        $('#modal_geo').modal('toggle');
        navigator.geolocation.getCurrentPosition(sendPosition, errorPosition, {
            maximumAge: 200,
            timeout: 5000,
            enableHighAccuracy: true
        });
    } else {
        errorPosition(false);
    }
}
function errorPosition(error) {
    $body = $('#modal_body_geo');
    $body.html('<h4 style="color: red">Error obteniendo localización</h4>' +
        '<p>Por favor active la ubicación de su dispositivo, permita su uso y recargue la página.</p>');
    if (error) {
        $body.append('<h5>Código de error: ' + error.message + "</h5>");
    }
}
function sendPosition(position) {
    $form = $('#form_geo');
    $token = $form.children().first();
    $button = $('#btn_geo');

    var parametros = {
        "lat": position.coords.latitude,
        "lon": position.coords.longitude,
        "csrfmiddlewaretoken": $token.val()
    };
    $.ajax({
        data: parametros,
        url: $form.prop('action'),
        type: 'post',
        success: function (response) {
            $button.remove();
            $('#space_geo').append('<a href="https://maps.google.com/maps?q=loc:'
                + position.coords.latitude + ',' + position.coords.longitude
                + '" type="button" target="_blank" class="btn btn-success">' +
                '<span class="glyphicon glyphicon-map-marker" aria-hidden="true"></span></a>');
            $('#modal_geo').modal('toggle');

        }
    });
}


$(function () {
    $('#btn_geo').on('click', function () {
        getLocation();
    })
});