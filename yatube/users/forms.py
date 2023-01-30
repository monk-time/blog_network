from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError

from posts.models import User


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise ValidationError('Этот адрес уже зарегистрирован')
        return self.cleaned_data['email']
