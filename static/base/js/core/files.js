let img_counter = 0;
let upload_counter = 0;
let upload_counter_finished = 0;
let uploading_images = false;

function generateId(s) {
    let hash = 0;
    if (s.length === 0) return hash;
    for (i = 0; i < s.length; i++) {
        char = s.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }

    return hash;
}

function prepareUploadToS3(file, url, token) {
    let id = generateId(file.name);
    const displayName = file.name.length <= 40 ? file.name : file.name.substring(0, 40) + "..."
    const uploadBar = '<h5>' + displayName + ' <small id="' + id + '_s">0%</small></h5>\n' +
        '                            <div class="row">\n' +
        '                                <div class="col-md-12 col-xs-12 col-lg-12">\n' +
        '                                    <div class="progress">\n' +
        '                                        <div id="' + id + '_p" class="progress-bar progress-bar-striped progress-bar-info active"\n' +
        '                                             role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"\n' +
        '                                             style="width:0%">\n' +
        '                                        </div>\n' +
        '                                    </div>\n' +
        '                                </div>\n' +
        '                            </div>\n'
    $('#file_progress').append(uploadBar);
    $.post(url, {originalFilename: file.name, csrfmiddlewaretoken: token})
        .done(function (data) {
            uploadFileToS3(file, data)
        })
        .fail(function (data) {
            setUploadToError(id);
        });
}

function uploadFileToS3(file, s3Data) {
    let formData = new FormData();
    formData.append('AWSAccessKeyId', s3Data.fields.AWSAccessKeyId)
    formData.append('key', s3Data.fields.key)
    formData.append('policy', s3Data.fields.policy)
    formData.append('signature', s3Data.fields.signature)
    formData.append('Content-Type', s3Data.fields["Content-Type"])
    formData.append('file', file)

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
        success: function () {
            finishUpload(id);
        },
        error: function () {
            setUploadToError(id);
        },
        xhr: function () {
            var xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener("progress", function (evt) {
                if (evt.lengthComputable) {
                    const percentComplete = Math.floor((evt.loaded / evt.total) * 100);
                    $("#" + id + '_p').css('width', percentComplete + "%")
                    $("#" + id + '_s').html(percentComplete + "%")
                }
            }, false);
            return xhr;
        }
    })
}

function setUploadToError(id) {
    $("#" + id + '_s').html('Error');
    $("#" + id + '_p').removeClass('progress-bar-info').addClass('progress-bar-danger');
}

function finishUpload(id) {
    $("#" + id + '_s').html('100%');
    $("#" + id + '_p').css('width', "100%")
    $("#" + id + '_p').removeClass('progress-bar-info').addClass('progress-bar-success');
    upload_counter_finished++;
    if (upload_counter_finished >= upload_counter) {
        if (uploading_images) {
            $('#preview_progress').show();
            $('#file_progress').hide();
            setTimeout(function () {
                location.reload();
            }, 3750);
        } else {
            location.reload();
        }
    }
}

function appendImage(i) {
    let d = `<button class="btn btn-danger btn-circle btn-circle-inline btn-delete-img img-${i.fileId}" data-url="${i.metaUrl}" data-id="img-${i.fileId}"  href="">
                            <span class="glyphicon glyphicon-remove" aria-hidden="true"/>
          </button>`

    if (i.userId !== doc_id_check) {
        d = ""
    }

    const iHtml = `<a href="${i.downloadUrl}" class="link_image img-${i.fileId}" target="_blank">
            <img class="gallery-th" src="${i.thDownloadUrl}" alt="Imagen de ${i.userName}"/>
        </a>${d}`;

    $('#images-row-body').append(iHtml)
}

function appendDocument(i) {
    let d = `<button class="btn btn-danger btn-circle btn-circle-inline btn-delete-doc" data-url="${i.metaUrl}" data-id="doc-${i.fileId}"  href="">
                            <span class="glyphicon glyphicon-remove" aria-hidden="true"/>
          </button>`

    let visible = `  <button disabled class='btn btn-xs btn-warning'><span class="fa fa-exclamation-circle"></span> Visible para operarios</button>`

    if (i.userId !== doc_id_check) {
        d = ""
    }

    if (i.visible !== true) {
        visible = ""
    }

    const p = `<li id="doc-${i.fileId}" class="list-group-item"> <strong>${i.originalFileName}</strong> | ${i.userName}, ${i.createdAt} ${visible}
                                    <div class="pull-right" style="display: inline-flex">` + d +
        `<button class="btn btn-info btn-circle btn-circle-inline btn-toggle-visibility" data-url="${i.metaUrl}" data-visible="${i.visible}">
                                                <span class="fa fa-eye" aria-hidden="true"/>
                                            </button>
                                            <a class="btn btn-success btn-circle btn-circle-inline"
                                               href="${i.downloadUrl}"
                                               target="_blank">
                                                <span class="glyphicon glyphicon-arrow-down" aria-hidden="true"/>
                                            </a>
                                    </div>
                                </li>`

    $('#documents-row-body').append(p)
}

function initDocumentButtons() {
    $('.btn-delete-doc').on('click', function () {
        const deleteUrl = $(this).data('url')
        const lineId = $(this).data('id')
        $('#' + lineId).html(`Eliminando...`)
        $.ajax({
            type: 'DELETE',
            url: deleteUrl,
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", $('#document').data('token'));
            },
            success: function () {
                $('#' + lineId).remove()
            }
        })
    })

    $('.btn-toggle-visibility').on('click', function () {
        const putUrl = $(this).data('url')
        const v = $(this).data('visible');
        console.log(v)
        const body = {
            visible: !v
        }
        console.log(body)
        $.ajax({
            type: 'PUT',
            url: putUrl,
            data: body,
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", $('#document').data('token'));
            },
            success: function () {
                location.reload();
            }
        })
    })
}

function initDeleteImages() {
    $('.btn-delete-img').on('click', function () {
        const deleteUrl = $(this).data('url')
        const lineId = $(this).data('id')
        $.ajax({
            type: 'DELETE',
            url: deleteUrl,
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", $('#document').data('token'));
            },
            success: function () {
                $('.' + lineId).remove()
            }
        })
    })
}


function loadImages() {
    $.get(image_list_url, function (data) {
        data.forEach(function (item,) {
            appendImage(item);
        });

        if (data.length > 0) {
            $('#images-row').fadeIn('fast');
        }

        initDeleteImages();
    });
}

function loadDocuments() {
    $.get(document_list_url, function (data) {
        data.forEach(function (item,) {
            appendDocument(item);
        });

        if (data.length > 0) {
            $('#documents-row').fadeIn('fast');
        }

        initDocumentButtons();
    });
}

$(function () {
    $('#document').on('change', function () {
        const url = $('#document').data('url');
        const token = $('#document').data('token');
        $('#file_selection').hide('slow');
        uploading_images = false;
        upload_counter = this.files.length;
        upload_counter_finished = 0;
        [...this.files].forEach(function (item, index) {
            prepareUploadToS3(item, url, token);
        });
    });

    $('#image').on('change', function () {
        const url = $('#image').data('url');
        const token = $('#image').data('token');
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

    loadImages();
    loadDocuments();
});
