/**
 * Created by xiscosastre on 26/4/16.
 */

$(function () {
    $('#selector_color').on('change', function () {
        $('#btn-color').css('background-color', $(this).find(':selected').data('color'));
    });

    $('#intervention_status').on('change', function () {
        var new_status = $(this).find(':selected').val();
        if (new_status == 2) {
            $('#intervention_assigned').fadeIn('slow');
        } else {
            $('#intervention_assigned').fadeOut('slow');
        }
    });

    $('.form_modify').on('submit', function () {
        $('.forms_content').hide('slow');
        $('.forms_progress').show('slow');
    });
});