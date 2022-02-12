import json
import math
import random
import re
import time
from typing import Any, Dict, List

from base.database import Database, Row

Question = Dict[str, Any]
Quiz = List[Question]


def get_quiz(db: Database) -> Quiz:
    """
    Selects a list of 20 questions from the database.

    A thin wrapper around `select_questions` intended for use as a JSON API.
    """
    questions = select_questions(db)

    # Convert question fields to JSON.
    for question in questions:
        question["answer"] = json.loads(question["answer"])
        if question["choices"]:
            question["choices"] = json.loads(question["choices"])

    return questions


def submit_quiz(db: Database, responses: Dict[str, Any]) -> dict:
    """
    Submits a quiz to be scored.
    """
    t = int(time.time())
    results = []
    quizzes_taken = set()
    for response in responses["responses"]:
        question = response["question"]
        quizzes_taken.add(question["quiz"]["id"])

        if response["response"]:
            answer = response["response"]["response"]
        else:
            answer = [""]

        score = score_question(question, answer)

        db.insert_and_get(
            "quiz_results",
            {
                "question": question["id"],
                "score": score,
                "time_asked": t,
            },
        )
        results.append(
            {
                "score": score,
                "answer": question["answer"],
            }
        )

        strength = question["strength"]
        if score >= 80:
            # Strength is capped at 5 unless the user explicitly marks it as memorized,
            # which is handled outside this function.
            if strength < 4:
                strength += 1
        elif score <= 50:
            if strength == 10:
                strength = 2
            else:
                strength -= 1

        db.update_by_pk(
            "quiz_questions",
            question["id"],
            {
                "strength": strength,
                "time_last_asked": t,
            },
        )

    for quiz_pk in quizzes_taken:
        db.update_by_pk("quizzes", quiz_pk, {"time_last_taken": t})

    return {"results": results}


def select_questions(db: Database) -> List[Row]:
    """
    Selects a list of 20 questions from the database using a spaced-repetition
    algorithm.

    The questions are drawn from 3 quizzes in a set ratio: 10 from the first quiz, 7
    from the second, and 3 from the third.

    The quizzes and questions are selected based on the strength of memorization and
    the time since they were last asked.
    """
    quizzes = select_quizzes(db)

    questions = []
    questions.extend(select_questions_from_quizzes(db, quizzes[0], 10))
    questions.extend(select_questions_from_quizzes(db, quizzes[1], 7))
    questions.extend(select_questions_from_quizzes(db, quizzes[2], 3))

    return questions


def select_quizzes(db: Database) -> List[Row]:
    """
    Selects a list of 3 questions from the database using a spaced-repetition algorithm.
    """
    quizzes = db.select("quizzes", where="disabled = 0")
    weights = get_quiz_weights(db, quizzes)
    return make_weighted_choice(quizzes, weights, 3)


def select_questions_from_quizzes(db: Database, quiz: Row, count: int) -> List[Row]:
    pool = db.select(
        "quiz_questions",
        where="quiz = :quiz AND deprecated = 0",
        values={"quiz": quiz["id"]},
        get_related=["quiz"],
    )
    weights = get_question_weights(db, pool)
    selected = make_weighted_choice(pool, weights, count)
    random.shuffle(selected)
    return selected


def get_quiz_weights(db: Database, quizzes: List[Row]) -> List[float]:
    """
    Returns the weights for the list of quizzes so that quizzes[i] corresponds to
    weights[i] in the return value.

    Weights are between 0.0 and 1.0. Higher values mean the quiz is more likely to be
    selected, but are otherwise arbitrary (1.0 does not mean the quiz has a 100% chance
    of being selected).
    """
    minimum_time_last_taken = min(quiz["time_last_taken"] for quiz in quizzes)
    maximum_time_last_taken = max(quiz["time_last_taken"] for quiz in quizzes)

    weights = []
    for quiz in quizzes:
        average_strength = (
            db.sql(
                """
            SELECT
              AVG(strength)
            FROM
              quiz_questions
            WHERE
              quiz = :quiz
            """,
                values={"quiz": quiz["id"]},
                as_tuple=True,
                multiple=False,
            )[0]
            or 0
        )

        if minimum_time_last_taken != maximum_time_last_taken:
            m = 1 / (minimum_time_last_taken - maximum_time_last_taken)
        else:
            m = 0
        b = 1

        assert (
            minimum_time_last_taken
            <= quiz["time_last_taken"]
            <= maximum_time_last_taken
        )

        time_weight = m * (quiz["time_last_taken"] - minimum_time_last_taken) + b
        assert 0.0 <= time_weight <= 1.0

        # Technically average strength for a quiz could be as high as 10 if all
        # questions are memorized, but we consider all values above 5 to be identical
        # to avoid skewing the scale.
        strength_weight = (5 - min(average_strength, 5)) / 5
        assert 0.0 <= strength_weight <= 1.0

        weight = 0.8 * strength_weight + 0.2 * time_weight
        assert 0.0 <= weight <= 1.0

        weights.append(weight)

    return weights


def get_question_weights(db: Database, questions: List[Row]) -> List[float]:
    """
    Returns the weights for the list of questions so that questions[i] corresponds to
    weights[i] in the return value.

    Weights are between 0.0 and 1.0. Higher values mean the question is more likely to
    be selected, but are otherwise arbitrary (1.0 does not mean the quiz has a 100%
    chance of being selected).
    """
    minimum_time_last_asked = min(question["time_last_asked"] for question in questions)
    maximum_time_last_asked = max(question["time_last_asked"] for question in questions)

    weights = []
    for question in questions:
        if minimum_time_last_asked != maximum_time_last_asked:
            m = 1 / (minimum_time_last_asked - maximum_time_last_asked)
        else:
            m = 0
        b = 1

        assert (
            minimum_time_last_asked
            <= question["time_last_asked"]
            <= maximum_time_last_asked
        )

        # Map the time last asked to a scale of 0 to 1, where 1 means the question has
        # the minimum value of time last asked (i.e., it has gone the longest without
        # being asked) and 0 means the question has the maximum value of time last
        # asked.
        time_weight = m * (question["time_last_asked"] - minimum_time_last_asked) + b
        assert 0.0 <= time_weight <= 1.0

        # Map the question's strength to a scale of 0 to 1.
        #
        # Strength   Weight
        #        1     0.83
        #        2     0.66
        #        3     0.50
        #        4     0.33
        #        5     0.16
        #       10     0.05
        #
        # Strengths between 5 and 10 are not possible.
        strength_weight = (
            0.05 if question["strength"] == 10 else (6 - question["strength"]) / 6
        )
        assert 0.0 <= strength_weight <= 1.0

        weight = 0.8 * strength_weight + 0.2 * time_weight
        assert 0.0 <= weight <= 1.0

        weights.append(weight)

    return weights


def make_weighted_choice(choices: list, weights: List[float], count: int) -> list:
    # Based on https://stackoverflow.com/a/3679747/
    selected: list = []

    while len(selected) < count:
        total = sum(weights)
        r = random.uniform(0, total)
        upto = 0.0
        for i, (choice, weight) in enumerate(zip(choices, weights)):
            if upto + weight >= r:
                selected.append(choice)
                choices = choices[:i] + choices[i + 1 :]
                weights = weights[:i] + weights[i + 1 :]
                break

            upto += weight

    assert len(selected) == count
    return selected


def score_question(question: Question, response: List[str]) -> int:
    """
    Returns the score of the response to the question, as an integer between 0 and 100.
    """
    if question["type"] == "unordered-list":
        points = 0
        for answer in question["answer"]:
            lower_case_answers = [a.lower() for a in answer]
            for r in response:
                r = r.lower() if r is not None else ""
                if r in lower_case_answers:
                    points += 1
                    break
        return math.floor((points / len(question["answer"])) * 100)
    elif question["type"] == "ordered-list":
        points = 0
        for (r, answers) in zip(response, question["answer"]):
            lower_case_answers = [a.lower() for a in answers]
            if r.lower() in lower_case_answers:
                points += 1
        return math.floor((points / len(question["answer"])) * 100)
    else:
        r = response[0].lower()
        if any(a.lower() == r for a in question["answer"]):
            return 100
        else:
            return 0


first_line_pattern = re.compile(r"^\[(.+)\] (.+)$")


def parse_question(quiz_name: str, block: List[str], lineno: int) -> Question:
    """
    Returns a question parsed from the list of lines.

    This is no longer used to parse questions from disk as they are now stored in the
    database, but it is used by the `kgx qnew` and `kgx qedit` commands.
    """
    if len(block) < 2:
        raise DrillParseError(f"too few lines, line {lineno}")

    m = first_line_pattern.match(block[0])
    if not m:
        raise DrillParseError(f"malformed first line, line {lineno}")

    question_id = m.group(1)
    question_text = m.group(2)

    question: Dict[str, Any] = {
        "id": quiz_name + "-" + question_id,
        "text": question_text,
    }

    answers = []
    for line in block[1:]:
        if line.startswith("-"):
            key, value = line[1:].split(":")
            key = key.strip()
            value = value.strip()

            if key == "tags":
                question["tags"] = [tag.strip() for tag in value.split(",")]
            elif key == "choices":
                question["choices"] = parse_answer(value)
                question["type"] = "multiple-choice"
            elif key == "ordered":
                if value == "true":
                    question["type"] = "ordered-list"
                elif value == "false":
                    # `false` is the default so nothing to do here.
                    pass
                else:
                    raise DrillParseError(
                        "value for 'ordered' attribute must be either 'true' or 'false'"
                        + f" (question {question_id})"
                    )
            else:
                raise DrillParseError(
                    f"unknown question attribute: {key} (question {question_id})"
                )
        else:
            answers.append(line)

    if len(answers) > 1:
        question["answer"] = [parse_answer(a) for a in answers]
    else:
        question["answer"] = parse_answer(answers[0])

    if "type" not in question:
        if len(answers) > 1:
            question["type"] = "unordered-list"
        else:
            question["type"] = "short-answer"

    return question


def parse_answer(answer: str) -> List[str]:
    return [a.strip() for a in answer.split("/")]


class DrillParseError(Exception):
    pass
