from allauth.account.views import SignupView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView

from .forms import CustomSignupForm
from .models import CustomUser


# Create your views here.
class SuperuserSignupView(LoginRequiredMixin, UserPassesTestMixin, SignupView):
    form_class = CustomSignupForm

    def dispatch(self, request, *args, **kwargs):
        # Allow only superusers to access the signup view even if they are logged in
        if request.user.is_authenticated and not request.user.is_superuser:
            return self.handle_already_logged_in()
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        # Only allow superusers to access the view
        return self.request.user.is_superuser

class UserDetailView(DetailView):
    model = CustomUser
    template_name = 'user_detail.html'  # Template for listing documents
    context_object_name = 'user'
