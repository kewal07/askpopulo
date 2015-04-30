// $(window).scroll(function() {   
//    if($(window).scrollTop() + $(window).innerHeight() == scrollHeight) {
//        alert("bottom!");
//    }
// });
/* For Fixed Header */
$(document).ready(function(){
	if ( $(window).width() > 960) {
		$(window).on('scroll', function() {
		    scrollPosition = $(this).scrollTop();
		    console.log(scrollPosition);
		    if (scrollPosition >= 10) {
		        // If the function is only supposed to fire once
		        //$(this).off('scroll');
		        //alert("bottom");
		        //check if too heavy...always detecting while scroll...maybe some way to detect once above ???
		        $("#header").attr("id","headerScroll");
		        $( ".logo img" ).addClass( "imgScroll" );
		        $( ".menu" ).addClass( "menuScroll" );
		        $( ".search" ).addClass( "searchScroll" );
		        $( ".searchBox" ).addClass( "searchBoxScroll" );
		        // Other function stuff here...
		    }
		    else{
		    	$("#headerScroll").attr("id","header");
		        $( ".logo img" ).removeClass( "imgScroll" );
		        $( ".menu" ).removeClass( "menuScroll" );
		        $( ".search" ).removeClass( "searchScroll" );
		        $( ".searchBox" ).removeClass( "searchBoxScroll" );
		    }
		});
	}
	/* End */

	/*For file browse */
	var invisible = $('<div/>').css({height:0,width:0,'overflow':'hidden','display':'inline-block'});
	var label = $('<div class="fileLabel"><img class="upImg" ><span id="upImgText">Chose file</span></div>');
	// var upImg = $('<img id="upImg" width=>')
	var fileInput = $(":file").after(label).wrap(invisible);
	$(".upImg").hide();

	fileInput.change(function(){
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
		$this.parent().next().children().first().next().text(fileName);
    	$this.parent().parent().children().first().next().attr("placeholder", "Describe your image");
	})

	$('.fileLabel').click(function(){
	    $(this).prev().children().first().click();
	});
	/* End */
});

