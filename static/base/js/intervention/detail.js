/**
 * Created by xiscosastre on 26/4/16.
 */

var img_counter = 0;


function urlify(text) {
    var urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.replace(urlRegex, function (url) {
        return '<a class="btn btn-primary btn-xs" target="_blank" href="' + url + '"><div class="fa fa-chain"></div> Enlace externo</a>';
    })
    // or alternatively
    // return text.replace(urlRegex, '<a href="$1">$1</a>')
}


function set_image(element) {
    $modal = $('#modal_image');
    $('#body_image').html("");
    $("#link_original_image").attr('href', "#");
    $remove_link = $('#link_remove');
    $remove_link.hide();
    $('#progress_bar_image').show();
    var url = element.data('url');
    $('#title_image').html("Foto de " + element.data('name'));
    $('#date_image').html(element.data('date'));
    var data_remove = element.data('remove');
    if (data_remove != "noremove") {
        $remove_link.attr('href', data_remove);
        $remove_link.show()
    }
    $modal.modal("show");
    var img = $("<img class='img-responsive' />").attr('src', url)
        .on('load', function () {
            $('#progress_bar_image').hide();
            $("#body_image").append(img);
            $("#link_original_image").attr('href', url);
        });


    var next = element.data("gallery-id") + 1;
    var previous = next - 2;

    if (next >= img_counter) {
        next = 0;
    }

    if (previous < 0) {
        previous = img_counter - 1;
    }

    $('#next_img_btn').data("gallery-id", next);
    $('#previous_img_btn').data("gallery-id", previous);

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

    $('#image').on('change', function () {
        $('#icon_image').hide();
        $("#label_image").prepend('<span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span>');
        $('#form_image').submit();
    });

    $('#document').on('change', function () {
        $('#icon_document').hide();
        $("#label_document").prepend('<span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span>');
        $('#form_document').submit();
    });

    $link_images = $('.link_image');
    $link_images.each(function (index) {
        $(this).data("gallery-id", img_counter);
        img_counter++;
    });

    $link_images.on('click', function () {
        set_image($(this));
    });



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

    $('.gallery_btn').on('click', function () {
        var gallery_id = $(this).data("gallery-id");
        $img_element = $($link_images.get(gallery_id));
        set_image($img_element);
    });
});