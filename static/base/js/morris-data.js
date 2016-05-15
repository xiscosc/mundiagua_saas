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


    Morris.Bar({
        element: 'morris-bar-chart',
        data: [{
            y: '2006',
            a: 100,
            b: 90
        }, {
            y: '2007',
            a: 75,
            b: 65
        }, {
            y: '2008',
            a: 50,
            b: 40
        }, {
            y: '2009',
            a: 75,
            b: 65
        }, {
            y: '2010',
            a: 50,
            b: 40
        }, {
            y: '2011',
            a: 75,
            b: 65
        }, {
            y: '2012',
            a: 100,
            b: 90
        }],
        xkey: 'y',
        ykeys: ['a', 'b'],
        labels: ['Series A', 'Series B'],
        hideHover: 'auto',
        resize: true
    });

});
