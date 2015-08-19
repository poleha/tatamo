from django import template
from polls.forms import VoteForm
from polls.models import Poll, Vote
from django.core.urlresolvers import reverse

register = template.Library()

@register.inclusion_tag('polls/poll_detail.html', takes_context=True)
def show_poll(context, poll_pk):
    result_context = {}
    user = context['request'].user
    try:
        poll = Poll.objects.get(pk=poll_pk)
    except:
        return

    if user.is_authenticated():
        voted = Vote.objects.filter(user=user, poll=poll).exists()
    else:
        session_key = context['request'].session.session_key
        voted = Vote.objects.filter(session_key=session_key, poll=poll).exists()
    if not voted:
        form = VoteForm(poll=poll, initial={'poll': poll})
        result_context['poll'] = poll
        result_context['form'] = form
        result_context['submit_url'] = reverse('polls:poll-view', kwargs={'pk': poll.pk})
        result_context['render_scripts'] = True
    result_context['voted'] = voted
    return result_context

