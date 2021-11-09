/**
 * Created by xiscosastre on 08/05/2017.
 */

function activateEreaseButton() {
    $('.btn-delete-line').on('click', function (event) {
        event.preventDefault();
        var $parent = $(this).parent().parent();
        $parent.hide("slow", function () {
            $parent.remove();
        });
    });
}

function addNewLine(is_edit) {
    $('#table-budget').append(get_new_line(is_edit));
    $('tr').show('slow');
    $ta = $('.txt-typeahead');
    // $ta.typeahead('destroy');
    // $ta.typeahead({source: data_typeahead});
    activateEreaseButton();
    $("html, body").animate({ scrollTop: $(document).height()-$(window).height() });
    $ta.last().focus();
}

var data_typeahead = [];

function get_new_line(is_edit) {
    var str = '<tr style="display: none;">';
    if (is_edit){
        str = str + '<input type="hidden" value="0" name="pk_line" />';
    }
    str = str + '<td><button class="btn btn-danger btn-delete-line"><i class="fa fa-remove"></i></button></td>' +
    '<td><textarea class="form-control txt-typeahead" rows="3" name="product" required></textarea></td>' +
    '<td><input type="text" class="form-control"  name="price" required autocomplete="off"></td>' +
    '<td><input type="text" class="form-control" name="quantity" required autocomplete="off"></td>' +
    '<td><input type="text" class="form-control"  name="dto" required autocomplete="off"></td>' +
    '</tr>';

    return str
}


$(function () {

    // $.get("/budget/typeahead/", function (data) {
    //     data_typeahead = data;
    //     $ta = $('.txt-typeahead');
    //     $ta.typeahead('destroy');
    //     $ta.typeahead({source: data_typeahead});
    //     activateEreaseButton();
    // });

    $(window).keydown(function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });


});