from django.shortcuts import render, reverse, Http404
from django.views import generic
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template import loader
from django.core import signing
from user.models import CustomUser
from . import forms


class SigningMixin(object):
    salt = 'password_recovery'

    def check_signing(self, token):
        token_lifetime = 3600 * 72
        try:
            signing.loads(token, salt=self.salt, max_age=token_lifetime)
        except signing.SignatureExpired:
            return False
        except signing.BadSignature:
            raise Http404

    def activate_user(self, token):
        try:
            user = CustomUser.objects.get(pk=signing.loads(token, salt=self.salt))
            user.is_active = True
            user.save()
        except signing.BadSignature:
            raise Http404

    def get_user(self, token):
        return CustomUser.objects.get(pk=signing.loads(token, salt=self.salt))


class SendEmailMixin(object):

    def send_password_recovery_email(self):
        context = {'site': get_current_site(self.request),
                   'user': self.user,
                   'token': signing.dumps(self.user.pk, salt=self.salt)}
        body = loader.render_to_string('password/password_recovery_text', context).strip()
        subject = 'Password recovery'

        send_mail(subject, body, 'test-site', [self.user.email], fail_silently=False)


class PasswordRecoveryView(SigningMixin, SendEmailMixin, generic.FormView):
    form_class = forms.PasswordRecoveryForm
    user = None
    template_name = 'password/password_recovery.html'

    def get_success_url(self):
        return reverse('password-recovery-sent')

    def form_valid(self, form):
        self.user = form.user
        self.send_password_recovery_email()


class PasswordReset(SigningMixin, generic.FormView):
    form_class = forms.PasswordResetForm
    template_name = 'password/password_reset.html'
    token = None

    def get_success_url(self):
        return reverse('login-page')

    def form_valid(self, form):
        user = self.get_user(self.token)
        user.set_password(form.cleaned_data.get('new_password_2'))
        user.save()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        self.token = kwargs['token']
        self.check_signing(self.token)
        return super().dispatch(request, *args, **kwargs)


class PasswordChangeView(generic.FormView):
    form_class = forms.PasswordChangeForm
    template_name = 'password/password_change.html'

    def get_success_url(self):
        return '/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.user.set_password(form.cleaned_data.get('new_password_2'))
        form.user.save()
        return super().form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PasswordRecoverySent(generic.TemplateView):
    template_name = 'password/password_recovery_sent.html'
