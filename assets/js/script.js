$(document).ready(function(){
	$("#id_categories").addClass("clearfix");
	
	if($(window).width() <= 960){
		$("#verticalTab").addClass("responsiveStats");
		$("#tabContentResponsive").show();
	}

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
	$('.userInNav').click(function(){
		$('.dropDownBox').slideToggle("slow");
	});
	$('.menuResponsive').click(function(){
		$('.dropDownBox').slideToggle("slow");
	});
	/* end of Dropdownbox on click of user image in nav */
	
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


	/*help*/
	$(".helpChardin").click(function(e){
		e.preventDefault();
		$('html, body').animate({ scrollTop: 0 }, 'slow');
		$('body').chardinJs('start');
	});
	/*end*/
});
function openOverlay(olEl) {
	console.log("In overlay");
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
			top : 130,
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