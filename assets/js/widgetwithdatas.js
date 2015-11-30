(function() {
// Localize jQuery variable
var jQuery;

/******** Load jQuery if not present *********/
if (window.jQuery === undefined || window.jQuery.fn.jquery !== '1.11.1') {
    var script_tag = document.createElement('script');
    script_tag.setAttribute("type","text/javascript");
    script_tag.setAttribute("src","http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js");
    if (script_tag.readyState) {
      script_tag.onreadystatechange = function () { // For old versions of IE
          if (this.readyState == 'complete' || this.readyState == 'loaded') {
              scriptLoadHandler();
          }
      };
    } else { // Other browsers
      script_tag.onload = scriptLoadHandler;
    }
    // Try to find the head, otherwise default to the documentElement
    (document.getElementsByTagName("head")[0] || document.documentElement).appendChild(script_tag);
} else {
    // The jQuery version on the window is the one we want to use
    jQuery = window.jQuery;
    main();
}

var headID = document.getElementsByTagName("head")[0];
var newScript = document.createElement('script');
newScript.type = 'text/javascript';
newScript.src = 'https://www.google.com/jsapi';
headID.appendChild(newScript);

/******** Called once jQuery has loaded ******/
function scriptLoadHandler() {
    // Restore $ and window.jQuery to their previous values and store the
    // new jQuery in our local jQuery variable
    jQuery = window.jQuery.noConflict(true);
    // Call our main function
    main(); 
}

/******** Our main function ********/
function main() {
    function askByPollLoadGoogle()
    {
	if(typeof google != 'undefined' && google && google.load)
        {
            // Now you can use google.load() here...
	    google.load('visualization', '1', {'callback':'', 'packages':['corechart']});
        }
        else
        {
            // Retry later...
            setTimeout(askByPollLoadGoogle, 30);
        }
    }
    askByPollLoadGoogle();
    //setTimeout(function(){google.load('visualization', '1', {'callback':'', 'packages':['corechart']})}, 2000); 
    jQuery(document).ready(function($) { 
    	//setTimeout(function(){google.load('visualization', '1', {'callback':'', 'packages':['corechart']})}, 1000);
    	/******* Load CSS *******/
        var css_link = $("<link>", { 
            rel: "stylesheet", 
            type: "text/css", 
            href: "https://www.askbypoll.com/static/polls/css/askbypoll-widget-style.css" 
        });
        css_link.appendTo('head');      
		var font_link = $("<link>", { 
            rel: "stylesheet", 
            type: "text/css", 
            href: "https://fonts.googleapis.com/css?family=Montserrat" 
        });
        font_link.appendTo('head'); 

        /******* Load HTML *******/
		$(".askbypoll-embed-poll").each(function(index){
			//setTimeout(function(){google.load('visualization', '1', {'callback':'', 'packages':['corechart']})}, 1000);
			var divId = $(this).attr('id');
			var pollId = $(this).attr('id').split('---')[1];
			var jsonp_url = "https://www.askbypoll.com/embed-poll?pollId="+pollId+"&callback=?";
			var that = $(this);
			var alreadyVoted = getAskByPollCookie('ASKBYPOLL_VOTED_'+pollId);
			var dataGiven = undefined;
			if(divId.startsWith('askbypoll-data')){
				var dataGiven = getAskByPollCookie('ASKBYPOLL_DATA_GIVEN_'+pollId);
			}
			// if(alreadyVoted == 'true' && dataGiven == 'true'){
			// 	var askbypollAge = '19';
			// 	var askbypollGender = "M";
			// 	var askbypollProfession = "Student";
			// 	var askbypollEmail = "a@b.com";
			// 	var pollDiv = $("#askbypoll-embed-poll---"+pollId);
			// 	var jsonp_url = "https://www.askbypoll.com/results-embed-poll?dataStored="+dataGiven+"&alreadyVoted="+alreadyVoted+"&pollId="+pollId+"&age="+askbypollAge+"&gender="+askbypollGender+"&profession="+askbypollProfession+"&email="+askbypollEmail+"&callback=?";
			// 	$.getJSON(jsonp_url, function(data) {
			// 		pollDiv.html(data.html);
			// 		$("#askbypoll-content---1---"+pollId).show();
			// 		google.setOnLoadCallback(drawAgeChart(pollId, data.age_dic));
			// 		google.setOnLoadCallback(drawGenderChart(pollId, data.gender_dic));
			// 		google.setOnLoadCallback(drawProfessionChart(pollId, data.prof_dic));
			// 		google.setOnLoadCallback(drawRegionsMap(pollId, data.country_dic));
			// 		event.stopPropagation();
			// 	});
			// }else {
				$.getJSON(jsonp_url, function(data) {
					console.log(data);
					that.html(data.html);
					var check_if_voted_url = "https://www.askbypoll.com/vote-embed-poll?pollId="+pollId+"&alreadyVoted="+alreadyVoted+"&callback=?";
					$.getJSON(check_if_voted_url, function(data) {
					console.log("data is ::",data);
					if("result" in data){
						var result = data.result;
						console.log("Result is::",result);
						for (var choice in result) {
							if (result.hasOwnProperty(choice)) {
								var progressBarId = "askbypoll-embed-progress-bar---"+choice;
								var percent = result[choice].split('---')[0];
								$('#'+progressBarId).css('display','inline-block');
								$('#'+progressBarId).css('width',percent+'%');
								$('#'+progressBarId).css('background','yellow');
								$('#askbypoll-result-choice---'+choice).text(percent+'%');
							}
						}
					}

					});
				});
			// }
		});
		$(".askbypoll-embed-poll").on( "click", ".askbypoll-embed-poll-question-choice-text", function(event) {
			var pollId = $(this).parent().parent().attr("id").split('---')[1];
			var divId = $(this).parent().parent().parent().parent().attr("id");
			var alreadyVoted = getAskByPollCookie('ASKBYPOLL_VOTED_'+pollId);
			var dataGiven = getAskByPollCookie('ASKBYPOLL_DATA_GIVEN_'+pollId);
			
			console.log(alreadyVoted, dataGiven);
			if(alreadyVoted == 'true')
						event.stopPropagation();
			else {
				var a = new Date();
				a = new Date(a.getTime() +1000*60*60*24);
				document.cookie = 'ASKBYPOLL_VOTED_'+pollId+'='+true+'; expires='+a.toGMTString()+';path=/'; 
				var choiceId = $(this).attr("id").split('---')[1];
				var jsonp_url = "https://www.askbypoll.com/vote-embed-poll?pollId="+pollId+"&choiceId="+choiceId+"&callback=?";
				$.getJSON(jsonp_url, function(data) {
					var result = data.result;
					for (var choice in result) {
						if (result.hasOwnProperty(choice)) {
							var progressBarId = "askbypoll-embed-progress-bar---"+choice;
							var percent = result[choice].split('---')[0];
							$('#'+progressBarId).css('display','inline-block');
							$('#'+progressBarId).css('width',percent+'%');
							$('#'+progressBarId).css('background','yellow');
							$('#askbypoll-result-choice---'+choice).text(percent+'%');
						}
					}
					if(divId.startsWith('askbypoll-data')){
						//$("#askbypoll-embed-poll-question-choices---"+pollId).css("opacity","0.5");
						$("#askbypoll-embed-overlay---"+pollId).toggle("slow");
					}
				});
			}
		});
		
		$(".askbypoll-embed-poll").on( "click", ".askbypoll-embed-poll-question-choice-img", function(event) {
			var pollId = $(this).parent().parent().attr("id").split('---')[1];
			var divId = $(this).parent().parent().parent().parent().attr("id");
			var alreadyVoted = getAskByPollCookie('ASKBYPOLL_VOTED_'+pollId);
			var dataGiven = getAskByPollCookie('ASKBYPOLL_DATA_GIVEN_'+pollId);
			if(alreadyVoted == 'true')
						event.stopPropagation();
			else {
				var a = new Date();
				a = new Date(a.getTime() +1000*60*60*24);
				document.cookie = 'ASKBYPOLL_VOTED_'+pollId+'='+true+'; expires='+a.toGMTString()+';path=/'; 
				var choiceId = $(this).attr("id").split('---')[1];
				// var pollId = $(".askbypoll-embed-poll").attr('id').split('---')[1];
				console.log(pollId);
				var jsonp_url = "https://www.askbypoll.com/vote-embed-poll?pollId="+pollId+"&choiceId="+choiceId+"&callback=?";
				$.getJSON(jsonp_url, function(data) {
					var result = data.result;
					for (var choice in result) {
						if (result.hasOwnProperty(choice)) {
							var progressBarId = "askbypoll-embed-progress-bar---"+choice;
							var percent = result[choice].split('---')[0];
							$('#'+progressBarId).css('display','inline-block');
							$('#'+progressBarId).css('width',percent+'%');
							$('#'+progressBarId).css('background','yellow');
							$('#askbypoll-result-choice---'+choice).text(percent+'%');
						}
					}
					if(divId.startsWith('askbypoll-data')){
						$("#askbypoll-embed-poll-question-choices---"+pollId).css("opacity","0.5");
						$("#askbypoll-embed-overlay---"+pollId).toggle("slow");
					}		
				});
			}
		});
		
		$(".askbypoll-embed-poll").on( "click", ".askbypoll-button", function() {
			var that = $(this);
			var pollId = $(this).parent().parent().attr("id").split('---')[1];
			var pollDiv = $("#askbypoll-data-embed-poll---"+pollId);
			var askbypollAge = $("#askbypoll-age---"+pollId).val();
			var askbypollGender = $("#askbypoll-gender---"+pollId).val();
			var askbypollProfession = $("#askbypoll-profession---"+pollId).val();
			var askbypollEmail = $("#askbypoll-email---"+pollId).val();
			console.log(askbypollEmail,askbypollProfession,askbypollGender,askbypollAge);
			if(askbypollAge.trim() == "" || askbypollGender == "notSelected" || askbypollProfession == "notSelected"){
				$("#askbypoll-age---"+pollId).parent().prepend('<span class="askbypoll-embed-error"> Age Gender Profession are mandatory</span>');
			}else{
				var jsonp_url = "https://www.askbypoll.com/results-embed-poll?pollId="+pollId+"&age="+askbypollAge+"&gender="+askbypollGender+"&profession="+askbypollProfession+"&email="+askbypollEmail+"&callback=?";
				var a = new Date();
				a = new Date(a.getTime() +1000*60*60*24);
				document.cookie = 'ASKBYPOLL_DATA_GIVEN_'+pollId+'='+true+'; expires='+a.toGMTString()+';path=/';
				$.getJSON(jsonp_url, function(data) {
					$("#askbypoll-embed-overlay---"+pollId).toggle("slow");
					pollDiv.html(data.html);
					$("#askbypoll-content---1---"+pollId).show();
					google.setOnLoadCallback(drawAgeChart(pollId, data.age_dic));
					google.setOnLoadCallback(drawGenderChart(pollId, data.gender_dic));
					google.setOnLoadCallback(drawProfessionChart(pollId, data.prof_dic));
					google.setOnLoadCallback(drawRegionsMap(pollId, data.country_dic));
				});
			}
		});
		$(".askbypoll-embed-poll").on( "click", ".askbypoll-close-button", function() {
			console.log("reached in close");
			var that = $(this);
			var pollId = $(this).attr('id').split('---')[1];
			var overlayId = "#askbypoll-embed-overlay---"+pollId;
			console.log("reached in close",overlayId);
			$(overlayId).toggle('slow');
		});

		$(".askbypoll-embed-poll").on( "click", ".askbypoll-embed-tab-radio", function() {
			var that = $(this);
			var elemId = that[0].id;
			var content_index = elemId.split("---")[1];
			var pollId = elemId.split("---")[2];
			var show_content = '#askbypoll-content---'+content_index+'---'+pollId;
			$(".askbypoll-embed-content"+pollId).hide();
			$(show_content).show();
		});

		function drawAgeChart(pollId, age_dic) {
			var data = google.visualization.arrayToDataTable([
			  ['Task', 'Hours per Day'],
			  ['Upto 19',age_dic['under_19']],
			  ['19-25',age_dic['bet_20_25']],
			  ['26-30',age_dic['bet_26_30']],
			  ['31-35',age_dic['bet_31_35']],
			  ['36-50',age_dic['bet_36_50']],
			  ['50 Above',age_dic['over_50']]
			]);
			var options = {
			  'backgroundColor': 'transparent',
			  // 'width':700,
     		             'height':400
			};
			var chart = new google.visualization.PieChart(document.getElementById("askbypoll-agechart---"+pollId));
			chart.draw(data, options);
	  	}
	  	function drawGenderChart(pollId, gender_dic) {
			var data = google.visualization.arrayToDataTable([
			  ['Task', 'Hours per Day'],
			  ['Male', gender_dic["M"]],
			  ['Female',gender_dic["F"]],
			  ['Not Say', gender_dic["D"]]
			]);
			var options = {
			  'backgroundColor': 'transparent',
			  // 'width':700,
     		             'height':400
			};
			var chart = new google.visualization.PieChart(document.getElementById("askbypoll-genderchart---"+pollId));
			chart.draw(data, options);
		}
		function drawProfessionChart(pollId, prof_dic) {
			var profData = [['Profession','Votes']];
			for(prof in prof_dic)
				profData.push([prof,prof_dic[prof]]);
			var data = google.visualization.arrayToDataTable(profData);
			var options = {
			  'backgroundColor': 'transparent',
			  // 'width':700,
     		             'height':400
			};
			var chart = new google.visualization.PieChart(document.getElementById("askbypoll-professionchart---"+pollId));
			chart.draw(data, options);
		}
		function drawRegionsMap(pollId, country_dic) {
			var conData = [['Country', 'Votes']];
			for(con in country_dic){
				conData.push([con,country_dic[con]]);
			}
			var data = google.visualization.arrayToDataTable(conData);
			var options = {
				'backgroundColor': 'transparent',
				'height':400
			};
			var chart = new google.visualization.GeoChart(document.getElementById('askbypoll-regions_div---'+pollId));
			chart.draw(data, options);
		}
    });
}
function getAskByPollCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
    }
    return "";
}
})(); // We call our anonymous function immediately
