// http://jsfiddle.net/mekwall/sgxKJ/

$.widget("ui.autocomplete", $.ui.autocomplete, {
    options : $.extend({}, this.options, {
        multiselect: false,
        maxselection: 5,
        elemId: ""
    }),
    _create: function(){
        this._super();
        var self = this,
        o = self.options;
        var itemsAdded = $('#'+o.elemId).val();
        

        if (o.multiselect) {
            self.selectedItems = {};           
            self.multiselect = $("<div></div>")
                .addClass("ui-autocomplete-multiselect ui-state-default ui-widget")
                .css("width", self.element.width())
                .insertBefore(self.element)
                .append(self.element)
                .bind("click.autocomplete", function(){
                    self.element.focus();
                });
				
			if(!(itemsAdded === "")){
				console.log(itemsAdded.split(","));
				$.each(itemsAdded.split(","),function(i,items){
					console.log(items);
					if(!(items === "")){
						o.maxselection--;
						$("<div></div>")
							.addClass("ui-autocomplete-multiselect-item")
							.text(items)
							.append(
								$("<span></span>")
									.addClass("ui-icon ui-icon-close")
									.click(function(){
										o.maxselection++;
										var item = $(this).parent();
										delete self.selectedItems[item.text()];
										itemsAdded=itemsAdded.replace(item.text()+",","");
										$('#'+o.elemId).val(itemsAdded);
										item.remove();
									})
							)
							.insertBefore(self.element);
					}
				});
			}
            
            var fontSize = parseInt(self.element.css("fontSize"), 10);
            function autoSize(e){
                // Hackish autosizing
                var $this = $(this);
                $this.width(1).width(this.scrollWidth+fontSize-1);
            };

            var kc = $.ui.keyCode;
            self.element.bind({
                "keydown.autocomplete": function(e){
                    if ((this.value === "") && (e.keyCode == kc.BACKSPACE)) {
                        var prev = self.element.prev();
                        delete self.selectedItems[prev.text()];
                        itemsAdded=itemsAdded.replace(prev.text()+",","");
                        $('#'+o.elemId).val(itemsAdded);
                        o.maxselection++;
                        prev.remove();
                    }
                },
                // TODO: Implement outline of container
                "focus.autocomplete blur.autocomplete": function(){
                    self.multiselect.toggleClass("ui-state-active");
                },
                "keypress.autocomplete change.autocomplete focus.autocomplete blur.autocomplete": autoSize
            }).trigger("change");
            // TODO: There's a better way?
            o.select = o.select || function(e, ui) {
                if(!(ui.item.label in self.selectedItems) && o.maxselection > 0){
                    itemsAdded = itemsAdded+(ui.item.label+",");//append(ui.item.label+",");
                    $('#'+o.elemId).val(itemsAdded);
                    o.maxselection--;
                    $("<div></div>")
                        .addClass("ui-autocomplete-multiselect-item")
                        .text(ui.item.label)
                        .append(
                            $("<span></span>")
                                .addClass("ui-icon ui-icon-close")
                                .click(function(){
                                    o.maxselection++;
                                    var item = $(this).parent();
                                    delete self.selectedItems[item.text()];
                                    itemsAdded=itemsAdded.replace(item.text()+",","");
                                    $('#'+o.elemId).val(itemsAdded);
                                    item.remove();
                                })
                        )
                        .insertBefore(self.element);
                }
                else if(o.maxselection <= 0)
                {
                    alert("Maximum number of categories selected");
                }
                self.selectedItems[ui.item.label] = ui.item;
                self._value("");
                 return false;
            }
            /*self.options.open = function(e, ui) {
                var pos = self.multiselect.position();
                pos.top += self.multiselect.height();
                self.menu.element.position(pos);
            }*/
        }
        return this;
    }
});