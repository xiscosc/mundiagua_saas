/**
 * Created by xiscosastre on 14/12/2016.
 */


function getHtml(i, client, address, assigned, url) {
    return '<div id="content">' +
                        '<div id="siteNotice">' +
                        '</div>' +
                        '<h4 id="firstHeading" class="firstHeading"><small>'+i+'</small> '+client+'</h4>' +
                        '<div id="bodyContent">' +
                        '<p>'+address+'</p>' +
                        '<p>'+assigned+'</p>' +
                        '<p><a href="'+url+'">' +
                        'Ver avería</p>' +
                        '</div>' +
                        '</div>';
}

function createInfoWindow(i, client, address, assigned, url) {
    return new google.maps.InfoWindow({
                    content: getHtml(i, client, address, assigned, url)
                });
}

function createMarker(map, lat, lng) {

    return new google.maps.Marker({
                    position: {lat: lat, lng: lng},
                    map: map
                });
}

function putMarker(map, lat, lng, i, client, address, assigned, url) {
    var mar = createMarker(map, lat, lng);
    var inf = createInfoWindow(i, client, address, assigned, url);
    mar.addListener('click', function () {
                    inf.open(map, mar);
                });
}

function initMap() {
    var mallorca = {lat: 39.6953, lng: 3.0176};
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 8,
        center: mallorca
    });
    return map;
}