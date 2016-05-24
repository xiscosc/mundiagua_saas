$(function () {

    $.get("/intervention/morris/input/", function (data) {
        Morris.Line({
            element: 'morris-line-chart',
            data: data,
            xkey: 'y',
            ykeys: ['t'],
            labels: ['Total diario'],
            resize: true
        });
    });


    $.get("/intervention/morris/assigned/", function (data) {
        Morris.Donut({
            element: 'morris-donut-chart',
            data: data,
            resize: true
        });
    });


    $.get("/intervention/morris/yearvs/", function (data) {
        Morris.Bar({
            element: 'morris-bar-chart',
            data: data.d,
            xkey: 'y',
            ykeys: ['a', 'b'],
            labels: data.labels,
            hideHover: 'auto',
            resize: true
        });
        $('#bar-chart-title').append(data.labels[0] + " vs " + data.labels[1])
    });

});
