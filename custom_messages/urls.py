from django.conf.urls import url

from custom_messages import views

urlpatterns = [
    url(regex='^send_message/(?P<target_user>[-\w ]+)$',
        view=views.SendMessage.as_view(),
        name='send-message'),

    url(regex='^send_message/$',
        view=views.SendMessage.as_view(),
        name='send-message-custom'),

    url(regex='^(?P<username>[\w]+)/user_info/inc_messages_list$',
        view=views.PrivateMessagesIncomeListView.as_view(),
        name='private-income-messages'),

    url(regex='^(?P<username>[\w]+)/user_info/out_messages_list$',
        view=views.PrivateMessagesOutcomeListView.as_view(),
        name='private-outcome-messages'),

    url(regex='^(?P<username>[\w]+)/user_info/messages_list/(?P<pk>[0-9]+)$',
        view=views.PrivateMessageDetails.as_view(),
        name='private-message-details'),

    url(regex='^delete_message/(?P<message_id>[0-9]+)$',
        view=views.delete_private_message,
        name='delete-private-message')
]
