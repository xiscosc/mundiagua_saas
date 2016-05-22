/**
 * Created by xiscosastre on 23/05/16.
 */
function preparePrint() {
    $("td").each(function() {
        if (($(this).html().replace(/ /g,'').replace(/\r?\n|\r/g, '') == "") && ($(this).attr('id')!= "header")) {
            $parent = $(this).parent();
            if ($parent.children().length <= 2) {
                $parent.hide();
            }
        }
    });
    window.print();
}
$(function() {
    preparePrint();
});