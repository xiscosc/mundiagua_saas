function createTd(data) {
    if (data == null) {
        return "<td>No disponible</td>";
    }

    return "<td>"+ data + "</td>";
}

function createTr(data) {
    if (data == null) {
        return "<tr>No disponible</tr>";
    }

    return "<tr>"+ data + "</tr>";
}

function initTable() {
    $('#sms-table').html("<tr>\n" +
        "                    <th>Remitente</th>\n" +
        "                    <th>Telefono</th>\n" +
        "                    <th>Fecha</th>\n" +
        "                    <th>Texto</th>\n" +
        "                </tr>");
}

function getDate(ts) {
    var date = new Date(ts * 1000);
    var dd = String(date.getDate()).padStart(2, '0');
    var mm = String(date.getMonth() + 1).padStart(2, '0'); //January is 0!
    var yyyy = date.getFullYear();
    var hh = date.getHours();
    var min = date.getMinutes();

    if (hh < 10) {
        hh = "0"+hh;
    }

    if (min < 10) {
        min = "0"+min;
    }

    return hh + ":" + min + " " + dd + '/' + mm + '/' + yyyy;
}

function getAllSMS(limit=0, offset=0) {
    var params = "?limit=" + limit + "&offset=" + offset;
    $.get("/core/sms-api/sms/all/list" + params, function (data) {
        $('#sms-list').fadeOut();
        initTable();
        data.items.forEach(function (item, index) {
            $('#sms-table').append(createTr(
                createTd(item.phone.name) +
                createTd("+" + item.msisdn) +
                createTd(getDate(item.ts)) +
                createTd(item.text)));
        });
    });
}

$(function () {
    getAllSMS();
});