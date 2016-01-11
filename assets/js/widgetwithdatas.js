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
var poll_choices = {};
var added_polls = [];

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
            href: "http://localhost:8000/static/polls/css/askbypoll-widget-style.css" 
        });
        css_link.appendTo('head');      
		var font_link = $("<link>", { 
            rel: "stylesheet", 
            type: "text/css", 
            href: "https://fonts.googleapis.com/css?family=Montserrat" 
        });
        font_link.appendTo('head'); 
        var parentDivId = $(".askbypoll-embed-poll").width();
		var askByPoll_age_data;
		var askByPoll_gender_data;
		var askbypoll_prof_data;
		var askbypoll_country_data;
		var protectResult = 0;
		function responsive_css(pollId){
			console.log($("#askbypoll-embed-poll-wrapper---"+pollId).width());
			if($("#askbypoll-embed-poll-wrapper---"+pollId).width() < 420){
				$("#askbypoll-embed-overlay---"+pollId).attr("style","width: 80% ! important");
				$("#askbypoll-embed-poll-icon---"+pollId).attr("style","display: none ! important");
				$("#askbypoll-widget-title---"+pollId).attr("style","line-height: 1 ! important; padding-bottom: 0.2rem ! important;");
				// .css("line-height","1 !important");
				// $("#askbypoll-widget-title---"+pollId).css("padding-bottom","0.2rem !important");
				$("#askbypoll-embed-poll-question-text---"+pollId).attr("style","margin-bottom:1rem ! important");
				// css("margin-bottom","1rem !important");
				$("#askbypoll-embed-poll-question-description---"+pollId).attr("style","display: none ! important");
				// if(typeof hide == 'undefined')
				$("#askbypoll-embed-show-demographics---"+pollId).css("position","relative");
				$("#askbypoll-embed-poll-powered-by-p---"+pollId).attr("style","position: relative ! important");
			}
		}
        /******* Load HTML *******/
		$(".askbypoll-embed-poll").each(function(index){
			//setTimeout(function(){google.load('visualization', '1', {'callback':'', 'packages':['corechart']})}, 1000);
			var divId = $(this).attr('id');
			var pollId = $(this).attr('id').split('---')[1];
			console.log(added_polls,jQuery.inArray( pollId, added_polls ));
			if(jQuery.inArray( pollId, added_polls ) != -1){
				$(this)[0].remove();
				return true;
			}
			added_polls.push(pollId);
			var jsonp_url = "http://localhost:8000/embed-poll?pollId="+pollId+"&callback=?";
			var that = $(this);
			var alreadyVoted = getAskByPollCookie('ASKBYPOLL_VOTED_'+pollId);
			var votedChoiceCookie = getAskByPollCookie('ASKBYPOLL_VOTED_CHOICE_'+pollId);
			var dataGiven = undefined;
			if(divId.startsWith('askbypoll-data')){
				var dataGiven = getAskByPollCookie('ASKBYPOLL_DATA_GIVEN_'+pollId);
			}
			if(alreadyVoted == 'true' && dataGiven == 'true'){
				var votedSession = getAskByPollCookie('ASKBYPOLL_VOTED_SESSION_'+pollId);
				var askbypollAge = '19';
				var askbypollGender = "M";
				var askbypollProfession = "Student";
				var askbypollEmail = "a@b.com";
				var pollDiv = $("#askbypoll-data-embed-poll---"+pollId);
				var jsonp_url = "http://localhost:8000/results-embed-poll?dataStored="+dataGiven+"&alreadyVoted="+alreadyVoted+"&pollId="+pollId+"&age="+askbypollAge+"&gender="+askbypollGender+"&profession="+askbypollProfession+"&email="+askbypollEmail+"&votedSession="+votedSession+"&src="+location.href+"&callback=?";
				$.getJSON(jsonp_url, function(data) {
					protectResult = data.protect;
					pollDiv.html(data.html);
					askByPoll_age_data = data.age_dic;
					askByPoll_gender_data = data.gender_dic;
					askbypoll_prof_data = data.prof_dic;
					askbypoll_country_data = data.country_dic;
					$("#askbypoll-content---1---"+pollId).show();
					// $("#askbypoll-embed-poll-question-text---"+pollId).css("margin-left","2rem");
					if(protectResult == 1){
						$('#askbypoll-embed-poll-question-choices---'+pollId.toString()).html('<p id="askbypoll-thankyou-message"> Thank you for your vote!!!</p>');
					}else{
						var progressBarId = "askbypoll-embed-progress-bar---"+votedChoiceCookie;
						$('#'+progressBarId).css('background','red');
					}
					google.setOnLoadCallback(drawAgeChart(pollId, data.age_dic));
					google.setOnLoadCallback(drawGenderChart(pollId, data.gender_dic));
					google.setOnLoadCallback(drawProfessionChart(pollId, data.prof_dic));
					// google.setOnLoadCallback(drawRegionsMap(pollId, data.country_dic));
					responsive_css(pollId);
				});
			} else {
				$.getJSON(jsonp_url, function(data) {
					that.html(data.html);
					var check_if_voted_url = "http://localhost:8000/vote-embed-poll?pollId="+pollId+"&alreadyVoted="+alreadyVoted+"&src="+location.href+"&callback=?";
					$.getJSON(check_if_voted_url, function(data) {
						if("result" in data){
							var result = data.result;
							protectResult = data.protect;
							
							if(protectResult == 0){
								for (var choice in result) {
									if (result.hasOwnProperty(choice)) {
										var progressBarId = "askbypoll-embed-progress-bar---"+choice;
										var percent = result[choice]["percent"];
										var width = result[choice]["width"];
										$('#'+progressBarId).css('display','inline-block');
										$('#'+progressBarId).css('width',width+'%');
										//$('#'+progressBarId).css('background','yellow');
										$('#askbypoll-result-choice---'+choice).text(percent+'%');
										if(percent == 0){
											var resspanid = "#askbypoll-result-choice---"+choice;
											$(resspanid).attr("style", "position: relative; top: 17px; right: 1px;");
											// $(resspanid).css("top","17px");
											// $(resspanid).css("position","relative");
											$('#'+progressBarId).css('background','none');
										}
									}
								}
								$("#askbypoll-embed-show-demographics---"+pollId).show();
								var progressBarId = "askbypoll-embed-progress-bar---"+votedChoiceCookie;
								$('#'+progressBarId).css('background','red');
							} else {
								$('#askbypoll-embed-poll-question-choices---'+pollId.toString()).html('<p id="askbypoll-thankyou-message"> Thank you for your vote!!!</p>');
								$('.askbypoll-embed-content-div').css('height','50px');
							}
						}
						responsive_css(pollId);
					});
				});
			}
		});
		$(".askbypoll-embed-poll").on( "click", ".askbypoll-embed-poll-question-choice-text,.askbypoll-embed-progress-bar", function(event) {
			var pollId = $(this).parent().parent().attr("id").split('---')[1];
			var divId = $(this).parent().parent().parent().parent().attr("id");
			var alreadyVoted = getAskByPollCookie('ASKBYPOLL_VOTED_'+pollId);
			var dataGiven = getAskByPollCookie('ASKBYPOLL_DATA_GIVEN_'+pollId);
			
			if(alreadyVoted == 'true')
						event.stopPropagation();
			else {
				var a = new Date();
				a = new Date(a.getTime() +1000*60*60*24*7);
				document.cookie = 'ASKBYPOLL_VOTED_'+pollId+'='+true+'; expires='+a.toGMTString()+';path='+location.href; 
				var choiceId = $(this).attr("id").split('---')[1];
				document.cookie = 'ASKBYPOLL_VOTED_CHOICE_'+pollId+'='+choiceId+'; expires='+a.toGMTString()+';path='+location.href;  
				poll_choices[pollId] = choiceId;
				var jsonp_url = "http://localhost:8000/vote-embed-poll?pollId="+pollId+"&choiceId="+choiceId+"&src="+location.href+"&callback=?";
				$(".askbypoll-embed-progress-bar").css("width", 0);
				$.getJSON(jsonp_url, function(data) {
					var result = data.result;
					var votedChoice = data.votedChoice;
					protectResult = data.protect;
					var votedSession = data.sessionKey;
					document.cookie = 'ASKBYPOLL_VOTED_SESSION_'+pollId+'='+votedSession+'; expires='+a.toGMTString()+';path='+location.href; 

					if(protectResult == 0){
						for (var choice in result) {
							if (result.hasOwnProperty(choice)) {
								var progressBarId = "askbypoll-embed-progress-bar---"+choice;
								var percent = result[choice]["percent"];
								var width = result[choice]["width"];
								$('#'+progressBarId).css('display','inline-block');
								$('#'+progressBarId).css('width',width+'%');
								if(votedChoice == choice)
									$('#'+progressBarId).css('background','red');
								$('#askbypoll-result-choice---'+choice).text(percent+'%');
								if(percent == 0){
									var resspanid = "#askbypoll-result-choice---"+choice;
									$(resspanid).attr("style", "position: relative; top: 17px; right: 1px;");
									// $(resspanid).css("position","relative");
									$('#'+progressBarId).css('background','none');
								}
							}
						}
					} else {
						$('#askbypoll-embed-poll-question-choices---'+pollId.toString()).html('<p id="askbypoll-thankyou-message"> Thank you for your vote!!!</p>');
						$('.askbypoll-embed-content-div').css('height','50px');
					}
					if(divId.startsWith('askbypoll-data')){
						//$("#askbypoll-embed-poll-question-choices---"+pollId).css("opacity","0.5");
						$("#askbypoll-embed-overlay---"+pollId).toggle("slow");
					}
				});
			}
		});
		
		$(".askbypoll-embed-poll").on( "click", ".askbypoll-embed-poll-question-choice-img, .askbypoll-embed-poll-question-choice-img-text", function(event) {
			var pollId = $(this).parent().parent().attr("id").split('---')[1];
			var divId = $(this).parent().parent().parent().parent().attr("id");
			if($(this).attr("class").indexOf("askbypoll-embed-poll-question-choice-img-text") != -1){
				pollId = $(this).parent().parent().parent().attr("id").split('---')[1];
				divId = $(this).parent().parent().parent().parent().parent().attr("id");
			}
			var alreadyVoted = getAskByPollCookie('ASKBYPOLL_VOTED_'+pollId);
			var dataGiven = getAskByPollCookie('ASKBYPOLL_DATA_GIVEN_'+pollId);
			if(alreadyVoted == 'true')
						event.stopPropagation();
			else {
				var a = new Date();
				a = new Date(a.getTime() +1000*60*60*24*7);
				document.cookie = 'ASKBYPOLL_VOTED_'+pollId+'='+true+'; expires='+a.toGMTString()+';path='+location.href;  
				var choiceId = $(this).attr("id").split('---')[1].replace("text-","");
				document.cookie = 'ASKBYPOLL_VOTED_CHOICE_'+pollId+'='+choiceId+'; expires='+a.toGMTString()+';path='+location.href; 
				poll_choices[pollId] = choiceId;
				// var pollId = $(".askbypoll-embed-poll").attr('id').split('---')[1];
				var jsonp_url = "http://localhost:8000/vote-embed-poll?pollId="+pollId+"&choiceId="+choiceId+"&src="+location.href+"&callback=?";
				$.getJSON(jsonp_url, function(data) {
					var result = data.result;
					var votedChoice = data.votedChoice;
					protectResult = data.protect;
					
					if(protectResult == 0){
						for (var choice in result) {
							if (result.hasOwnProperty(choice)) {
								var progressBarId = "askbypoll-embed-progress-bar---"+choice;
								var percent = result[choice]["percent"];
								var width = result[choice]["width"];
								$('#'+progressBarId).css('display','inline-block');
								$('#'+progressBarId).css('width',width+'%');
								if(percent == 0){
									var resspanid = "#askbypoll-result-choice---"+choice;
									$(resspanid).css("top","17px");
									$(resspanid).css("position","relative");
									$('#'+progressBarId).css('background','none');
								}
								if(votedChoice == choice)
									$('#'+progressBarId).css('background','red');
								//$('#'+progressBarId).css('background','yellow');
								$('#askbypoll-result-choice---'+choice).text(percent+'%');
							}
						}
					} else {
						$('#askbypoll-embed-poll-question-choices---'+pollId.toString()).html('<p id="askbypoll-thankyou-message"> Thank you for your vote!!!</p>');
						$('.askbypoll-embed-content-div').css('height','50px');
					}
					if(divId.startsWith('askbypoll-data')){
						//$("#askbypoll-embed-poll-question-choices---"+pollId).css("opacity","0.5");
						$("#askbypoll-embed-overlay---"+pollId).toggle("slow");
					}		
				});
			}
		});
		
		$(".askbypoll-embed-poll").on( "click", ".askbypoll-button", function() {
			var that = $(this);
			var pollId = $(this).parent().parent().attr("id").split('---')[1];
			//parentDivId = $(this).parent().parent().parent().width();
			var pollDiv = $("#askbypoll-data-embed-poll---"+pollId);
			var askbypollAge = $("#askbypoll-age---"+pollId).val();
			var askbypollGender = $("#askbypoll-gender---"+pollId).val();
			var askbypollProfession = $("#askbypoll-profession---"+pollId).val();
			var askbypollEmail = $("#askbypoll-email---"+pollId).val();
			var votedSession = getAskByPollCookie('ASKBYPOLL_VOTED_SESSION_'+pollId);
			if(askbypollAge.trim() == "" || askbypollGender == "notSelected" || askbypollProfession == "notSelected"){
				$("#askbypoll-age---"+pollId).parent().prepend('<span class="askbypoll-embed-error"> Age Gender Profession are mandatory</span>');
			}else{
				var a = new Date();
                a = new Date(a.getTime() +1000*60*60*24*7);
				document.cookie = 'ASKBYPOLL_DATA_GIVEN_'+pollId+'='+true+'; expires='+a.toGMTString()+';path='+location.href; 
				var jsonp_url = "http://localhost:8000/results-embed-poll?pollId="+pollId+"&age="+askbypollAge+"&gender="+askbypollGender+"&profession="+askbypollProfession+"&email="+askbypollEmail+"&votedSession="+votedSession+"&src="+location.href+"&callback=?";
				//var a = new Date();
				//a = new Date(a.getTime() +1000*60*60*24);
				//document.cookie = 'ASKBYPOLL_DATA_GIVEN_'+pollId+'='+true+'; expires='+a.toGMTString()+';path=/';
				$.getJSON(jsonp_url, function(data) {
					$("#askbypoll-embed-overlay---"+pollId).toggle("slow");
					pollDiv.html(data.html);
					protectResult = data.protect;
					var votedChoice = data.votedChoice;
					var error = data.error;
					if(error != ""){
						$("#askbypoll-embed-poll-wrapper---"+pollId).append('<div class="askbypoll-widget-error" id="askbypoll-widget-error---'+pollId+'">'+error+"</div>");
					}
					$("#askbypoll-content---1---"+pollId).show();
					if(protectResult == 1)
					{
						$('#askbypoll-embed-poll-question-choices---'+pollId.toString()).html('<p id="askbypoll-thankyou-message"> Thank you for your vote!!!</p>');
						$('.askbypoll-embed-content-div').css('height','50px');
					}
					else
					{
						var progressBarId = "askbypoll-embed-progress-bar---"+votedChoice;
						$('#'+progressBarId).css('background','red');
						$("#askbypoll-embed-show-demographics---"+pollId).hide();
						responsive_css(pollId);
					}
					document.cookie = 'ASKBYPOLL_VOTED_CHOICE_'+pollId+'='+votedChoice+'; expires='+a.toGMTString()+';path='+location.href; 
					// $("#askbypoll-embed-poll-question-text---"+pollId).css("margin-left","2rem");
					askByPoll_age_data = data.age_dic;
					askByPoll_gender_data = data.gender_dic;
					askbypoll_prof_data = data.prof_dic;
					askbypoll_country_data = data.country_dic;
					google.setOnLoadCallback(drawAgeChart(pollId, data.age_dic));
					google.setOnLoadCallback(drawGenderChart(pollId, data.gender_dic));
					google.setOnLoadCallback(drawProfessionChart(pollId, data.prof_dic));
					// google.setOnLoadCallback(drawRegionsMap(pollId, data.country_dic));
				});
			}
		});
		$(".askbypoll-embed-poll").on( "click", ".askbypoll-close-button", function() {
			var that = $(this);
			var pollId = $(this).attr('id').split('---')[1];
			var overlayId = "#askbypoll-embed-overlay---"+pollId;
			
			if(protectResult == 1) {
				$('#askbypoll-embed-poll-question-choices---'+pollId.toString()).html('<p id="askbypoll-thankyou-message"> Thank you for your vote!!!</p>');
				$('.askbypoll-embed-content-div').css('height','50px');
			}
			
			$(overlayId).toggle('slow');
			$("#askbypoll-embed-show-demographics---"+pollId).show();
		});
		$(".askbypoll-embed-poll").on( "click", ".askbypoll-embed-show-demographics", function() {
			var that = $(this);
			var pollId = $(this).attr('id').split('---')[1];
			var overlayId = "#askbypoll-embed-overlay---"+pollId;
			
			if(protectResult == 1) {
				$('#askbypoll-embed-poll-question-choices---'+pollId.toString()).html('<p id="askbypoll-thankyou-message"> Thank you for your vote!!!</p>');
				$('.askbypoll-embed-content-div').css('height','50px');
			}
			
			$(overlayId).toggle('slow');
		});

		$(".askbypoll-embed-poll").on( "click", ".askbypoll-embed-tab-radio", function() {
			var that = $(this);
			var elemId = that[0].id;
			var content_index = elemId.split("---")[1];
			var pollId = elemId.split("---")[2];
			var show_content = '#askbypoll-content---'+content_index+'---'+pollId;
			$(".askbypoll-embed-content"+pollId).hide();
			if(content_index == 2){
				$(show_content).show();
				google.setOnLoadCallback(drawAgeChart(pollId, askByPoll_age_data));
			}else if(content_index == 3){
				$(show_content).show();
				google.setOnLoadCallback(drawGenderChart(pollId, askByPoll_gender_data));
			}else if(content_index == 4){
				$(show_content).show();
				google.setOnLoadCallback(drawProfessionChart(pollId, askbypoll_prof_data));
			}else if(content_index == 5){
                $(show_content).show();
				google.setOnLoadCallback(drawProfessionChart(pollId, askbypoll_country_data));
            }else {
				$(show_content).show();	
			}
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
			  // backgroundColor: {'stroke':'#666', 'strokeWidth':'2'},
			  pieHole: 0.4,
    		  legend:'bottom'
			};

			if(protectResult == 0){
				var chart = new google.visualization.PieChart(document.getElementById("askbypoll-agechart---"+pollId));
				chart.draw(data, options);
			} else {
				$('#askbypoll-agechart---'+pollId.toString()).html('<p id="askbypoll-thankyou-message"> Thank you for your vote!!!</p>');
				$('.askbypoll-embed-content-div').css('height','50px');
			}
	  	}
	  	function drawGenderChart(pollId, gender_dic) {
			var data = google.visualization.arrayToDataTable([
			  ['Task', 'Hours per Day'],
			  ['Male', gender_dic["M"]],
			  ['Female',gender_dic["F"]],
			  ['Not Say', gender_dic["D"]]
			]);
			var options = {
			  // 'backgroundColor': 'transparent',
			  pieHole: 0.4,
              legend:'bottom',
               // backgroundColor: {'stroke':'#666', 'strokeWidth':'2'}
			};

			if(protectResult == 0){
				var chart = new google.visualization.PieChart(document.getElementById("askbypoll-genderchart---"+pollId));
				chart.draw(data, options);
			} else {
				$('#askbypoll-genderchart---'+pollId.toString()).html('<p id="askbypoll-thankyou-message"> Thank you for your vote!!!</p>');
				$('.askbypoll-embed-content-div').css('height','50px');
			}
		}
		function drawProfessionChart(pollId, prof_dic) {
			var profData = [['Profession','Votes']];
			for(prof in prof_dic)
				profData.push([prof,prof_dic[prof]]);
			var data = google.visualization.arrayToDataTable(profData);
			var options = {
			  // 'backgroundColor': 'transparent',
			   pieHole: 0.4,
               legend:'bottom',
               // backgroundColor: {'stroke':'#666', 'strokeWidth':'2'},
			};

			if(protectResult == 0){
				var chart = new google.visualization.PieChart(document.getElementById("askbypoll-professionchart---"+pollId));
				chart.draw(data, options);
			} else {
				$('#askbypoll-professionchart---'+pollId.toString()).html('<p id="askbypoll-thankyou-message"> Thank you for your vote!!!</p>');
				$('.askbypoll-embed-content-div').css('height','50px');
			}
		}
		function drawRegionsMap(pollId, country_dic) {
			var conData = [['Country', 'Votes']];
			for(con in country_dic){
				conData.push([con,country_dic[con]]);
			}
			var data = google.visualization.arrayToDataTable(conData);
			var options = {
				//'backgroundColor': 'transparent',
				//backgroundColor: {'strokeWidth':'2'},
				'height':'700px'
			};

			if(protectResult == 0){
				var chart = new google.visualization.GeoChart(document.getElementById('askbypoll-regions_div---'+pollId));
				chart.draw(data, options);
			} else {
				$('#askbypoll-regions_div---'+pollId.toString()).html('<p id="askbypoll-thankyou-message"> Thank you for your vote!!!</p>');
				$('.askbypoll-embed-content-div').css('height','50px');
			}
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
