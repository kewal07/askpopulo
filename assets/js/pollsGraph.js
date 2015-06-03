google.load('visualization', '1', {packages: ['corechart', 'bar','geochart']});
$(document).ready(function(){
  drawPollsChart();
  window.addEventListener("resize", resizeEventHandler);

  function resizeEventHandler() {
	drawPollsChart();
	if($('.analysis').is(':visible')){
	    drawGenderChart();
      drawAgeChart();
      drawOthersChart();
      drawLocationChart();
	 }
  }
  
  $('#submit').click(function(){
      $('.analysis').toggle("slow");
	  $('#mapBackButton').removeClass("back");
	  $("#mapBackButton").css("display", "inline-block");
      var delay=1000; //1 seconds
      setTimeout(function(){
      //your code to be executed after 1 seconds
        if($('.analysis').is(':visible')){
          drawGenderChart();
          drawAgeChart();
          drawOthersChart();
          drawLocationChart();
        }
      }, delay); 
    });    
});

function drawPollsChart() {
var question = $("#questionData").val();
console.log(question.question_text);
  var data = google.visualization.arrayToDataTable([
    ['Element', 'Votes', { role: 'style' }],
    ['Html & Css', 8.94, '#F7464A'],            // RGB value
    ['Android', 10.49, '#46BFBD'],            // English color name
    ['IOS', 19.30, '#66FF33'],
    ['Javascript', 21.45, '#FF6600'], // CSS-style declaration
        ]);

        var options = {
          chartArea: {width: '60%'},
          fontSize:20,
          bars: {
            groupWidth: 100
          },
          hAxis: {
            title: '',
            minValue: 0,
            gridlines: {
              color: 'transparent'
              },
            textPosition: 'none',
            baselineColor: 'transparent'
          },
          vAxis: {
            title: '',
            gridlines: {
              color: 'transparent'
              },
          },
          legend:{
              position:'none'
          },
           animation:{
              startup:true,
              duration: 3000,
              easing: 'inAndOut',
         },
        };

        var chart = new google.visualization.BarChart(document.getElementById('pollsChart'));
        chart.draw(data, options);
        google.visualization.events.addListener(chart, 'animationfinish', displayAnnotation);   
        function displayAnnotation(e){
         data = google.visualization.arrayToDataTable([
                ['Options', 'Votes', { role: 'style' }, { role: 'annotation' }],
                ['Html & Css', 8.94, '#F7464A','14%'],            // RGB value
                ['Android', 10.49, '#46BFBD','16%'],            // English color name
                ['IOS', 19.30, '#66FF33','56%'],
                ['Javascript', 21.45, '#FF6600','9%'], // CSS-style declaration
        ]);
        options = {
          chartArea: {width: '60%'},
          fontSize:20,
          bars: {
            groupWidth: 100
          },
          hAxis: {
            title: '',
            minValue: 0,
            gridlines: {
              color: 'transparent'
            },
            textPosition: 'none',
            baselineColor: 'transparent'
          },
          vAxis: {
            title: '',
            gridlines: {
              color: 'transparent'
              },
          },
          legend:{
              position:'none'
          },
           animation:{
              startup:true,
              duration: 1,
              easing: 'inAndOut',
         },
        };

        chart.draw(data,options);
      }
  }

function drawGenderChart() {
  var data = google.visualization.arrayToDataTable([
    ['Gender', 'Votes'],
    ['Male',     350],
    ['Female',   435]
  ]);
  var options = {
    pieHole: 0.4,
    legend:'bottom'
  };
  var chart = new google.visualization.PieChart(document.getElementById('genderChart'));
  chart.draw(data, options);
}

function drawAgeChart() {
  var data = google.visualization.arrayToDataTable([
    ['Age Group', 'Votes'],
    ['Upto 19',     350],
    ['20-35',   435],
    ['36-50',     350],
    ['50+',   435]
  ]);
  var options = {
    pieHole: 0.4,
    legend:'bottom'
  };
  var chart = new google.visualization.PieChart(document.getElementById('ageChart'));
  chart.draw(data, options);
}

function drawOthersChart() {
  var data = google.visualization.arrayToDataTable([
    ['Users', 'Votes'],
    ['Windows', 1350],
    ['Android', 435],
    ['Apple', 350],
    ['Linux', 45]
  ]);
  var options = {
    pieHole: 0.4,
    legend:'bottom'
  };
  var chart = new google.visualization.PieChart(document.getElementById('othersChart'));
  chart.draw(data, options);
}

function drawLocationChart() {
    $('#mapBackButton').removeClass('back');
    var data = google.visualization.arrayToDataTable([
      ['Country', 'Votes'],
      ['Germany', 20000],
      ['United States', 30000],
      ['Brazil', 4000],
      ['Canada', 5000],
      ['France', 6000],
      ['RU', 7000],
      ['India', 9990],
	  ['China', 10000]
    ]);
    var options = {};
    var chart = new google.visualization.GeoChart(document.getElementById('locationChart'));
    chart.draw(data, options);
    google.visualization.events.addListener(chart, 'regionClick', selectHandler);
}
function selectHandler(e) {
  if(e.region == 'IN'){
	$("#mapBackButton").css("display", "inline-block");
	$('#mapBackButton').addClass("back");
    drawIndiaMap()
  } else if(e.region == 'US'){
	$("#mapBackButton").css("display", "inline-block");
	$('#mapBackButton').addClass("back");
    drawUSMap()
  }
} 
  
  /* India Start */
function drawIndiaMap() {
  var data = google.visualization.arrayToDataTable([
            ['State', 'Votes'],
            ['West Bengal', 5],
            ['Karnataka', 22],
            ['Jharkhand', 37],
            ['Andhra Pradesh', 15],
            ['Assam',7],
            ['Rajasthan',102],
            ['Gujarat',112],
            ['Haryana',3],
            ['Goa',76],
            ['Arunachal Pradesh',13],
            ['Bihar',47],
            ['Chhattisgarh',39],
            ['Himachal Pradesh',20],
            ['Kerala',33],
            ['Madhya Pradesh',21],
            ['Maharashtra',45],
            ['Manipur',77],
            ['Meghalaya',67],
            ['Mizoram',1],
            ['Nagaland',4],
            ['Punjab',65],
            ['Sikkim',8],
            ['Telangana',21],
            ['Tripura',3],
            ['Uttar Pradesh',143],
            ['Jammu and Kashmir',17],
            ['Tamil Nadu',33],
            ['Orissa',99],
            ['Puducherry',11],
            ['Lakshadweep',1],
            ['Chandigarh',44],
            ['Delhi',175],
            ['Andaman and Nicobar Islands',3],
            ['IN-UT',11]
  ]);
  var options = {
      region: 'IN',
      displayMode: 'regions',
      resolution: 'provinces',
      datalessRegionColor: '#666',
      colorAxis: {colors: ['#FF9900', '#FFFFFF', '#00CC00']},
      backgroundColor: '#81d4fa',
      domain: 'IN'
  };
  var chart = new google.visualization.GeoChart(document.getElementById('locationChart'));
  chart.draw(data, options);
};
/* India End */
    
/*US Starts*/
function drawUSMap() {
  var data = google.visualization.arrayToDataTable([
            ['State', 'Data'],
            ['California', 5],
            ['Texas', 22],
            ['Florida', 37],
            ['New York', 15],
            ['Illinois',7],
            ['Pennsylvania',102],
            ['Ohio',112],
            ['Georgia',3],
            ['North Carolina',76],
            ['Michigan',13],
            ['New Jersey',47],
            ['Virginia',39],
            ['Washington',20],
            ['Massachusetts',33],
            ['Arizona',21],
            ['Indiana',45],
            ['Tennessee',77],
            ['Missouri',67],
            ['Maryland',1],
            ['Wisconsin',4],
            ['Minnesota',65],
            ['Colorado',8],
            ['Alabama',21],
            ['South Carolina',3],
            ['Louisiana',143],
            ['Kentucky',17],
            ['Oregon',33],
            ['Oklahoma',99],
            ['Puerto Rico',11],
            ['Connecticut',1],
            ['Iowa',44],
            ['Mississippi',175],
            ['Arkansas',3],
            ['Utah',11],
            ['Kansas',4],
            ['Nevada',65],
            ['New Mexico',8],
            ['Alabama',21],
            ['Nebraska',3],
            ['West Virginia',143],
            ['Idaho',17],
            ['Hawaii',33],
            ['Maine',99],
            ['New Hampshire',11],
            ['Rhode Island',1],
            ['Montana',44],
            ['Delaware',175],
            ['South Dakota',3],
            ['North Dakota',11],
            ['Alaska',33],
            ['District of Columbia',99],
            ['Vermont',11],
            ['Rhode Island',1],
            ['Wyoming',44],
            ['Guam',175],
            ['U.S. Virgin Islands',3],
            ['American Samoa',11],
            ['Northern Mariana Islands',11]
  ]);
var options = {
    region: 'US',
    displayMode: 'regions',
    resolution: 'provinces',
    datalessRegionColor: '#666',
    colorAxis: {colors: ['#B22234', '#FFFFFF', '#3C3B6E']},
    backgroundColor: '#81d4fa',
    domain: 'IN',
    width: '100%'
  };

  var chart = new google.visualization.GeoChart(document.getElementById('locationChart'));
  chart.draw(data, options);
};
/*US Ends*/

function back(){  
	$("#mapBackButton").css("display", "none");  
    drawLocationChart();
}
   
