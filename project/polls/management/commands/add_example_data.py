from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from polls.models import Question, Choice


class Command(BaseCommand):
    help = "Add example data into the database"
    POLLS = [
        {
            "question": "Do you have any questions?",
            "choices": ["No", "Yes", "*Deep silence"],
        },
        {
            "question": "Where did I leave my keys?",
            "choices": [
                "In the kitchen?",
                "Outside?",
                "In your pocket?",
                "You don't have keyes?",
            ],
        },
        {
            "question": "How are you?",
            "choices": ["Ok", "Fine. How are you?", "I'm coping"],
        },
        {"question": "Why?", "choices": ["I don't know", "Huh?"]},
        {"question": "What's up?", "choices": ["Not much", "The sky"]},
        {
            "question": "JavaScript uses too many brackets?",
            "choices": ["Yes", "No, but acually yes"],
        },
    ]
    USERS = [
        {"name": "alice", "pwd": "redqueen"},
        {"name": "bob", "pwd": "squarepants"},
    ]

    def handle(self, *args, **options):
        for poll in self.POLLS:
            question = Question.objects.create(
                question_text=poll["question"], pub_date=timezone.now()
            )

            for choice in poll["choices"]:
                Choice.objects.create(question=question, choice_text=choice, votes=0)

        for user in self.USERS:
            User.objects.create_user(username=user["name"], password=user["pwd"])

        self.stdout.write(
            self.style.SUCCESS("Data added successfully into the database.")
        )
