$(document).ready(function () {
    var article_list = $('#article-list');

    article_list.on('mouseenter', '.article', function () {
        $(this).find('.panel-heading').css('color', '#AA3939');
    });
    article_list.on('mouseleave', '.article', function () {
        $(this).css('color', 'black');
        $(this).find('.panel-heading').css('color', 'black');
    });
    article_list.on('click', '.article', function () {
        var link = '/article/' + $(this).data('pk');
        $(location).attr('href', link);
    });

});
