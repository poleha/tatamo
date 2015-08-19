from django.forms.models import ModelForm
from django.forms import HiddenInput, TextInput, Textarea
from contact_form.models import ContactForm
from discount.models import UserProfile

class ContactFormModel(ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None and user.is_authenticated():
            profile = UserProfile.get_profile(user)
            self.fields['name'].initial = "{0} {1}".format(user.first_name, user.last_name)
            #self.fields['name'].widget = HiddenInput()
            self.fields['email'].initial = user.email
            #self.fields['email'].widget = HiddenInput()
            self.fields['phone'].initial = profile.phone
            #self.fields['phone'].widget = HiddenInput()
            self.instance.user = user

        self.fields['name'].widget = TextInput(attrs={'placeholder': 'Ваше имя'})
        self.fields['email'].widget = TextInput(attrs={'placeholder': 'Email'})
        self.fields['phone'].widget = TextInput(attrs={'placeholder': 'Телефон'})
        self.fields['body'].widget = Textarea(attrs={'placeholder': 'Сообщение'})


    class Meta:
        model = ContactForm
        exclude = ['status', 'user', 'created']
