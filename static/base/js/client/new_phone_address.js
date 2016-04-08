/**
 * Created by xiscosastre on 6/4/16.
 */

$('#btn_other').on( "click", function( event ) {
  event.preventDefault();
  $('#other').val(1);
  $('#new_form').submit();
});