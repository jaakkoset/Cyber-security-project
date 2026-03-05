from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"
    paginate_by = 10

    def get_queryset(self):
        """Return published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by(
            "-pub_date"
        )


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        # Excludes any questions that aren't published yet.
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def create(request):
    """Returns the template for the poll creation page."""
    return render(request, "polls/create.html")


# 2 CSRF attack. The below line should be enabled.
# @require_POST
def save_poll(request):
    """Saves the new polls into the database and redirects the user on the fron page."""
    # if request.method == "GET":
    #     print(request.GET["question"])
    #     print(request.GET["choice1"])
    #     print(request.GET["choice2"])
    #     print(request.GET["choice3"])
    #     print(request.GET["choice4"])
    # if request.method == "POST":
    #     print(request.POST["question"])
    #     print(request.POST["choice1"])
    #     print(request.POST["choice2"])
    #     print(request.POST["choice3"])
    #     print(request.POST["choice4"])
    return HttpResponseRedirect(reverse("polls:index"))
