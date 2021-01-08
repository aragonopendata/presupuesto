$(document).ready(function(){
	// Breakpoints
	$(window).setBreakpoints({
		// use only largest available vs use all available
		distinct: true,
		// array of widths in pixels where breakpoints should be triggered
		breakpoints: [320, 480, 768, 1024]
	});
	$(window).setBreakpoints();
	

	// Use cookies to check is user arrives to 'articulo' from 'politicas' or 'resumen'
	if ($('body').hasClass('body-summary')) {
		$.cookie('resumen', 1);

	} else if ($('body').hasClass('body-policies')) {
		var cookie = $.cookie('resumen');
		if( cookie && cookie === '1' ){
			$('.history-back a').attr('href', '/resumen').html('← Volver');
			$.removeCookie('resumen');
		}

	} else {
		$.removeCookie('resumen');
	}

	// Initialice tooltips at Budget Indicators
	$('#totals_panel .icon-question').tooltip();

	// Support a 'chrome-less' mode to improve the look of the site when embedded via iframe.
	// Just add a query parameter 'embedded', with any value, and the chrome-less model will be
	// enabled. A cookie is set for the remainder of the session so we don't have to pollute
	// all the app links to carry the query parameter around.
	queryParameters = $.deparam.querystring();
	if ( typeof queryParameters.embedded != 'undefined' ) {
		$.cookie('embedded', 1);	// Set a cookie to remember we are embedded
	}
	if ( $.cookie('embedded')==='1' ) {
		$('.hide-when-embedded').hide();
	}


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
//	 addProjectLabel(2016);
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

//función que añade un titulo de antención a los proyectos de presupuesto del año dado por parametro
function addProjectLabel(year){
	var url = window.location;
	if (url.pathname.indexOf('politicas')>0){
		var anio = $('div.jslider-value span ').html();
		if (anio == year){
			if ($('div.projectLabel').length==0){
				$('h1.main-title').before('<div class="projectLabel" style="float: right; margin-top: 35px;">Presupuestos</div>');
			}
		}
		else{
			if ($('div.projectLabel').length>0){
				$('div.projectLabel').remove();
			}
		}
	}
}
