$(document).ready(function(){
	// Breakpoints
	$(window).setBreakpoints({
		// use only largest available vs use all available
		distinct: true,
		// array of widths in pixels where breakpoints should be triggered
		breakpoints: [320, 480, 768, 1024]
	});
	$(window).setBreakpoints();
	


	// iPhone Safari Viewport Scaling Bug
	(function(doc) {

		var addEvent = 'addEventListener',
		    type = 'gesturestart',
		    qsa = 'querySelectorAll',
		    scales = [1, 1],
		    meta = qsa in doc ? doc[qsa]('meta[name=viewport]') : [];

		function fix() {
			meta.content = 'width=device-width,minimum-scale=' + scales[0] + ',maximum-scale=' + scales[1];
			doc.removeEventListener(type, fix, true);
		}

		if ((meta = meta[meta.length - 1]) && addEvent in doc) {
			fix();
			scales = [.25, 1.6];
			doc[addEvent](type, fix, true);
		}

	}(document));

});











// Menú principal RWD
var ww = document.body.clientWidth;

$(document).ready(function() {
  $(".nav-rwd li a").each(function() {
    if ($(this).next().length > 0) {
    	$(this).addClass("parent");
		};
	})
	
	$(".main-menu-toggle").click(function(e) {
		e.preventDefault();
		$(this).toggleClass("active");
		$(".nav-rwd").toggle();
	});
	adjustMenu();
});

$(window).bind('resize orientationchange', function() {
	ww = document.body.clientWidth;
	adjustMenu();
});

var adjustMenu = function() {
	if (ww < 768) {
		// if "more" link not in DOM, add it
		if (!$(".more")[0]) {
			$('<div class="more">&nbsp;</div>').insertBefore('.parent');
		}

		$(".main-menu-toggle").css("display", "inline-block");

		if (!$(".main-menu-toggle").hasClass("active")) {
			$(".nav-rwd").hide();
		} else {
			$(".nav-rwd").show();
		}

		$(".nav-rwd li").unbind('mouseenter mouseleave');

		$(".nav-rwd li a.parent").unbind('click');

		$(".nav-rwd li .more").unbind('click').bind('click', function() {
			$(this).parent("li").toggleClass("hover");
		});
	} else if (ww >= 768) {
    	// remove .more link in desktop view
    	$('.more').remove(); 
		$(".main-menu-toggle").css("display", "none");
		$(".nav-rwd").show();
		$(".nav-rwd li").removeClass("hover");
		$(".nav-rwd li a").unbind('click');
		$(".nav-rwd li").unbind('mouseenter mouseleave').bind('mouseenter mouseleave', function() {
		 	// must be attached to li so that mouseleave is not triggered when hover over submenu
		 	$(this).toggleClass('hover');
		});
	}
};