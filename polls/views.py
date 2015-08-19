from django.views import generic
from polls import models
from polls.forms import VoteForm
from django.core.urlresolvers import reverse
from django.http import HttpResponse

class PollView(generic.TemplateView):
    #model = models.Poll
    #context_object_name = 'poll'
    template_name = 'polls/poll_detail.html'
    #http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']

    def get_poll(self, **kwargs):
        if not hasattr(self, 'poll'):
            pk = kwargs['pk']
            self.poll = models.Poll.objects.get(pk=pk)
        return self.poll


    def post(self, request, *args, **kwargs):
        poll = self.get_poll(**kwargs)
        form = VoteForm(poll=poll, data=self.request.POST)
        if form.is_valid():
            answer = form.cleaned_data.get('answer')
            #answer = models.Answer.objects.get(pk=answer_pk)

            user = request.user

            if user.is_authenticated():
                voted = models.Vote.objects.filter(user=user, poll=poll).exists()
            else:
                session_key = request.session.session_key
                voted = models.Vote.objects.filter(session_key=session_key, poll=poll).exists()

            if voted:
                return HttpResponse('Вы уже голосовали. Спасибо!')
            else:
                vote = models.Vote()
                vote.poll = poll
                vote.answer = answer
                if user.is_authenticated():
                    vote.user = user
                else:
                    vote.session_key = session_key
                vote.save()
                return HttpResponse('Спасибо!')
        else:
            return self.render_to_response(self.get_context_data(form=form))


    #Not used
    """
    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        poll = self.get_poll(**kwargs)
        if form is None:
            form = VoteForm(poll=poll, initial={'poll': poll})
        context['poll'] = poll
        context['form'] = form
        context['submit_url'] = reverse('polls:poll-view', kwargs={'pk': poll.pk})
        return context
    """






