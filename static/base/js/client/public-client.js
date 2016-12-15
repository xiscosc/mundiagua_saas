/**
 * Created by xiscosastre on 4/08/16.
 */

$(function() {
    $bar = $('#pb');

    $bar.css('width', Math.abs(perc)+"%");
    if (perc==100) {
        $bar.addClass('progress-bar-success');
        $bar.removeClass('active');
    }
    if (perc<0) {
        $bar.addClass('progress-bar-danger');
        $bar.removeClass('active');
    }
});