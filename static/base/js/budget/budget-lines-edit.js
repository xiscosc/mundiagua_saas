/**
 * Created by xiscosastre on 18/05/16.
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

function addNewLine() {
    $('#table-budget').append(new_line);
    $('tr').show('slow');
    $ta = $('.txt-typeahead');
    $ta.typeahead('destroy');
    $ta.typeahead({source: data_typeahead});
    activateEreaseButton();
}

var data_typeahead = [];

var new_line = '<tr style="display: none;">' +
    '<input type="hidden" value="0" name="pk_line" />' +
    '<td><button class="btn btn-danger btn-delete-line"><i class="fa fa-remove"></i></button></td>' +
    '<td><textarea class="form-control txt-typeahead" rows="3" name="product" required></textarea></td>' +
    '<td><input type="text" class="form-control"  name="price" required autocomplete="off"></td>' +
    '<td><input type="text" class="form-control" name="quantity" required autocomplete="off"></td>' +
    '<td><input type="text" class="form-control"  name="dto" required autocomplete="off"></td>' +
    '</tr>';


$(function () {

    $.get("/budget/typeahead/", function (data) {
        data_typeahead = data;
        $ta = $('.txt-typeahead');
        $ta.typeahead('destroy');
        $ta.typeahead({source: data_typeahead});
        activateEreaseButton();
    });

    $('#btn-new-line').on('click', function () {
        addNewLine();
    });

    $(window).keydown(function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });


});