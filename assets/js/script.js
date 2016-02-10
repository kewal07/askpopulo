$(document).ready(function(){

	$("#id_categories").addClass("clearfix");
	
	if($(window).width() <= 960){
		$("#verticalTab").addClass("responsiveStats");
		$("#tabContentResponsive").show();
	}
	if($(window).width() > 960){
		/* for expiry date */
		var cnt = $(".newDateForm").contents();
		$(".newDateForm").remove();
		$("label[for='qExpiry']").parent().append(cnt);
		/* end */
	}
	/*gender css for responsive view*/
	// console.log($("label[for='id_gender_0']").parent().children().first().next());
	// $("label[for='id_gender_0']").parent().children().first().next().css({"display":"inline-block !important","width":"33% !important"});
	$("label[for='id_gender_0']").parent().children().first().next().addClass("first_Gender");
	/*end*/
	
	/*For file browse */
	var invisible = $('<div/>').css({height:0,width:0,'overflow':'hidden','display':'inline-block'});
	var label = $('<div class="fileLabel"><img class="upImg" ><span id="upImgText">Upload Image</span></div>');
	// var upImg = $('<img id="upImg" width=>')
	var fileInput = $(":file").after(label).wrap(invisible);
	$(".upImg").hide();

	fileInput.change(function(){
		// $('#upImgText').hide();
	    $this = $(this);
	    var fileVal = $this.val();
    	var fileNameIndex = fileVal.lastIndexOf("\\") + 1;
    	var fileName = fileVal.substr(fileNameIndex);
    	if (this.files && this.files[0]) {
            var reader = new FileReader();
            
            reader.onload = function (e) {
                imgSrc = e.target.result;
				//console.log($this.parent().children().first());
				// $(".upImg").attr('src', e.target.result);
				$this.parent().next().children().first().attr('src', e.target.result);
				// $(".upImg").show();
				$this.parent().next().children().first().show();
            }
            
            reader.readAsDataURL(this.files[0]);
        }
		// $("#upImgText").text(fileName);
		$this.parent().next().children().first().next().hide();
    	$this.parent().parent().children().first().next().attr("placeholder", "Describe your image");
	})

	$('body').on('click','.fileLabel',function(){
	    $(this).prev().children().first().click();
	});
	/* End of file browse*/

	/* For changing border color of the selected radio image */
	$(".choices").click(function(){
		// console.log($(".choices.choice_image#"+$(this)[0].id)[0]);
		$(".choice_image").css({"border-color":"#666"});
		($(".choice_image#"+$(this)[0].id)[0]).style.borderColor="#00FF00";
	});
	/* End of changing image border color */

	/* Dropdownbox on click of user image in nav */
	// $('.userInNav').click(function(){
	// 	$('.dropDownLoc').hide();
	// 	// $('.dropDownNot').hide();
	// 	$('.dropDownBox').slideToggle("slow");
	// });
	$('.menuResponsive').click(function(){
		$('.dropDownLoc').hide();
		// $('.dropDownNot').hide();
		$('.dropDownBox').slideToggle("slow");
	});
	$('.location_select').click(function(){
		$('.dropDownBox').hide();
		// $('.dropDownNot').hide();
		$('.dropDownLoc').slideToggle("slow");
	});
	$(".userInNav").click(function(){
		// console.log("notification click")
		var elem_pos = $(this).offset();
		$('.dropDownLoc').hide();
		// $('.dropDownBox').hide();
		$(".dropDownBox").slideToggle("slow");
		
	});
	/* end of Dropdownbox on click of user image in nav */

	$(".location_link").bind("click",function(){
		// console.log("link clicked");
		var new_location = $(this)[0].innerHTML;
		document.cookie = "location=" + new_location + "; path=/";
	    $(".location_link").unbind("click");
		// return false;
	});
	
	/* Overlay */
	/* close overlay call */
	$("#okay").click(function(){
		closeOverlay();
	});
	/* close overlay call end */

	$('#id_categories').hide();
	$('#id_categories').prev().append("<span id='cats'>Please Click here to expand and select your categories</span>");
	$('#id_categories').prev().on('click', '#cats', function() {
    	$('#id_categories').toggle();
  	});

  	$("#category_tooltip_fa").hover(function(e){
  		// console.log($(this));
  		var elem_pos = $(this).offset();
  		// console.log(elem_pos.top,elem_pos.left);
  		$("#category_tooltip").css({
  			"top":elem_pos.top-100,
  			"left":elem_pos.left-60,
  		});
  		$("#category_tooltip").toggle();
  	});

  	$("#groups_tooltip_fa").hover(function(e){
  		// console.log($(this));
  		var elem_pos = $(this).offset();
  		// console.log(elem_pos.top,elem_pos.left);
  		$("#groups_tooltip").css({
  			"top":elem_pos.top-100,
  			"left":elem_pos.left-60,
  		});
  		$("#groups_tooltip").toggle();
  	});

  	$("#featuredimage_tooltip_fa").hover(function(e){
  		// console.log($(this));
  		var elem_pos = $(this).offset();
  		// console.log(elem_pos.top,elem_pos.left);
  		$("#featuredimage_tooltip").css({
  			"top":elem_pos.top-100,
  			"left":elem_pos.left-60,
  		});
  		$("#featuredimage_tooltip").toggle();
  	});

  	$("#private_poll_fa").hover(function(e){
  		// console.log("category_tooltip");
  		var elem_pos = $(this).offset();
  		// console.log(elem_pos.top,elem_pos.left);
  		$("#private_poll_tooltip").css({
  			"top":elem_pos.top-100,
  			"left":elem_pos.left-60,
  			"width":"30%",
  		});
  		$("#private_poll_tooltip").toggle();
  	});
  	$("#protectResult_fa").hover(function(e){
  		// console.log("category_tooltip");
  		var elem_pos = $(this).offset();
  		// console.log(elem_pos.top,elem_pos.left);
  		$("#protectResult_tooltip").css({
  			"top":elem_pos.top-100,
  			"left":elem_pos.left-60,
  			"width":"30%",
  		});
  		$("#protectResult_tooltip").toggle();
  	});
  	$("#makeFeatured_fa").hover(function(e){
  		// console.log("category_tooltip");
  		var elem_pos = $(this).offset();
  		// console.log(elem_pos.top,elem_pos.left);
  		$("#makeFeatured_tooltip").css({
  			"top":elem_pos.top-100,
  			"left":elem_pos.left-60,
  			"width":"30%",
  		});
  		$("#makeFeatured_tooltip").toggle();
  	});

	/*help*/
	$(".helpChardin").click(function(e){
		e.preventDefault();
		$('html, body').animate({ scrollTop: 0 }, 'slow');
		$('body').chardinJs('start');
	});
	/*end*/
	
	/* agreement in sign up page */
	var agreement_label = '<label class="agreement_label" for="id_agreement">I have read and agree with the <a class="agreement_anchor" href="/static/AskByPollTermsofUse.docx" target="_blank">Terms of Use</a> and <a class="agreement_anchor" href="/static/ASKBYPOLLPrivacyPolicies.docx" target="_blank">Privacy</a></label>'
	$("#id_agreement").parent().append(agreement_label);
	/* end */

	/* activate menu link */
	activateMenuLink();
	/* end */

	/* description on hover */
	if($(window).width() > 960){
		$(".qTextDesc").hover(function(){
			var elem=$(this)[0];
			if($("#"+elem.id).next().text().length > 0)
				$("#"+elem.id).next().toggle();
		});
	}
	/* end */

	/* clean old time */
	$("#clearOldExpiryTimefa").click(function(){
		// console.log($("#oldExpiryTimespan")[0].innerHTML);
		$("#oldExpiryTimespan")[0].innerHTML = "None";
		$("#oldExpiryTimeinput").attr("value","clean");
	});
	/* end */

	$(".myProfileTabs").click(function(){
		var elemId = $(this)[0].id;
		console.log("profile tabs clicked");
		console.log(elemId);
		$(".profileDetail").hide();
		// var divElemId = "." + elemId + "Div";
		var divElemId = elemId + "Div";
		$(".profileDetail").hide();
		$(".detailHeader h1").text(headerText[elemId]);
		// $(divElemId).slideToggle("slow");
		if(divElemId === "myABPInboxDiv"){
			console.log("nbox Loaded for user");
			$("#myABPInboxDiv").html('<object id="inboxObject" data="/messages/inbox/" style="height:25rem; width:100%;"/>');
			$("#myABPInboxDiv").toggle();
		}
		else{
			if(divElemId === "notificationsDiv"){
				$("#notification_count_span")[0].innerHTML = 0;
				// $("#notification_count_span").hide();
		  		$.ajax(
				{
					type: 'GET',
					url:"/user/notifications_read",
					// data:$(elemid).serialize(),
					success:function(response)
					{
						console.log("marked read");
					}
				});     
			}
			var new_elem_html = "";
			var path = location.pathname;
			$.ajax({
		        url: path,
		        type: 'GET',
		        async: false,
		        cache: false,
		        timeout: 30000,
		        error: function(){
		            return true;
		        },
		        success: function(msg){
		        	var new_html = document.createElement('html');
		        	new_html.innerHTML = msg;
		        	// console.log(new_html);
		        	// console.log(typeof(new_html));
		        	// console.log(new_html.getElementsByTagName("div"));
		        	var new_divs = new_html.getElementsByTagName("div");
		        	for (var i = 0, len = new_divs.length; i < len; i++) {
					    if (new_divs[i].id === divElemId) {
					        var result = new_divs[i];
					        // console.log(result)
					        new_elem_html = result.innerHTML;
					        break;
					    }
					}
					// console.log($("#"+divElemId));
		            $("#"+divElemId)[0].innerHTML = new_elem_html;
		            // console.log($("#"+divElemId));
		            // $(".admin-dash-div").hide();
		            $("#"+divElemId).slideToggle("slow");
		        }
		    });
		}
		if($(window).width() < 960){
			$(".profileStats").slideToggle("slow");
			$(".fa-arrow-left").show();
		}
	});

	$(".user_not_credit_message_li").click(function(){
		console.log("clicked li");
		var elemId = $(this)[0].id;
		console.log(elemId);
		var profile_path = $("#profile_page_url_in_common")[0].href;
		console.log(profile_path);
		// history.pushState('data', '', profile_path);
		// var new_elem_html = "";
		// var path = location.pathname;
		if(elemId === "common_notifications"){
			document.cookie = "public_profile=notifications; path=/";
			$("#notification_count_span")[0].innerHTML = 0;
			$("#notification_count_span").hide();
	  		$.ajax(
			{
				type: 'GET',
				url:"/user/notifications_read",
				// data:$(elemid).serialize(),
				success:function(response)
				{
					console.log("marked read");
				}
			});     
			console.log("open notifications");
			// profileLoadDiv("notifications");
			// $("#notifications")[0].click();
		}else if(elemId === "common_credits"){
			document.cookie = "public_profile=myCredits; path=/";
			console.log("open credits");
			// profileLoadDiv("myCredits");
			// $("#myCredits")[0].click();
		}else if(elemId === "common_inbox"){
			document.cookie = "public_profile=myABPInbox; path=/";
			console.log("open inbox");
			// profileLoadDiv("myABPInbox");
			// $("#myABPInbox")[0].click();
		}
		var profile_page = window.open(profile_path,"_top");
	});

	$('.fa-envelope').click(function(){
		openOverlay("#overlay-inAbox4");
	});
	$('body').on("click",".fa-envelope",function(){
		console.log("open message block");
		openOverlay("#overlay-inAbox4");
	});
});

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
    }
    return "";
}

// function ajaxindicatorstart(text)
// {
// 	if(jQuery('body').find('#resultLoading').attr('id') != 'resultLoading'){
// 	jQuery('body').append('<div id="resultLoading" style="display:none"><div><img src="ajax-loader.gif"><div>'+text+'</div></div><div class="bg"></div></div>');
// 	}

// 	jQuery('#resultLoading').css({
// 		'width':'100%',
// 		'height':'100%',
// 		'position':'fixed',
// 		'z-index':'10000000',
// 		'top':'0',
// 		'left':'0',
// 		'right':'0',
// 		'bottom':'0',
// 		'margin':'auto'
// 	});

// 	jQuery('#resultLoading .bg').css({
// 		'background':'#000000',
// 		'opacity':'0.7',
// 		'width':'100%',
// 		'height':'100%',
// 		'position':'absolute',
// 		'top':'0'
// 	});

// 	jQuery('#resultLoading>div:first').css({
// 		'width': '250px',
// 		'height':'75px',
// 		'text-align': 'center',
// 		'position': 'fixed',
// 		'top':'0',
// 		'left':'0',
// 		'right':'0',
// 		'bottom':'0',
// 		'margin':'auto',
// 		'font-size':'16px',
// 		'z-index':'10',
// 		'color':'#ffffff'

// 	});

//     jQuery('#resultLoading .bg').height('100%');
//        jQuery('#resultLoading').fadeIn(300);
//     jQuery('body').css('cursor', 'wait');
// }

// function ajaxindicatorstop()
// {
//     jQuery('#resultLoading .bg').height('100%');
//        jQuery('#resultLoading').fadeOut(300);
//     jQuery('body').css('cursor', 'default');
// }

// jQuery(document).ajaxStart(function () {
//  		//show ajax indicator
// ajaxindicatorstart('Please give us a moment while we Make Sense of Millions of Bits for You !');
// }).ajaxStop(function () {
// //hide ajax indicator
// ajaxindicatorstop();
// });


function activateMenuLink () {
	$( ".menuanchor" ).each(function( ) {
		elemHref = $(this)[0].href;
		windowHref = window.location.href;
		if(windowHref.indexOf("?") != -1)
			windowHref = windowHref.substr(0,windowHref.indexOf("?"));
		if(windowHref == elemHref)
			$(this).addClass('anchoractive');
	});
}
function openOverlay(olEl) {
	toppx = 130;
	if(olEl === "#overlay-inAbox3")
		toppx = 100;
	$oLay = $(olEl);
	if ($('#overlay-shade').length == 0)
		$('body').prepend('<div id="overlay-shade"></div>');
	$('#overlay-shade').fadeTo(300, 0.6, function() {
		// var props = {
			// //oLayWidth       : $oLay.width(),
			// scrTop          : $(window).scrollTop(),
			// viewPortWidth   : $(window).width()
		// };
	$oLay.css({
			display : 'block',
			opacity : 0,
			});
	$oLay.animate({
			top : toppx,
			opacity : 1
			}, 600);
	});
}

function closeOverlay() {
	$('.overlay').animate({
		top : '-=300',
		opacity : 0
	}, 400, function() {
		$('#overlay-shade').fadeOut(300);
		$(this).css('display','none');
	});
}
/* End Overlay */

function yesnoconfirm(url){
	$("#yes").click(function(){
		closeOverlay();
		window.location.href = url;
	});
	$("#no").click(function(){
		closeOverlay();
		return false;
	});
}

function confirm_redirect(olEl,val,url){
	$oLay = $(olEl);
	console.log(url);
	// console.log(val);
	if (val === "delete_question"){
		console.log($oLay.children().children().first()[0])
		$oLay.children().children().first()[0].innerHTML = "You Sure Want to Delete the Poll??";
	}
	if (val === "delete_survey"){
		console.log($oLay.children().children().first()[0])
		$oLay.children().children().first()[0].innerHTML = "You Sure Want to Delete the Survey??";
	}
	openOverlay(olEl);
	return yesnoconfirm(url);
}

function confirm_redirect_only(olEl,val,url){
	$oLay = $(olEl);
	console.log(url);
	// console.log(val);
	$oLay.children().children().first()[0].innerHTML = val;
	openOverlay(olEl);
	$("#okay_redirect").click(function(){
		closeOverlay();
		window.location.href = url;
	});
}

/* Function for charts start */
function drawPollsChart(csrf_token,analyse_type,pollId,age,gender,profession,location,state, graphType) {
	// console.log(analyse_type,pollId,age,gender,profession,location);
	var pollsData = [];
	var pollsDataExtra = [];
	var pollsColors = ["#F7464A","#46BFBD","#66FF33","#FF6600"];
	var colCount = 0;
	var advanced_analyse_dic = {};
	if (typeof graphType === "undefined" || graphType === null) { 
	    graphType = ""; 
	}
	if (typeof age === "undefined" || age === null) { 
	    age = "nochoice"; 
	}
	if (typeof gender === "undefined" || gender === null) { 
	    gender = "nochoice"; 
	}
	if (typeof profession === "undefined" || profession === null) { 
	    profession = "nochoice"; 
	}
	if (typeof location === "undefined" || location === null) { 
	    location = "nochoice"; 
	}
	if (typeof state === "undefined" || state === null) { 
	    state = "nochoice"; 
	}
	$.ajax({
        url: "/advanced_analyse",
        type: 'POST',
        data: { question: pollId,
        		age: age,
        		gender: gender,
        		profession: profession,
        		country: location,
        		state: state,
        		csrfmiddlewaretoken: csrf_token
        	},
        async: false,
        cache: false,
        timeout: 30000,
        error: function(){
            return true;
        },
        success: function(msg){
        	// console.log(msg);
        	advanced_analyse_dic=msg;
        }
    });
	pollsData.push(['Element', 'Votes', { role: 'style' }, { role: 'annotation' }]);
	pollsDataExtra.push(['Element', 'Votes', { role: 'style' }, { role: 'annotation' }]);
	for(var choice in advanced_analyse_dic['choices']){
		var inData = [];
		var inDataExtra = [];
		var choice_dic = advanced_analyse_dic['choices'][choice];
		inData.push(choice_dic["key"]);
		inData.push(choice_dic["val"]);
		inDataExtra.push(choice_dic["key"]);
		inDataExtra.push(choice_dic["extra_val"]);
		// inData.push(choice['val']);
		inData.push(pollsColors[colCount]);
		inDataExtra.push(pollsColors[colCount++]);
		var percent = 0;
		var percentExtra = 0;
		if(advanced_analyse_dic['total_votes'] > 0)
			percent = Math.round((choice_dic["val"]/advanced_analyse_dic['total_votes'])*100);
			// percent = Math.round((choice["val"]/advanced_analyse_dic['total_votes'])*100);
		if(advanced_analyse_dic['total_votes_extra'] > 0)
			percentExtra = Math.round((choice_dic["extra_val"]/advanced_analyse_dic['total_votes_extra'])*100);
		inData.push(percent+"%");
		inDataExtra.push(percentExtra+"%");
		pollsData.push(inData);
		pollsDataExtra.push(inDataExtra);
		// console.log(inData);
	}
	var data = google.visualization.arrayToDataTable(pollsData);
	// set a padding value to cover the height of title and axis values
	// var paddingHeight = 10;// * data.getNumberOfRows();
	// set the height to be covered by the rows
	var rowHeight = data.getNumberOfRows() * 40;
	// set the total chart height
	var chartHeight = rowHeight ;//+ paddingHeight;
	var dataExtra = google.visualization.arrayToDataTable(pollsDataExtra);
	var options = {
          chartArea: {left:80,width: '60%',height:'100%'},
          height: chartHeight,
          fontSize:14,
          bars: {
            groupWidth: '100%'
          },
          annotations:{
          	textStyle: {
		      opacity: 0         // The transparency of the text.
		    }	        
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
              duration: 2000,
              easing: 'inAndOut',
         },
        };
	var optionsCol = {
          chartArea: {width: '95%'},
          fontSize:14,
          bars: {
            groupWidth: 100
          },
          annotations:{
          	textStyle: {
		      opacity: 0         // The transparency of the text.
		    }	        
          },
          hAxis: {
            title: '',
            minValue: 0,
            gridlines: {
              color: 'transparent'
              },
            // textPosition: 'none',
            // baselineColor: 'transparent'
          },
          vAxis: {
            title: '',
            gridlines: {
              color: 'transparent'
              },
            textPosition: 'none',
            baselineColor: 'transparent'
          },
          legend:{
              position:'none'
          },
           animation:{
              startup:true,
              duration: 2000,
              easing: 'inAndOut',
         },
        };
        var chart = "";
        if(graphType != ""){
        	// console.log(analyse_type+'pollsChart---'+pollId+'---'+graphType);
        	if(document.getElementById(analyse_type+'pollsChart---'+pollId+'---'+graphType) != null){
        		chart = new google.visualization.ColumnChart(document.getElementById(analyse_type+'pollsChart---'+pollId+'---'+graphType));
        		chart.draw(data, optionsCol);
        	}
        }else{
        	chart = new google.visualization.BarChart(document.getElementById(analyse_type+'pollsChart---'+pollId));
        	chart.draw(data, options);
        }
        google.visualization.events.addListener(chart, 'animationfinish', displayAnnotation);
        $("#polls-votes-count---"+pollId)[0].innerHTML =  advanced_analyse_dic['total_votes'] + " Votes";
        $("#advanced-polls-votes-count---"+pollId)[0].innerHTML =  advanced_analyse_dic['total_votes'] + " Votes";
        if(advanced_analyse_dic['total_votes'] != advanced_analyse_dic['total_votes_extra'] && document.getElementById(analyse_type+'pollsChart---'+pollId+'---extra') != null){
        	$("#advanced-ana-bar-graph-1---"+pollId).show();
        	$("#advanced-ana-bar-graph-2---"+pollId).show();
        	$("#advanced-ana-bar-graph-1---"+pollId).html("Results With All Responses : "+advanced_analyse_dic['total_votes_extra']);
        	$("#advanced-ana-bar-graph-2---"+pollId).html("Results Which Have Demographic Data : "+advanced_analyse_dic['total_votes']);
        	var chartExtra = new google.visualization.BarChart(document.getElementById(analyse_type+'pollsChart---'+pollId+'---extra'));
	        chartExtra.draw(dataExtra, options);
	        google.visualization.events.addListener(chartExtra, 'animationfinish', displayAnnotation);
        }  

    function displayAnnotation(e){
        data = google.visualization.arrayToDataTable(pollsData);
        options = {
          chartArea: {left:80,width: '60%',height:'100%'},
          fontSize:14,
          height:chartHeight,
          bars: {
            groupWidth: '100%'
          },
          annotations:{
          	textStyle: {
		      opacity: 1         // The transparency of the text.
		    }	        
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
        optionsCol = {
          chartArea: {width: '95%'},
          fontSize:14,
          bars: {
            groupWidth: 100
          },
          annotations:{
          	textStyle: {
		      opacity: 1         // The transparency of the text.
		    }	        
          },
          hAxis: {
            title: '',
            minValue: 0,
            gridlines: {
              color: 'transparent'
              },
            // textPosition: 'none',
            // baselineColor: 'transparent'
          },
          vAxis: {
            title: '',
            gridlines: {
              color: 'transparent'
              },
            textPosition: 'none',
            baselineColor: 'transparent'
          },
          legend:{
              position:'none'
          },
           animation:{
              startup:true,
              duration: 2000,
              easing: 'inAndOut',
         },
        };
		if(graphType != ""){
        	chart.draw(data, optionsCol);
        }else{
        	chart.draw(data, options);
        }
        if(advanced_analyse_dic['total_votes'] != advanced_analyse_dic['total_votes_extra'] && document.getElementById(analyse_type+'pollsChart---'+pollId+'---extra') != null){
        	dataExtra = google.visualization.arrayToDataTable(pollsDataExtra);
	        chartExtra.draw(dataExtra, options);
        }  
    }
}

function drawGenderChart(csrf_token,analyse_type,pollId,choiceId,graphId) {
  var genderData = [['Gender', 'Votes']];
  if(typeof choiceId == 'undefined' || choiceId === null)
  	choiceId = "nochoice"
  if(typeof graphId == 'undefined')
  	graphId = ""
  else
  	graphId = "---"+graphId
  var advanced_analyse_dic = {};
  $.ajax({
        url: "/advanced_analyse_choice",
        type: 'POST',
        data: { question: pollId,
        		choice: choiceId,
        		csrfmiddlewaretoken: csrf_token
        	},
        async: false,
        cache: false,
        timeout: 30000,
        error: function(){
            return true;
        },
        success: function(msg){
        	// console.log(msg);
        	advanced_analyse_dic=msg;
        }
    });
  var m = advanced_analyse_dic['gender']['M'];
  var f = advanced_analyse_dic['gender']['F'];
  var d = advanced_analyse_dic['gender']['D'];
  
  if(m>0)
  	genderData.push(['Male',m]);
  if(f>0)
  	genderData.push(['Female',f]);
  if(d>0)
  	genderData.push(['Not Disclosed',d])
  var data = google.visualization.arrayToDataTable(genderData);
  var options = {
    pieHole: 0.4,
    legend:'bottom'
  };

  // console.log(analyse_type+'genderChart---'+pollId+graphId);
  if(document.getElementById(analyse_type+'genderChart---'+pollId+graphId) != null){
	  var chart = new google.visualization.PieChart(document.getElementById(analyse_type+'genderChart---'+pollId+graphId));
	  chart.draw(data, options);
	}
}

function drawAgeChart(csrf_token,analyse_type,pollId,choiceId,graphId) {
  var ageData = [['Age Group', 'Votes']];
  if(typeof choiceId == 'undefined' || choiceId === null)
  	choiceId = "nochoice"
  if(typeof graphId == 'undefined')
  	graphId = ""
  else
  	graphId = "---"+graphId
  var advanced_analyse_dic = {};
  $.ajax({
        url: "/advanced_analyse_choice",
        type: 'POST',
        data: { question: pollId,
        		choice: choiceId,
        		csrfmiddlewaretoken: csrf_token
        	},
        async: false,
        cache: false,
        timeout: 30000,
        error: function(){
            return true;
        },
        success: function(msg){
        	// console.log(msg);
        	advanced_analyse_dic=msg;
        }
    });
  var under_19 = advanced_analyse_dic['age']['under_19'];
  var bet_20_25 = advanced_analyse_dic['age']['bet_20_25'];
  var bet_26_30 = advanced_analyse_dic['age']['bet_26_30'];
  var bet_31_35 = advanced_analyse_dic['age']['bet_31_35'];;
  var bet_36_50 = advanced_analyse_dic['age']['bet_36_50'];
  var over_50 = advanced_analyse_dic['age']['over_50'];
  if(under_19 > 0)
  	ageData.push(['Upto 19',under_19]);
  if(bet_20_25 > 0)
  	ageData.push(['20-25',bet_20_25]);
  if(bet_26_30 > 0)
  	ageData.push(['26-30',bet_26_30]);
  if(bet_31_35 > 0)
  	ageData.push(['31-35',bet_31_35]);
  if(bet_36_50 > 0)
  	ageData.push(['36-50',bet_36_50]);
  if(over_50 > 0)
  	ageData.push(['50+',over_50]);
  var data = google.visualization.arrayToDataTable(ageData);
  var options = {
    pieHole: 0.4,
    legend:'bottom'
  };
  // console.log(analyse_type+'ageChart---'+pollId+graphId);
  if(document.getElementById(analyse_type+'ageChart---'+pollId+graphId) != null){
	  var chart = new google.visualization.PieChart(document.getElementById(analyse_type+'ageChart---'+pollId+graphId));
	  chart.draw(data, options);
	}
}

function drawOthersChart(csrf_token,analyse_type,pollId,choiceId,graphId) {
	var profDict = {};
	var profData = [['Profession','Votes']];
	if(typeof choiceId == 'undefined' || choiceId === null)
  		choiceId = "nochoice"
  	if(typeof graphId == 'undefined')
	  	graphId = ""
	  else
	  	graphId = "---"+graphId
  	var advanced_analyse_dic = {};
	$.ajax({
	    url: "/advanced_analyse_choice",
	    type: 'POST',
	    data: { question: pollId,
	    		choice: choiceId,
	    		csrfmiddlewaretoken: csrf_token
	    	},
	    async: false,
	    cache: false,
	    timeout: 30000,
	    error: function(){
	        return true;
	    },
	    success: function(msg){
	    	// console.log(msg);
	    	advanced_analyse_dic=msg;
	    }
	});
	profDict = advanced_analyse_dic["profession"];
	for(prof in profDict)
		profData.push([prof,profDict[prof]]);
	var data = google.visualization.arrayToDataTable(profData);
	var options = {
	pieHole: 0.4,
	legend:'bottom'
	};
	// console.log(analyse_type+'othersChart---'+pollId+graphId);
  	if(document.getElementById(analyse_type+'othersChart---'+pollId+graphId) != null){
		var chart = new google.visualization.PieChart(document.getElementById(analyse_type+'othersChart---'+pollId+graphId));
		chart.draw(data, options);
	}
}

var backChoiceId = "";
// var bakgraphId = "";
var backdict = {};

function drawLocationChart(csrf_token,analyse_type,pollId,choiceId,graphId) {
    // $('#mapBackButton').removeClass('back');
	var conData = [['Country', 'Votes']];
	var conDict = {};
	if(typeof choiceId == 'undefined' || choiceId === null)
  		choiceId = "nochoice"
	// console.log(typeof graphId,choiceId);
  	if(typeof graphId == 'undefined' || graphId == 'undefined')
	  	graphId = ""
	else
	  	graphId = "---"+graphId.replace("---","");
	// console.log(graphId);
	backdict[pollId+"---"+graphId] = choiceId;
	// console.log(backdict);
	
  	var advanced_analyse_dic = {};
	$.ajax({
	    url: "/advanced_analyse_choice",
	    type: 'POST',
	    data: { question: pollId,
	    		choice: choiceId,
	    		csrfmiddlewaretoken: csrf_token
	    	},
	    async: false,
	    cache: false,
	    timeout: 30000,
	    error: function(){
	        return true;
	    },
	    success: function(msg){
	    	// console.log(msg);
	    	advanced_analyse_dic=msg;
	    }
	});
	conDict = advanced_analyse_dic["country"]
	for(con in conDict){
		conData.push([con,conDict[con]]);
	}
    var data = google.visualization.arrayToDataTable(conData);
    var options = {};
    // console.log(analyse_type+'locationChart---'+pollId+graphId);
  	if(document.getElementById(analyse_type+'locationChart---'+pollId+graphId) != null){
	    var chart = new google.visualization.GeoChart(document.getElementById(analyse_type+'locationChart---'+pollId+graphId));
	    chart.draw(data, options);
	    google.visualization.events.addListener(chart, 'regionClick', function(e){
	    	$("#"+analyse_type+"mapBackButton").css("display", "inline-block");
			// $('#mapBackButton').addClass("back");
			drawStateMap(csrf_token,analyse_type,e.region,pollId,choiceId,graphId);
	    });
	}
}

var regionDict = {
	"IN":"India","AZ":"Azerbaijan","US":"USA","PK":"Pakistan","GB":"United Kingdom","AU":"Australia","CA":"Canada","PH":"Philippines","AQ":"Antartica","BB":"Barbados","DE":"Germany","SJ":"Svalbard","AF":"Afghanistan","DZ":"Algeria","AL":"Albania","AS":"American Samoa","AO":"Angola","AI":"Anguilla","AG":"Antigua and Barbuda","AR":"Argentina","AM":"Armenia","AW":"Aruba","AT":"Austria","AZ":"Azerbaijan","BS":"Bahamas","BH":"Bahrain","BD":"Bangladesh","BB":"Barbados","BY":"Belarus","BE":"Belgium","BZ":"Belize","BJ":"Benin","BR":"Brazil","BM":"Bermuda","BT":"Bhutan","BO":"Bolivia","BA":"Bosnia and Herzegovina","CN":"China","DE":"Germany","DK":"Denmark","NL":"Netherlands","PK":"Pakistan","ZW":"Zimbabwe","ZM":"Zambia","ZA":"South Africa","CH":"Switzerland","TH":"Thailand","SG":"Singapore","SE":"Sweden","TR":"Turkey","QA":"Qatar","RE":"Reunion","RO":"Romania","SA":"Saudi Arabia","RW":"Rwanda","JP":"Japan","KE":"Kenya","NO":"Norway","NP":"Nepal","PL":"Poland","NZ":"New Zealand","GB-SCT":"Scotland","EG":"Egypt"
}

function drawStateMap(csrf_token,analyse_type,region,pollId,choiceId,graphId){
	backChoiceId = choiceId;
	backdict[pollId+"---"+graphId] = choiceId;
	// console.log(backdict);
	// bakgraphId = graphId;
	var options = {
      region: region,
      displayMode: 'regions',
      resolution: 'provinces',
      datalessRegionColor: '#666',
      colorAxis: {colors: ['#FF9900', '#FFFFFF', '#00CC00']},
      backgroundColor: '#81d4fa',
      domain: 'IN'
  };
	var stateContry = regionDict[region];
	var stateData = [['State', 'Votes']];
	var stateDict = {};
	if(typeof choiceId == 'undefined')
  		choiceId = "nochoice"
  	var advanced_analyse_dic = {};
	$.ajax({
	    url: "/advanced_analyse_choice",
	    type: 'POST',
	    data: { question: pollId,
	    		choice: choiceId,
	    		stateContry: stateContry,
	    		csrfmiddlewaretoken: csrf_token
	    	},
	    async: false,
	    cache: false,
	    timeout: 30000,
	    error: function(){
	        return true;
	    },
	    success: function(msg){
	    	// console.log(msg);
	    	advanced_analyse_dic=msg;
	    }
	});
	stateDict = advanced_analyse_dic["state"]
	for(state in stateDict){
		stateData.push([state,stateDict[state]]);
	}
	// console.log(stateData)

	var data = google.visualization.arrayToDataTable(stateData);
	// console.log(analyse_type+'locationChart---'+pollId+graphId);
  	if(document.getElementById(analyse_type+'locationChart---'+pollId+graphId) != null){
		var chart = new google.visualization.GeoChart(document.getElementById(analyse_type+'locationChart---'+pollId+graphId));
		chart.draw(data, options);
	}
}
    
function back(csrf_token,analyse_type,pollId,bakgraphId){  
	$("#"+analyse_type+"mapBackButton").css("display", "none");
	if (typeof bakgraphId != "undefined"){
		backChoiceId = backdict[pollId+"------"+bakgraphId];
		bakgraphId = bakgraphId + ""
	} else{
		backChoiceId = backdict[pollId+"---"];
	}
	// console.log(bakgraphId,backChoiceId,backdict);
    drawLocationChart(csrf_token,analyse_type,pollId,backChoiceId,bakgraphId);
}
/* Function for charts end */

function getBase64Image(img, a4) {
    var canvas = document.createElement("canvas");
    canvas.width = a4[0];
    canvas.height = a4[1];
    var ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);
    var dataURL = canvas.toDataURL("image/jpeg");
    return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
}

function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}

function getQueryParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}
