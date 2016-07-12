$(document).ready(function(){
	// survey common start
	$('#surveys-content').on("click",'.fileLabel',function(){
		$(this).prev().children().first().click();
	});

	$("#surveys-content").on("click",".add-demographics",function(){
		var question_elem = '<div class="survey-demographic-div" id="demographicDiv'+demographic_count+'">';
		question_elem += '<i id="remove-demographic' +demographic_count+ '" class="fa fa-times-circle remove-demographic"> Remove</i>';
		question_elem += '<p class="form-p"><label for="demographic_name'+demographic_count+'">Name</label><input type="text" id ="demographic_name'+demographic_count+'" name="demographic_name'+demographic_count+'" placeholder="Demographic Name" maxlength="64"></input></p>';
		question_elem += '<p class="form-p"><label for="demographic_values'+demographic_count+'">Description</label><textarea id ="demographic_values'+demographic_count+'" name="demographic_values'+demographic_count+'" placeholder="Comma Separated Values Leave empty for text input" maxlength="400"></textarea></p>';
		demographic_list.push(demographic_count);
		demographic_count += 1;
		$(".survey-demographics").append(question_elem);
	});

	$("#surveys-content").on("click",".remove-demographic",function(){
		var elemId = $(this)[0].id;
		var demographic_count_select = elemId.replace("remove-demographic","");
		$("#demographicDiv"+demographic_count_select).remove();
		demographic_list = jQuery.grep(demographic_list, function(value) {
		  return value != demographic_count_select;
		})
	});

	$("#surveys-content").on("click",".add-sections",function(){
		$(".survey-sections").toggle();
	});

	$("#surveys-content").on("change","select#qSection",function(){
		// var noOfSections = +'$("select#qSection option:selected" ).val()';
		$(".survey-sec").remove();
		var noOfSections = $("select#qSection option:selected").val();
		var i;
		for (i = 1; i <= parseInt(noOfSections); i++) { 
			var element = '<input type="text" class="survey-sec" id="sectionName---'+i+'" name="sectionName---'+i+'" placeholder="Section '+i+'" maxlength="64">';
			$(".survey-sections").append(element);
		}
	});

	$("#surveys-content").on("click",".add-q",function(){
  		choice_count[question_count] = 1;
  		choice_list[question_count] = [];
  		var question_count_str = question_count.toString();
  		question_list.push(question_count_str);
  		var question_elem = '<div class="survey-question-div" id="questionDiv'+question_count_str+'">';
  		question_elem += '<i id="remove-question' +question_count_str+ '"class="fa fa-times-circle remove-question"> Remove</i><p class="form-p"> Question <span class="display_question_count">'+display_question_count+'</span>:</p><p class="form-p"><label class=" required" for="qText';
  		question_elem += question_count_str;
  		question_elem += '">Question</label><textarea id ="qText';
  		question_elem += question_count_str;
  		question_elem += '" name="qText';
  		question_elem += question_count_str;
  		question_elem += '" placeholder="Ask the people" maxlength="200"></textarea></p><p class="form-p"><label for="qDesc';
  		question_elem += question_count_str;
  		question_elem += '">Description</label><textarea id ="qDesc';
  		question_elem += question_count_str;
  		question_elem += '" name="qDesc';
  		question_elem += question_count_str;
  		question_elem += '" placeholder="Description" maxlength="400"></textarea></p>';
  		if(mandatorySurvey)
  			question_elem += '<p class="anonymous"><input id="mandatory' +question_count_str+ '" name="mandatory' +question_count_str+ '" type="checkbox" checked><label for="mandatory' +question_count_str+ '">Mandatory </label></p>';
  		else
  			question_elem += '<p class="anonymous"><input id="mandatory' +question_count_str+ '" name="mandatory' +question_count_str+ '" type="checkbox"><label for="mandatory' +question_count_str+ '">Mandatory </label></p>';
  		if(protectedResultSurvey)
  			question_elem += '<p class="anonymous" style="margin-top:1rem"><input id="protectResult' +question_count_str+ '" name="protectResult' +question_count_str+ '" type="checkbox" checked><label for="protectResult' +question_count_str+ '">Protect Result </label></p>';
  		else
  			question_elem += '<p class="anonymous" style="margin-top:1rem"><input id="protectResult' +question_count_str+ '" name="protectResult' +question_count_str+ '" type="checkbox"><label for="protectResult' +question_count_str+ '">Protect Result </label></p>';
  		if(addCommentSurvey)
  			question_elem += '<p id="addComment' +question_count_str+ 'p" class="anonymous" style="display:none;margin-top:1rem"><input id="addComment' +question_count_str+ '" name="addComment' +question_count_str+ '" type="checkbox" checked><label for="addComment' +question_count_str+ '">Require Feedback </label></p>';
  		else
  			question_elem += '<p id="addComment' +question_count_str+ 'p" class="anonymous" style="display:none;margin-top:1rem"><input id="addComment' +question_count_str+ '" name="addComment' +question_count_str+ '" type="checkbox"><label for="addComment' +question_count_str+ '">Require Feedback </label></p>';
  		if(horizontalOptions)
  			question_elem += '<p class="anonymous" style="margin-top:1rem"><input id="horizontalOptions' +question_count_str+ '" name="horizontalOptions' +question_count_str+ '" type="checkbox" checked><label for="horizontalOptions' +question_count_str+ '">Arrange Options Horizontaly </label></p>';
  		else
  			question_elem += '<p class="anonymous" style="margin-top:1rem"><input id="horizontalOptions' +question_count_str+ '" name="horizontalOptions' +question_count_str+ '" type="checkbox"><label for="horizontalOptions' +question_count_str+ '">Arrange Options Horizontaly </label></p>';
  		question_elem += '<p class="form-p"><label for="qSect---'+question_count_str+'">Section</label><select class="qSect" id="qSect---'+question_count_str+'" name="qSect---'+question_count_str+'">';
  		var noOfSections = $("select#qSection option:selected").val();
  		var i;
  		for (i = 0; i <= parseInt(noOfSections); i++) { 
  			question_elem += '<option value="'+$("#sectionName---"+i).val()+'">'+$("#sectionName---"+i).val()+'</option>';
  		}
  		question_elem += '</select></p>';
  		question_elem += '<p class="form-p"><label for="qType';
  		question_elem += question_count_str;
  		// change for radio default start
  		question_elem += '">Question Type</label><select class="question-type-select" id="question-type-select'+question_count_str+'" name="qType'+question_count_str+'"><option value="radio">Single Select</option><option value="checkbox">Multi Select</option><option value="rating">Rating</option><option value="text">Text</option><option value="matrixrating">Matrix / Rating Scale</option></select></p>';
  		question_elem += '<div id="question'+question_count_str+'choiceDiv"><i id="' +question_count_str+'---radio" class="fa fa-plus-circle add-choice"> Add Another</i></div>'
  		// change for radio default end
  		question_elem += '</div>';
  		$(".survey-questions").append(question_elem);
  		// change for radio default start
  		add_another_choice(question_count,"radio");
  		$("#addComment"+question_count_str+"p").show();
  		// change for radio default end
  		question_count += 1;
  		display_question_count += 1;
  		var id="#questionDiv"+question_count_str;
  		$('html, body').animate({
	        scrollTop: $(id).offset().top-120
	    }, 1000);
  	});

	$("#surveys-content").on("click",".remove-choice",function(){
		var elemId = $(this)[0].id;
		var question_count_select2 = elemId.split("---")[0];
		var question_choice_count2 = elemId.split("---")[1];
		var selectedType2 = elemId.split("---")[2];
		$("#questionDiv"+question_count_select2+"choice"+question_choice_count2+"Div").remove();
		choice_list[question_count_select2] = jQuery.grep(choice_list[question_count_select2], function(value) {
		  return value != question_choice_count2;
		})
		if(choice_list[question_count_select2].length < max_choices + 1){
			if ($("#"+question_count_select2+'---'+selectedType2).length > 0) {
			    $("#"+question_count_select2+'---'+selectedType2).show();
			}
		}
	});
	
	$("#surveys-content").on("click",".remove-column",function(){
		var elemId = $(this)[0].id;
		var question_count_select2 = elemId.split("---")[0];
		var question_column_count2 = elemId.split("---")[1];
		var selectedType2 = elemId.split("---")[2];
		$("#questionDiv"+question_count_select2+"column"+question_column_count2+"Div").remove();
		column_list[question_count_select2] = jQuery.grep(column_list[question_count_select2], function(value) {
		  return value != question_column_count2;
		})
		if(column_list[question_count_select2].length < max_choices + 1){
			if ($("#"+question_count_select2+'---'+selectedType2).length > 0) {
			    $("#"+question_count_select2+'---'+selectedType2).show();
			}
		}
	});

	$("#surveys-content").on("change",".question-type-select",function(){
			var select_elem_id = $(this)[0].id;
			var question_count_select = select_elem_id.replace("question-type-select","");
			choice_count[question_count_select] = 1;
			choice_list[question_count_select] = [];
			var question_choice_count = choice_count[question_count_select];
			var choice_elem_div = "question"+question_count_select+"choiceDiv";
		var column_elem_div = "question"+question_count_select+"columnDiv";
			var question_div = "questionDiv"+question_count_select;
		$("#"+choice_elem_div).remove();
			var selectedType = $("#"+select_elem_id+" option:selected").val();

		  	if(selectedType === 'matrixrating'){
				var add_another_choice_elem = '<div id="'+choice_elem_div+'" class="matrix-row"></div>';
				var add_another_column_elem = '<div id="'+column_elem_div+'" class="matrix-column"></div>';
				column_count[question_count_select] = 1;
				column_list[question_count_select] = [];
				
				$("#"+question_div).append(add_another_choice_elem);
				$("#"+question_div).append(add_another_column_elem);
				
				$("#"+choice_elem_div).append('<p> Rows </p>');
				$("#"+choice_elem_div).append('<i id="' +question_count_select+'---'+selectedType + '" class="fa fa-plus-circle add-choice"> Add Another</i>');
				add_another_choice(question_count_select,selectedType);
				$("#"+column_elem_div).append('<p> Columns </p>');
				$("#"+column_elem_div).append('<i id="' +question_count_select+'---'+selectedType + '" class="fa fa-plus-circle add-column"> Add Another</i>');
				//add_another_choice(question_count_select,selectedType);
			} else if(selectedType != "text" && selectedType != "rating") {
				var add_another_choice_elem = '<div id="'+choice_elem_div+'"></div>';
				$("#"+question_div).append(add_another_choice_elem);
				$("#"+choice_elem_div).append('<i id="' +question_count_select+'---'+selectedType + '" class="fa fa-plus-circle add-choice"> Add Another</i>');
				add_another_choice(question_count_select,selectedType);
			}
			if(selectedType == "rating"){
				var add_another_choice_elem = '<div id="'+choice_elem_div+'"></div>';
				$("#"+question_div).append(add_another_choice_elem);
				$("#"+choice_elem_div).append('<input type="text" class="min-max-values" name="'+question_count_select+'---'+selectedType+'---Min" id="'+question_count_select+'---'+selectedType+'---Min" placeholder="Minimum Value"/><input type="text" class="min-max-values" name="'+question_count_select+'---'+selectedType+'---Max" id="'+question_count_select+'---'+selectedType+'---Max" placeholder="Maximum Value"/>');
			}

			if(selectedType == "radio"){
				$("#addComment"+question_count_select+"p").show();
			} else {
				$("#addComment"+question_count_select+"p").hide();
			}
	});
	
	$("#surveys-content").on("click",".add-column",function(){
		var elemId = $(this)[0].id;
		var question_count_select1 = elemId.split("---")[0];
		var selectedType1 = elemId.split("---")[1];
		if(column_list[question_count_select1].length < max_choices + 1){
			var question_column_count = column_count[question_count_select1];
			column_list[question_count_select1].push(question_column_count);
			var column_elem_div = "question"+question_count_select1+"columnDiv";
			var question_div = "questionDiv"+question_count_select1;
			var column_elem_id = question_div+'column'+question_column_count;
			var font_awesome_str = "";
			var column_elem = "";
			column_elem += '<div id="'+column_elem_id+'Div"><p class="form-p">'+ font_awesome_str;
			column_elem += '<label class="label-width" for="'+column_elem_id+'"></label><input id="'+column_elem_id;
			column_elem += '" class="createPollText" type="text" name="'+column_elem_id+'" placeholder="Column Label" maxlength="200">';
			column_elem += '<i id="' +question_count_select1+'---'+ question_column_count+'---'+selectedType1+ '" class="fa fa-times-circle remove-column"> Remove</i></p></div>';
			$("#"+column_elem_div).append(column_elem);
			column_count[question_count_select1]+=1;
		}
		
		if(column_list[question_count_select1].length >= max_choices + 1){
			$("#"+question_count_select1+'---'+selectedType1).hide();
		}
	});

	$("#surveys-content").on("click",".add-choice",function(){
		var elemId = $(this)[0].id;
		var question_count_select1 = elemId.split("---")[0];
		var selectedType1 = elemId.split("---")[1];
		add_another_choice(question_count_select1,selectedType1);
		if(choice_list[question_count_select1].length >= max_choices + 1){
			$("#"+question_count_select1+'---'+selectedType1).hide();
		}
	});

	$("#surveys-content").on("click",".remove-question",function(){
		var elemId = $(this)[0].id;
		var question_count_select3 = elemId.replace("remove-question","");
		$("#questionDiv"+question_count_select3).remove();
		question_list = jQuery.grep(question_list, function(value) {
		  return value != question_count_select3;
		})
		delete choice_list[question_count_select3];
		var refresh_display_count = 1;
		$(".display_question_count").each(function(i){
			$(this)[0].innerHTML = refresh_display_count;
			refresh_display_count += 1;
		});
		display_question_count = refresh_display_count;
	});

	$("#surveys-content").on("click","#protectResult",function(){
		protectedResultSurvey = !protectedResultSurvey;
		var checked = false;
		if($("#protectResult").is(':checked'))
			checked = true;
		for(var i=0; i<question_list.length; i++){
			$("#protectResult"+question_list[i]).prop( "checked", checked );
		}
	});

	$("#surveys-content").on("click","#mandatory",function(){
		mandatorySurvey = !mandatorySurvey;
		var checked = false;
		if($("#mandatory").is(':checked'))
			checked = true;
		for(var i=0; i<question_list.length; i++){
			$("#mandatory"+question_list[i]).prop( "checked", checked );
		}
	});

	$("#surveys-content").on("click","#addComment",function(){
		addCommentSurvey = !addCommentSurvey;
		var checked = false;
		if($("#addComment").is(':checked'))
			checked = true;
		for(var i=0; i<question_list.length; i++){
			$("#addComment"+question_list[i]).prop( "checked", checked );
		}
	});

	$("#surveys-content").on("click","#horizontalOptions",function(){
		horizontalOptions = !horizontalOptions;
		var checked = false;
		if($("#horizontalOptions").is(':checked'))
			checked = true;
		for(var i=0; i<question_list.length; i++){
			$("#horizontalOptions"+question_list[i]).prop( "checked", checked );
		}
	});
	// survey common end
});

function add_another_choice(question_count_select,selectedType)
{
	if(choice_list[question_count_select].length < max_choices + 1){
		var question_choice_count = choice_count[question_count_select];
		choice_list[question_count_select].push(question_choice_count);
		var choice_elem_div = "question"+question_count_select+"choiceDiv";
		var question_div = "questionDiv"+question_count_select;
		var choice_elem_id = question_div+'choice'+question_choice_count;
		var choice_file_id = question_div+'choice'+question_choice_count+'file';
		var font_awesome_str = "";
		var choice_elem = "";
		if(selectedType === "radio"){
			font_awesome_str = "";
		} else if(selectedType === "checkbox"){
			font_awesome_str = "";
		}

		if(selectedType === 'matrixrating'){
			choice_elem += '<div id="'+choice_elem_id+'Div"><p class="form-p">'+ font_awesome_str;
			choice_elem += '<label class="label-width" for="'+choice_elem_id+'"></label><input id="'+choice_elem_id;
			choice_elem += '" class="createPollText" type="text" name="'+choice_elem_id+'" placeholder="Row Label" maxlength="200">';
			choice_elem += '<i id="' +question_count_select+'---'+ question_choice_count+'---'+selectedType+ '" class="fa fa-times-circle remove-choice"> Remove</i></p></div>';
			$("#"+choice_elem_div).append(choice_elem);
		} else if(selectedType != "text"){
			choice_elem += '<div id="'+choice_elem_id+'Div"><p class="form-p">'+ font_awesome_str;
			choice_elem += '<label class="label-width" for="'+choice_elem_id+'"></label><input id="'+choice_elem_id;
			choice_elem += '" class="createPollText" type="text" name="'+choice_elem_id+'" placeholder="Enter Choice" maxlength="200">';
			choice_elem += '<input id="'+choice_file_id+'" class="fileButtonClass" type="file" name="'+choice_elem_id+'" accept="image/*">';
			choice_elem += '<i id="' +question_count_select+'---'+ question_choice_count+'---'+selectedType+ '" class="fa fa-times-circle remove-choice"> Remove</i></p></div>';
			// console.log($("#"+choice_elem_div),choice_elem);
			$("#"+choice_elem_div).append(choice_elem);
		}
		choice_count[question_count_select]+=1;

		/*For file browse */
		var invisible = $('<div/>').css({height:0,width:0,'overflow':'hidden','display':'inline-block'});
		var label = $('<div class="fileLabel btn"><img class="upImg" style="display:none;"><span id="upImgText">Upload Image</span></div>');
		var fileInput = $("#"+choice_file_id).after(label).wrap(invisible);

		fileInput.change(function(){
			$this = $(this);
			var fileVal = $this.val();
			var fileNameIndex = fileVal.lastIndexOf("\\") + 1;
			var fileName = fileVal.substr(fileNameIndex);
			if (this.files && this.files[0]) {
			var reader = new FileReader();
			reader.onload = function (e) {
				imgSrc = e.target.result;
						$this.parent().next().children().first().attr('src', e.target.result);
						$this.parent().next().children().first().show();
			}
			reader.readAsDataURL(this.files[0]);
			}
				$this.parent().next().children().first().next().hide();
			$this.parent().parent().children().first().next().attr("placeholder", "Describe your image");
		});
		/* End of file browse*/
	}
	$("#surveys-content").on("click",".surveySubmit",function(event){
		event.preventDefault();
		var elemid = "#create-survey-form";
		var form_data = new FormData($(elemid)[0]);
		console.log(form_data);
		var ajax_url = $elemid.attr('action');
		form_data.append('question_count', JSON.stringify(question_list));
		form_data.append('choice_count', JSON.stringify(choice_list));
		form_data.append('column_count', JSON.stringify(column_list));
		form_data.append('demographic_count', JSON.stringify(demographic_list));
		$("#createSurveySubmit").attr("disabled","disabled");
		console.log(form_data);
		$.ajax(
		{
			type: 'POST',
			url:"/create_survey",
			data:form_data,
			processData: false,
			contentType: false,
			success:function(obj)
			{
				$(".errorlist").remove();
				if(obj.hasOwnProperty("success")){
					$('#dashboard-surveys-tab').trigger("click");
					display_question_count = 1;
					featureImageWrapped = false;
					question_count = 1;
					demographic_count = 1;
					question_list = [];
					demographic_list = [];
					choice_count = {};
					choice_list = {};
					column_count = {};
					column_list = {};
					protectedResultSurvey = false;
					addCommentSurvey = false;
					mandatorySurvey = false;
					horizontalOptions = false;
				}
				else{
					for(var key in obj){
					    if (obj.hasOwnProperty(key)){
					    	if(key === "surveyError")
						        $(".create-survey").children().first().prepend('<span class="errorlist errorlistSurvey error-survey"><br>'+obj[key]+'</span>');
						   	else{
						   		$("#"+key).parent().append('<span class="errorlist errorlistSurvey"><br>'+obj[key]+'</span>');
						   	}
					    }
					}
					$("#createSurveySubmit").removeAttr("disabled");
				}
			}
		});
	});
}