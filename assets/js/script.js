$(document).ready(function(){
	//$('input[type=text], textarea').bind('keypress', function (event) {
	//    var regex = new RegExp("^[a-zA-Z0-9]+$");
	//    var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
	//    if (!regex.test(key)) {
	//       event.preventDefault();
	//       return false;
	//    }
	//});

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
				console.log($this.parent().children().first());
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

	$('.fileLabel').click(function(){
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
		if(divElemId === "notifications"){
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
		}
		if(divElemId === "myABPInboxDiv"){
			console.log("nbox Loaded for user");
			$("#myABPInboxDiv").html('<object id="inboxObject" data="/messages/inbox/" style="height:25rem; width:100%;"/>');
			$("#myABPInboxDiv").toggle();
		}
		else{
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
	openOverlay(olEl);
	return yesnoconfirm(url);
}
