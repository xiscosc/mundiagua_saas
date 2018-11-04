/**
 * Created by xiscosastre on 18/05/16.
 */

$(function () {
    $.get("/core/message/ajax/", function (data) {
        $("#message-ajax").prepend(data);
    });
});