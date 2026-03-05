from django.core.management.base import BaseCommand
from django.utils import timezone
from polls.models import Question, Choice


class Command(BaseCommand):
    help = "Add example data into the database"
    DATA = [
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
            "question": "There are too many brackets in JavaScript?",
            "choices": ["Yes", "No, but acually yes"],
        },
    ]

    def handle(self, *args, **options):
        for q in self.DATA:
            question = Question.objects.create(
                question_text=q["question"], pub_date=timezone.now()
            )

            for choice in q["choices"]:
                Choice.objects.create(question=question, choice_text=choice, votes=0)

        self.stdout.write(
            self.style.SUCCESS("Data added successfully into the database.")
        )
