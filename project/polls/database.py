import sqlite3


def save_poll(data):
    connection = sqlite3.connect("db.sqlite3")
    connection.row_factory = sqlite3.Row

    question_id = save_question(connection, data["question"])

    # Create a list of tuples. Each tuple represents a choice:
    # (choice_text, votes, question_id)
    choices = [
        (data[c], 0, question_id)
        for c in ["choice1", "choice2", "choice3", "choice4"]
        # Skip empty choices
        if data[c]
    ]

    save_choices(connection, choices)

    connection.commit()
    connection.close()

    return True


def save_question(connection, question):
    cursor = connection.cursor()

    cursor.execute(
        f"""
            INSERT INTO polls_question
                (question_text, pub_date)
            VALUES
                ("{question}", CURRENT_TIMESTAMP);
        """
    )

    # Flaw 3. SQL injection fix. Remove the lines above.
    # cursor.execute(
    #     """
    #         INSERT INTO polls_question
    #             (question_text, pub_date)
    #         VALUES
    #             (?, CURRENT_TIMESTAMP);
    #     """,
    #     [question],
    # )

    return cursor.lastrowid


def save_choices(connection, choices):
    cursor = connection.cursor()

    cursor.executemany(
        """
            INSERT INTO polls_choice
                (choice_text, votes, question_id)
            VALUES
                (?, ?, ?);
        """,
        choices,
    )
