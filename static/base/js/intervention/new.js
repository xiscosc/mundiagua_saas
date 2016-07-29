/**
 * Created by xiscosastre on 29/7/16.
 */

$(function () {

    var zone_selector = $('#id_zone');

    var options = zone_selector.children();
    options.each(function (index) {
        $(this).css("background-color", zones_data[index+1]);
        $(this).css("color", "white");
    });

    var selected_zone = $('#selected_zone');

    selected_zone.css('background-color', zones_data[1]);

    zone_selector.on('change', function () {
            var sel = zone_selector.find(":selected");
            selected_zone.css('background-color', zones_data[sel.val()]);
            selected_zone.html(sel.html());
        })
});