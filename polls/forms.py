from django.forms import HiddenInput, ModelForm, ModelChoiceField
from django.forms.widgets import RadioChoiceInput, RadioSelect
from polls import models




class VoteForm(ModelForm):
    class Meta:
        model = models.Vote
        fields = ['answer', 'poll']
    answer = ModelChoiceField(queryset=models.Answer.objects.all(), widget=RadioSelect(), required=True, empty_label=None)

    def __init__(self, poll=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['poll'].widget = HiddenInput()
        self.fields['answer'].queryset = poll.answer_set
        #self.fields['answer'].empty_label = None
