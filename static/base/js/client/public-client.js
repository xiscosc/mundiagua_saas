/**
 * Created by xiscosastre on 4/08/16.
 */

$(function() {
    $bar = $('#pb');
    $bar.css('width', perc+"%");
    if (perc==100) {
        $bar.addClass('progress-bar-success');
        $bar.removeClass('active');
    }
});