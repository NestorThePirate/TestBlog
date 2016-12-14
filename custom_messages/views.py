from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import Http404, get_object_or_404, reverse, redirect
from django.views import generic
from django.http import JsonResponse
from custom_messages.forms import MessageForm
from custom_messages.models import PrivateMessage
from user.models import CustomUser


class SendMessage(generic.FormView):
    template_name = 'messages/send_message.html'
    form_class = MessageForm
    target_user = None

    def get_success_url(self):
        return reverse('private-outcome-messages', args=[self.request.user.username])

    def form_valid(self, form):
        new_message = form.save(commit=False)
        new_message.author_user = self.request.user
        new_message.user_messages_list = self.request.user.get_private_messages_list()
        new_message.save()
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if self.target_user:
            initial['target_username'] = self.target_user
        return initial

    def dispatch(self, request, *args, **kwargs):
        try:
            self.target_user = kwargs['target_user']
        except KeyError:
            pass
        if self.request.user is None:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class PrivateMessagesIncomeListView(generic.TemplateView):
    template_name = 'messages/messages_list.html'
    user = None

    def get_context_data(self, **kwargs):
        if self.request.user.username != kwargs['username']:
            raise Http404

        ctx = super().get_context_data(**kwargs)
        self.user = CustomUser.objects.get(username=kwargs['username'])
        ctx['income_messages'] = self.user.get_income_messages()
        ctx['message_obj'] = self.user.get_private_messages_list()
        return ctx


class PrivateMessagesOutcomeListView(generic.TemplateView):
    template_name = 'messages/messages_list.html'
    user = None

    def get_context_data(self, **kwargs):
        if self.request.user.username != kwargs['username']:
            raise Http404

        ctx = super().get_context_data(**kwargs)
        self.user = CustomUser.objects.get(username=kwargs['username'])
        ctx['outcome_messages'] = self.user.get_income_messages()
        ctx['message_obj'] = self.user.get_private_messages_list()
        return ctx


class PrivateMessageDetails(generic.RedirectView):
    template_name = 'messages/message_details.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            message = PrivateMessage.objects.get(pk=kwargs['pk'])
            if self.request.user != message.author_user:
                raise Http404
        except ObjectDoesNotExist:
            raise Http404
        message.checked = True
        message.save()
        if self.request.is_ajax():
            counter = self.request.user.get_private_messages_list().messages_counter()
            return JsonResponse({'messages_counter': counter,
                                 'sidebar_update': self.request.user.get_unchecked_messages()})
        return super().dispatch(request, *args, **kwargs)


def delete_private_message(request, message_id):
    message = get_object_or_404(PrivateMessage, pk=message_id)

    if request.user != message.user_messages_list.user:
        raise Http404
    message.delete()
    url = reverse('private-income-messages', args=[request.user.username])
    counter = request.user.get_private_messages_list().messages_counter()

    if request.is_ajax():
        return JsonResponse({'message': 'message deleted',
                             'sidebar_update': request.user.get_unchecked_messages(),
                             'messages_counter': counter})
    return redirect(url)
