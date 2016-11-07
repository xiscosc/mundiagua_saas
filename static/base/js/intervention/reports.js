/**
 * Created by xiscosastre on 07/11/16.
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

    $('input[type=radio][name=zone]').change(function() {
        if (this.value == '1') {
            $('#zone_pk').show('slow');
        }
        else if (this.value == '0') {
            $('#zone_pk').hide('slow');
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

    $('input[type=radio][name=worker]').change(function() {
        if (this.value == '1') {
            $('#worker_pk').show('slow');
        }
        else if (this.value == '0') {
            $('#worker_pk').hide('slow');
        }
    });

    $('#reportsol').on('click', function () {
        $(this).prop("disabled", true);
        $(this).val("Generando...");
        $("#reportform").submit();
    })

});


