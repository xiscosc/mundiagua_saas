/**
 * Created by xiscosastre on 26/4/16.
 */

var img_counter = 0;
var upload_counter = 0;
var upload_counter_finished = 0;
var uploading_images = false;

function urlify(text) {
    var urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.replace(urlRegex, function (url) {
        return '<a class="btn btn-primary btn-xs" target="_blank" href="' + url + '"><div class="fa fa-chain"></div> Enlace externo</a>';
    })
    // or alternatively
    // return text.replace(urlRegex, '<a href="$1">$1</a>')
}


function imgError(image) {
    image.onerror = "";
    image.src = "https://stackblitz.com/files/react-spinner-sample/github/RahmanM/react-spinner-sample/master/loading.gif";
    return true;
}

function uploadFileToS3(file, s3Data) {
    var formData = new FormData();
    formData.append('AWSAccessKeyId', s3Data.fields.AWSAccessKeyId)
    formData.append('key', s3Data.fields.key)
    formData.append('policy', s3Data.fields.policy)
    formData.append('signature', s3Data.fields.signature)
    formData.append('file', file)

    if (s3Data.fields.ContentType) {
        formData.append('ContentType', s3Data.fields.ContentType)
    }

    let id = generateId(file.name);

    $.ajax({
        type: 'POST',
        url: s3Data.url,
        // Content type must much with the parameter you signed your URL with
        contentType: false,
        // this flag is important, if not set, it will try to send data as a form
        processData: false,
        // the actual file is sent raw
        data: formData,
        success: function() { finishUpload(id); },
        error: function () { setUploadToError(id); },
        xhr: function() {
            var xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener("progress", function(evt) {
                if (evt.lengthComputable) {
                    var percentComplete = (evt.loaded / evt.total) * 100;
                    $("#" + id + '_p').html(Math.floor( percentComplete ) + "%")
                }
            }, false);
            return xhr;
        }
    })
}

function setUploadToError(id) {
    $("#" + id + '_s').removeClass('glyphicon-refresh-animate');
    $("#" + id + '_b').removeClass('btn-default').addClass('btn-danger');
}

function finishUpload(id) {
    $("#" + id + '_s').hide();
    $("#" + id + '_d').show();
    $("#" + id + '_b').removeClass('btn-default').addClass('btn-success');
    upload_counter_finished++;
    if (upload_counter_finished >= upload_counter) {
        if (uploading_images) {
            $('#preview_progress').show();
            $('#file_progress').hide();
            setTimeout(function(){ location.reload();}, 5000);
        } else {
            location.reload();
        }
    }
}

function set_image(element) {
    $modal = $('#modal_image');
    $('#body_image').html("");
    $("#link_original_image").attr('href', "#");
    $remove_link = $('#link_remove');
    $remove_link.hide();
    $('#progress_bar_image').show();
    var s3key = element.data('key');
    $('#title_image').html("Foto de " + element.data('name'));
    $('#date_image').html(element.data('date'));
    var data_remove = element.data('remove');
    if (data_remove != "noremove") {
        $remove_link.attr('href', data_remove);
        $remove_link.show()
    }
    $modal.modal("show");
    $.get(element.data('url'), function (data) {
        var img = $("<img class='img-responsive' />").attr('src', data)
            .on('load', function () {
                $('#progress_bar_image').hide();
                $("#body_image").append(img);
                $("#link_original_image").attr('href', data);
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
    })
}

function prepareUploadToS3(file, url, token) {
    let id = generateId(file.name);
    let uploadElement = '<button style="margin: 3px" disabled class="btn btn-default" id="' + id + '_b">' +
        file.name + ' <div id="' + id + '_p">0%</div>' +
        ' <span id="' + id + '_s" class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span>' +
        '<span id="' + id + '_d" class="glyphicon glyphicon-check" style="display: none"></span></button>';
    $('#file_progress').append(uploadElement);
    $.post(url, {fileName: file.name, csrfmiddlewaretoken: token})
        .done(function( data ) {
            uploadFileToS3(file, data)
        })
        .fail(function (data) {
            setUploadToError(id);
        });
}

function generateId(string) {

    var hash = 0;

    if (string.length == 0) return hash;

    for (i = 0; i < string.length; i++) {
        char = string.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }

    return hash;
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

    $('#document').on('change', function () {
        var url = $('#document').data('url');
        var token = $('#document').data('token');
        $('#file_selection').hide('slow');
        uploading_images = false;
        upload_counter = this.files.length;
        upload_counter_finished = 0;
        [...this.files].forEach(function (item, index) {
            prepareUploadToS3(item, url, token);
        });
    });

    $('#image').on('change', function () {
        var url = $('#image').data('url');
        var token = $('#image').data('token');
        $('#image_selection').hide('slow');
        upload_counter = this.files.length;
        uploading_images = true;
        upload_counter_finished = 0;
        [...this.files].forEach(function (item, index) {
            prepareUploadToS3(item, url, token);
        });
    });

    $('#icon_document').on('click', function () {
        $('#modal_upload').modal("show");
        $('#file_selection').show();
        $('#image_selection').hide();
    })

    $('#icon_image').on('click', function () {
        $('#modal_upload').modal("show");
        $('#image_selection').show();
        $('#file_selection').hide();
    })

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