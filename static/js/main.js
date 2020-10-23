$(document).ready(function () {
	"use strict"; // start of use strict

	/*==============================
	Header
	==============================*/
	$('.header__menu').on('click', function() {
		$('.header__menu').toggleClass('header__menu--active');
		$('.header__nav').toggleClass('header__nav--active');
	});

	/*==============================
	Carousel
	==============================*/
	$('.section__carousel').owlCarousel({
		mouseDrag: true,
		touchDrag: true,
		dots: true,
		loop: true,
		autoplay: true,
		autoplayTimeout: 6000,
		autoplayHoverPause: true,
		smartSpeed: 700,
		margin: 30,
		autoHeight: true,
		responsive : {
			0 : {
				items: 1,
			},
			576 : {
				items: 1,
			},
			768 : {
				items: 2,
			},
			992 : {
				items: 3,
			},
		}
	});

	/*==============================
	Upload img
	==============================*/
	$('.form__gallery-upload').on('change', function() {
		var length = $(this).get(0).files.length;
		var galleryLabel  = $(this).attr('data-name');

		if( length > 1 ){
			$(galleryLabel).text(length + " files selected");
		} else {
			$(galleryLabel).text($(this)[0].files[0].name);
		}
	});

	/*==============================
	Gallery
	==============================*/
	$('.article__gallery, .article__img').magnificPopup({
		fixedContentPos: true,
		type: 'image',
		closeOnContentClick: true,
		closeBtnInside: false,
		removalDelay: 300,
		mainClass: 'mfp-fade',
		image: {
			verticalFit: true
		},
		callbacks: {
			open: function() {
				if ($(window).width() > 1200) {
					$('.header').css('margin-left', "-" + (getScrollBarWidth()/2) + "px");
					$('.mfp-content').css('margin-left', "-" + getScrollBarWidth() + "px");
				}
			},
			close: function() {
				if ($(window).width() > 1200) {
					$('.header').css('margin-left', 0);
					$('.mfp-content').css('margin-left', 0);
				}
			}
		}
	});

	function getScrollBarWidth () {
		var $outer = $('<div>').css({visibility: 'hidden', width: 100, overflow: 'scroll'}).appendTo('body'),
			widthWithScroll = $('<div>').css({width: '100%'}).appendTo($outer).outerWidth();
		$outer.remove();
		return 100 - widthWithScroll;
	};

	
	
});