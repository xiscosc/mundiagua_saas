$(function() {

    Morris.Area({
        element: 'morris-area-chart',
        data: [{
            period: '2016-05-01',
            2015: Math.floor((Math.random() * 10) + 1),
            2016: Math.floor((Math.random() * 10) + 1),
        },{
            period: '2016-05-02',
            2015: Math.floor((Math.random() * 10) + 1),
            2016: Math.floor((Math.random() * 10) + 1),
        },{
            period: '2016-05-03',
            2015: Math.floor((Math.random() * 10) + 1),
            2016: Math.floor((Math.random() * 10) + 1),
        },{
            period: '2016-05-04',
            2015: Math.floor((Math.random() * 10) + 1),
            2016: Math.floor((Math.random() * 10) + 1),
        },{
            period: '2016-05-05',
            2015: Math.floor((Math.random() * 10) + 1),
            2016: Math.floor((Math.random() * 10) + 1),
        },{
            period: '2016-05-06',
            2015: Math.floor((Math.random() * 10) + 1),
            2016: Math.floor((Math.random() * 10) + 1),
        },],
        xkey: 'period',
        ykeys: ['2015', '2016'],
        labels: ['Año 2015', 'Año 2016'],
        pointSize: 2,
        hideHover: 'auto',
        resize: true
    });

    Morris.Donut({
        element: 'morris-donut-chart',
        data: [{
            label: "Download Sales",
            value: 12
        }, {
            label: "In-Store Sales",
            value: 30
        }, {
            label: "Mail-Order Sales",
            value: 20
        }],
        resize: true
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
