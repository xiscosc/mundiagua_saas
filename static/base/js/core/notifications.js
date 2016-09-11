/**
 * Created by xiscosastre on 11/9/16.
 */


$.notifyDefaults({
    offset: {
        x: 10,
        y: 65
    },
    animate: {
        enter: 'animated bounceInDown',
        exit: 'animated bounceOutUp'
    }
});

function make_notification(message, type, link) {

    if (!link) {
        $.notify({
            message: message
        }, {
            type: type
        });
    } else {
        $.notify({
            icon: 'glyphicon glyphicon-envelope',
            message: message,
            url: link,
            target: "_self"
        }, {
            type: type
        });
    }

}