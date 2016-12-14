function display_form_errors(error, form) {
    for (var e in error){
        $('#errors-list').prepend(error[e]).fadeIn();
    }
}


$(document).ready(function () {
   $(document).on('click', '.comment-answer', function (e) {
       e.preventDefault();
       if ($(this).text() == 'Отмена'){
           $(this).parent().find('#comment-form').remove();
           $(this).html('Ответить');
       }
       else{
           $(this).parent().append($('#comment-form').clone(true));
           $(this).html('Отмена');
       }
   });

    $(document).on('click', '.answer-submit', function (e) {
        e.preventDefault();
        var url = '/article/' + $('.article-details').data('obj-id');
        var form = $(this).parent();
        $.ajax({type: 'POST',
                url: url,
                data: form.serialize(),
                dataType:'json',
                success: function (response) {
                    $('#errors-list').empty();
                    if ('error' in response){
                        form.find('error').remove();
                        display_form_errors(response.error, form);
                    }
                    else {
                        var comment = $('<li class="comment" data-comment-id=' + response.pk + '>');
                        var panel_default = $('<div class="panel panel-default"></div>');
                        var panel_heading = $('<div class="panel-heading">' + response.user + ' ' + response.created + '</div>');
                        var panel_body = $('<div class="panel-body">' + response.text + '</div>');
                        var panel_footer = $('<div class="panel-footer"><button type="submit" class="btn btn-primary btn-sm comment-answer">Ответить</button> </div>');

                        panel_default.append(panel_heading).append(panel_body).append(panel_footer);
                        comment.append(panel_default);
                        if ('parent_pk' in response){
                            $("li[data-comment-id='" + response.parent +"']").append('<ul class=children>' + comment + '</ul>');
                        }
                        else{
                            $('#comments-section').append(comment);
                            form.trigger('reset');
                        }

                    }

                },
                error: function (xhr, errmsg, err) {alert(xhr.status + ": " + xhr.responseText);}})
    });

    $('.delete-comment').on('click', function (e) {
        e.preventDefault();
        var url = '/comment/delete/' + $(this).closest('.comment').data('comment-id');
        var comment = $(this).closest('.comment');
        $.ajax({type: 'GET',
                url: url,
                dataType: 'json',
                success: function (response) {
                    comment.remove();
                    alert(response.text);},
                error: function (xhr, errmsg, err) {alert(xhr.status + ": " + xhr.responseText);}})
    });

    $('.subscribe').on('click', function (e) {
        e.preventDefault();
        var url = '/subscribe/' + $('.article-details').data('obj-id');
        $.ajax({type: 'GET',
                url: url,
                dataType: 'json',
                success: function (response) {
                    $('.subscribe').html(response.message).css('color', 'black');
                },
                error: function (xhr, errmsg, err) {alert(xhr.status + ": " + xhr.responseText);}})
    })
});
