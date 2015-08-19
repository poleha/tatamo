



(function( $ ) {
	$.fn.iLightInputNumber = function() {

		var inBox = '.input-number-box';
		var newInput = '.input-number';
		var moreVal = '.input-number-more';
		var lessVal = '.input-number-less';

		this.each(function(){
			var el = $(this);
			$('<div class="'+ inBox.substr(1) +'"></div>').insertAfter( el );
			var parent = el.find('+ ' + inBox);
			parent.append(el);
			var classes = el.attr('class');
			parent.append('<input class="'+ newInput.substr(1) +'" type="text">');
			el.hide();
			var newEl = el.next();
			newEl.addClass(classes);
			var attrValue;

			function setInputAttr(attrName){
				if(el.attr(attrName)){
					attrValue = el.attr(attrName);
					newEl.attr(attrName, attrValue);
				}
			}

			setInputAttr('value');
			setInputAttr('placeholder');
			setInputAttr('min');
			setInputAttr('max');
			setInputAttr('step');

			parent.append('<div class='+ moreVal.substr(1) +'></div>');
			parent.append('<div class='+ lessVal.substr(1) +'></div>');
		});

		var value;
		var step;

		$('body').on('click', moreVal, function(){
			var el = $(this);
			var input = el.siblings(newInput);
			var max = input.attr('max');
			checkInputAttr(input);
			var newValue = value + step;
			if(newValue > max){
				newValue = max;
			}
			input.val(newValue);
			var inputNumber = el.siblings('[type=number]');
			inputNumber.val(newValue);
		});

		$('body').on('click', lessVal, function(){
			var el = $(this);
			var input = el.siblings(newInput);
			var min = input.attr('min');
			checkInputAttr(input);
			var newValue = value - step;
			if(newValue < min){
				newValue = min;
			}
			input.val(newValue);
			var inputNumber = el.siblings('[type=number]');
			inputNumber.val(newValue);
		});

		function checkInputAttr(input){
			if(input.attr('value')){
				value = parseFloat(input.attr('value'));
			}else if(input.attr('placeholder')){
				value = parseFloat(input.attr('placeholder'));
			}
			if(!( $.isNumeric(value) )){
				value = 0;
			}
			if(input.attr('step')){
				step = parseFloat(input.attr('step'));
			}else{
				step = 1;
			}
		}

		$(newInput).change(function(){
			var input = $(this);
			var value = parseFloat(input.val());
			var min = input.attr('min');
			var max = input.attr('max');
			if(value < min){
				value = min;
			} else if (value > max){
				value = max;
			}
			if(!( $.isNumeric(value) )){
				value = '';
			}
			input.val(value);
			input.siblings('[type=number]').val(value);
		});

	};
})(jQuery);

jQuery(function ($) {
	$('').iLightInputNumber();

});

$(function() {
	$('input[type="number"]').spinner({
	});
});

