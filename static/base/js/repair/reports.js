/**
 * Created by xiscosastre on 18/07/23.
 */


$(function () {
    $('input[type=radio][name=status]').change(function() {
        if (this.value == '1') {
            $('#status_pk').show('slow');
        }
        else if (this.value == '0') {
            $('#status_pk').hide('slow');
        }
    });

    $('input[type=radio][name=providertype]').change(function() {
        if (this.value == '1') {
            $('#providertype').show('slow');
        }
        else if (this.value == '0') {
            $('#providertype').hide('slow');
        }
    });

    $('input[type=radio][name=date]').change(function() {
        if (this.value == '1') {
            $('#date_pk').show('slow');
        }
        else if (this.value == '0') {
            $('#date_pk').hide('slow');
        }
    });

    $('#reportsol').on('click', function () {
        $(this).prop("disabled", true);
        $(this).val("Generando...");
        $("#reportform").submit();
    })

});


