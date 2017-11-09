/**
 * Created by xiscosastre on 6/4/16.
 */

$('#btn_other').on( "click", function( event ) {
  event.preventDefault();
  $('#other').val(1);
  $('#new_form').submit();
});


function add_pop(id_label, text){
  var id_button = 'pop_' + id_label;
  var pop_alias = ' <a tabindex="0" id="'+id_button+'" ' +
        'class="btn btn-default btn-circle btn-circle-inline" role="button">' +
        '<i class="fa fa-question"></i></a>';
    $('label:eq( '+id_label+' )').after(pop_alias);
    $('#'+id_button).popover({
        html: true,
        content: text,
        trigger: 'focus'
    });
}

$(function () {
    for (x=0; x<pops.length; x++) {
      add_pop(x, pops[x])
    }
});