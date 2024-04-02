from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError

from posts.models import User


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):  # type: ignore
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def clean_email(self):
        if (
            self.cleaned_data['email']
            and User.objects.filter(email=self.cleaned_data['email']).exists()
        ):
            msg = 'Этот адрес уже зарегистрирован'
            raise ValidationError(msg)
        return self.cleaned_data['email']
