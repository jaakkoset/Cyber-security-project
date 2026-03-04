"""Run this file to delete all data in polls_question and polls_choice tables, and then
repopulate the tables. The database must exist and be named 'db.sqlite3' before running
this file."""

import sqlite3


def clear_tables(connection):
    print("Deleting old data")
    cursor = connection.cursor()
    cursor.execute(
        """
        DELETE FROM polls_choice;
    """
    )
    connection.commit()
    cursor.execute(
        """
        DELETE FROM polls_question;
    """
    )
    connection.commit()


def add_questions(connection):
    cursor = connection.cursor()

    questions = [
        ("Do you have any questions?",),
        ("Where did I leave my keys?",),
        ("How are you?",),
        ("Why?",),
        ("What's up?",),
        ("Can I go?",),
    ]

    cursor.executemany(
        """
            INSERT INTO polls_question
                (question_text, pub_date)
            VALUES
                (?, CURRENT_TIMESTAMP);
        """,
        questions,
    )

    connection.commit()


def add_choices(connection):
    cursor = connection.cursor()
    # ("id", "choice_text", "votes", "question_id")
    questions = [
        # ("Do you have any questions?",),
        ("No", 0, 1),
        ("Yes", 0, 1),
        ("*Deep silence", 0, 1),
        # ("Where did I leave my keys?",),
        ("In the kitchen?", 0, 2),
        ("Outside?", 0, 2),
        ("In your pocket?", 0, 2),
        ("You don't have keys?", 0, 2),
        # ("How are you?",),
        ("Ok", 0, 3),
        ("Fine. How are you?", 0, 3),
        ("I'm coping", 0, 3),
        # ("Why?",),
        ("I don't know", 0, 4),
        ("What?", 0, 4),
        # ("What's up?",),
        ("Not much", 0, 5),
        ("The sky", 0, 5),
        # ("Can I go?",),
        ("No. Sit down!", 0, 6),
        ("Soon", 0, 6),
        ("Prehaps", 0, 6),
    ]

    cursor.executemany(
        """
            INSERT INTO polls_choice
                (choice_text, votes, question_id)
            VALUES
                (?, ?, ?);
        """,
        questions,
    )

    connection.commit()


def populate_database():
    """Add data into the database"""
    print("Connecting to the database")
    connection = sqlite3.connect("db.sqlite3")
    connection.row_factory = sqlite3.Row

    clear_tables(connection)
    add_questions(connection)
    add_choices(connection)

    print("New data added successfully")
    connection.close()
    print("Connection closed")


if __name__ == "__main__":
    populate_database()
