/**
 * Created by xiscosastre on 26/4/16.
 */

$('#selector-color').on('change', function() {
    $('#btn-color').css('background-color', $(this).find(':selected').data('color'));
});