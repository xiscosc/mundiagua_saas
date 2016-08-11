/**
 * Created by xiscosastre on 29/7/16.
 */

$(function () {

    var zone_selector = $('#id_zone');
    var add_selector = $('#id_address');
    var label_default_zone = $('#label_default_zone');

    label_default_zone.hide();

    var options = zone_selector.children();
    options.each(function (index) {
        $(this).css("background-color", zones_data[index + 1]);
        $(this).css("color", "white");
    });

    var selected_zone = $('#selected_zone');

    selected_zone.css('background-color', zones_data[1]);

    zone_selector.on('change', function () {
        var sel = zone_selector.find(":selected");
        selected_zone.css('background-color', zones_data[sel.val()]);
        selected_zone.html(sel.html());
    });

    add_selector.on('change', function () {
        var sel = add_selector.find(":selected");
        var default_zone = default_zones[sel.val()];
        if (default_zone == null) {
            label_default_zone.hide();
            zone_selector.val(1);
            zone_selector.change();
        } else {
            zone_selector.val(default_zone);
            zone_selector.change();
            label_default_zone.show();
        }
    })

});