/* Load this script using conditional IE comments if you need to support IE 7 and IE 6. */

window.onload = function() {
	function addIcon(el, entity) {
		var html = el.innerHTML;
		el.innerHTML = '<span style="font-family: \'icomoon\'">' + entity + '</span>' + html;
	}
	var icons = {
			'icon-file-pdf' : '&#x66;',
			'icon-file-word' : '&#x77;',
			'icon-file-excel' : '&#x6c;',
			'icon-file-powerpoint' : '&#x73;',
			'icon-file-zip' : '&#x7a;',
			'icon-plus' : '&#x2b;',
			'icon-cancel' : '&#x78;',
			'icon-minus' : '&#x2d;',
			'icon-expenses' : '&#x3c;',
			'icon-incomes' : '&#x3e;',
			'icon-programme' : '&#x70;',
			'icon-budget' : '&#x42;',
			'icon-search' : '&#x53;',
			'icon-term' : '&#x54;',
			'icon-glossary' : '&#x47;',
			'icon-calendar' : '&#x43;',
			'icon-aportacion' : '&#x63;',
			'icon-policy' : '&#x50;',
			'icon-home' : '&#x48;',
			'icon-checkmark' : '&#x76;',
			'icon-feed' : '&#x72;',
			'icon-loop' : '&#x21;',
			'icon-comparison' : '&#x22;'
		},
		els = document.getElementsByTagName('*'),
		i, attr, c, el;
	for (i = 0; ; i += 1) {
		el = els[i];
		if(!el) {
			break;
		}
		attr = el.getAttribute('data-icon');
		if (attr) {
			addIcon(el, attr);
		}
		c = el.className;
		c = c.match(/icon-[^\s'"]+/);
		if (c && icons[c[0]]) {
			addIcon(el, icons[c[0]]);
		}
	}
};