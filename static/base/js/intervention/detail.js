/**
 * Created by xiscosastre on 26/4/16.
 */

function urlify(text) {
    var urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.replace(urlRegex, function (url) {
        return '<a class="btn btn-primary btn-xs" target="_blank" href="' + url + '"><div class="fa fa-chain"></div> Enlace externo</a>';
    })
    // or alternatively
    // return text.replace(urlRegex, '<a href="$1">$1</a>')
}

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

    try {
        $('#history_table').children().first().children().last().children().each(function () {
            $(this).html("<strong>" + $(this).html() + "</strong>")
        })

    } catch (e) {
        //No table
    }

    $('.intervention_modification_note').each(function () {
        try {
            var txt = $(this).html();
            $(this).html(urlify(txt));
        } catch (err) {

        }
    });


    $('#intervention_description').children().each(function () {
        try {
            var txt = $(this).html();
            $(this).html(urlify(txt));
        } catch (err) {

        }
    });
});