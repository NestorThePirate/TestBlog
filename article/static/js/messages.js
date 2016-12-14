$(document).ready(function () {
   $('.message').on('click', function (e) {
       $(this).find('.message-details').slideToggle();
       $(this).find('.panel-heading').css('background-color', '#EDEDED');
       var url = window.location.pathname  + '/' + $(this).closest('.message').data('id');
       $.ajax({type: 'GET',
               url: url,
               dataType: 'json',
               success: function (response) {
                   $('#messages-counter').html(response.messages_counter);
                   $('#sidebar-messages').html(response.sidebar_update);
               },
               error: function (xhr, errmsg, err) {
                alert(xhr.status + ": " + xhr.responseText);}})
   });

    $('.delete-message').on('click', function (e) {
        e.preventDefault();
        var url = $(this).attr('href');
        var message = $(this).parent();
        $.ajax({
            type: 'GET',
            url: url,
            dataType: 'json',
            success : function (response) {
                message.remove();
                $('#sidebar-messages').html(response.sidebar_update);
                $('#messages-counter').html(response.messages_counter);
            },
            error: function (xhr, errmsg, err) {
                alert(xhr.status + ": " + xhr.responseText);}
        })
    })
});
