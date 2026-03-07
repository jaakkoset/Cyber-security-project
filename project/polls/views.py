from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Question, Choice
from . import database


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


# @login_required
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


# @require_POST
@login_required
def save_poll(request):
    """Saves the new polls into the database and redirects the user on the front page."""
    # Check that inputs are not empty
    if not (
        request.GET["question"] and request.GET["choice1"] and request.GET["choice2"]
    ):
        return render(
            request,
            "polls/create.html",
            {"error_message": "Fill the required fields"},
        )
    database.save_poll(request.GET)

    # Fix for CSRF attack
    # if not (request.POST["question"] and request.POST["choice1"] and request.POST["choice2"]):
    #     return render(
    #         request,
    #         "polls/create.html",
    #         {"error_message": "Fill the required fields"},
    #     )
    # database.save_poll(request.POST)

    return HttpResponseRedirect(reverse("polls:index"))


def login(request):
    """Login to a user account."""
    if request.method == "GET":
        return render(request, "polls/login.html")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return HttpResponseRedirect(reverse("polls:index"))
        else:
            return render(
                request,
                "polls/login.html",
                {"login_error_message": "Invalid username or password"},
            )


def signup(request):
    """Create new user accounts."""
    if request.method == "POST":
        username = request.POST["username"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if not (username and password1 and password2):
            return render(
                request,
                "polls/login.html",
                {"signup_error_message": "Username and password are required."},
            )
        if password1 != password2:
            return render(
                request,
                "polls/login.html",
                {"signup_error_message": "Passwords do not match."},
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "polls/login.html",
                {"signup_error_message": "Username already exists."},
            )

        user = User.objects.create_user(username=username, password=password1)
        auth_login(request, user)

        return HttpResponseRedirect(reverse("polls:index"))

    return HttpResponseRedirect(reverse("polls:index"))


def logout_route(request):
    logout(request)
    return HttpResponseRedirect(reverse("polls:index"))
