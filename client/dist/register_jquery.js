$(document).ready(function(){


    $('[data-modal= register]').on('click', function(){
        $('.overlay, #register').fadeIn();
    });

    $('[data-modal= game]').on('click', function(){
        $('.overlay, #game').fadeIn();
    });

    $('.modal__close').on('click', function(){
        $('.overlay, #sign, #register, #game').fadeOut();
    });

    let link = document.querySelector('.sign-up');

    link.addEventListener('click', () => {
        $('.overlay, #sign').fadeIn();
        $('#register').fadeOut();
    });

    jQuery(($) => {
        $('.settings__select').on('click', '.settings__select__head', function () {
            if ($(this).hasClass('open')) {
                $(this).removeClass('open');
                $(this).next().fadeOut();
            } else {
                $('.settings__select__head').removeClass('open');
                $('.settings__select__list').fadeOut();
                $(this).addClass('open');
                $(this).next().fadeIn();
            }
        });
    
        $('.settings__select').on('click', '.settings__select__item', function () {
            $('.settings__select__head').removeClass('open');
            $(this).parent().fadeOut();
            $(this).parent().prev().text($(this).text());
            $(this).parent().prev().prev().val($(this).text());
        });
    });

    $('ul.game__play__tabs').on('click', 'li:not(.game__play__tab_active)', function(){
        $(this)
        .addClass('game__play__tab_active').siblings().removeClass('game__play__tab_active')
        .closest('div.game__play').find('div.game__play__content').removeClass('game__play__content_active').eq($(this).index()).addClass('game__play__content_active');
    } )
});