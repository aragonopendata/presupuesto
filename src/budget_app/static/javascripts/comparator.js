$(document).ready(function() {
	//
	// 1. Sugerir la comparación entre entidades (municipio o comarca)
	//
	// Ocultar form + Meter Select2
	$(".comparator__form").hide().find("select").select2();
	
	// Abrir / Cerrar form
	$('.comparator__cta').toggle(
		function(){
			$(this).closest(".comparator").addClass("active");
			$(this).next(".comparator__form").show();
		},
		function(){
			$(this).closest(".comparator").removeClass("active");
			$(this).next(".comparator__form").hide();
		}
	);
});