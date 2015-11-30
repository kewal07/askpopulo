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
newScript.src = 'http://www.google.com/jsapi';
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
    jQuery(document).ready(function($) { 
    	setTimeout(function(){google.load('visualization', '1', {'callback':'', 'packages':['corechart']})}, 1000);
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
			var pollId = $(this).attr('id').split('---')[1];
			var jsonp_url = "https://www.askbypoll.com/embed-poll?pollId="+pollId+"&callback=?";
			var that = $(this);
			var alreadyVoted = getAskByPollCookie('ASKBYPOLL_VOTED_'+pollId);
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
		});
		$(".askbypoll-embed-poll").on( "click", ".askbypoll-embed-poll-question-choice-text", function(event) {
			var pollId = $(this).parent().parent().attr("id").split('---')[1];
			var alreadyVoted = getAskByPollCookie('ASKBYPOLL_VOTED_'+pollId);
			console.log(alreadyVoted,typeof alreadyVoted);
			console.log(pollId, typeof pollId)
			
			if(alreadyVoted == 'true'){
				console.log("propagation stopped");
				event.stopPropagation();
			} else {
				var a = new Date();
				a = new Date(a.getTime() +1000*60*60*24);
				document.cookie = 'ASKBYPOLL_VOTED_'+pollId+'='+true+'; expires='+a.toGMTString()+';path=/'; 
				
				var choiceId = $(this).attr("id").split('---')[1];
				var alreadyVoted = getAskByPollCookie('ASKBYPOLL_VOTED');
				console.log(alreadyVoted);
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
					$("#askbypoll-embed-poll-question-choices---"+pollId).css("opacity","0.5");
				});
			}
		});
		
		$(".askbypoll-embed-poll").on( "click", ".askbypoll-embed-poll-question-choice-img", function(event) {
			var choiceId = $(this).attr("id").split('---')[1];
			var pollId = $(this).parent().parent().attr("id").split('---')[1];
			var alreadyVoted = getAskByPollCookie('ASKBYPOLL_VOTED_'+pollId);

			if(alreadyVoted == 'true'){
				event.stopPropagation();
			} else {
				var a = new Date();
				a = new Date(a.getTime() +1000*60*60*24);
				document.cookie = 'ASKBYPOLL_VOTED_'+pollId+'='+true+'; expires='+a.toGMTString()+';path=/'; 
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
					$("#askbypoll-embed-poll-question-choices---"+pollId).css("opacity","0.5");
					//$("#askbypoll-embed-overlay---"+pollId).toggle("slow");
				});
			}
		});
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
})();