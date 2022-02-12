import unittest

from base.drill import parse_question, score_question

TEST_QUESTIONS = [
    [line.strip() for line in question.strip().splitlines()]
    for question in [
        """
        [1] Name the British philosopher who coined the term 'survival of the fittest.'
        Herbert Spencer / Spencer
        - tags: philosophy
        """,
        """
        [2] Name the two most common forms of municipal government in the United States.
        mayor-council
        council-manager
        - tags: politics
        """,
        """
        [46] How do you pronounce the former Mayor of New York City Ed Koch's last name?
        kotch
        - choices: coke / coach
        """,
        """
        [abc] List the first three US presidents.
        George Washington / Washington
        John Adams / Adams
        Thomas Jefferson / Jefferson
        - ordered: true
        """,
    ]
]


class DrillTests(unittest.TestCase):
    def test_parse_short_answer_question(self):
        self.assertEqual(
            parse_question("test", TEST_QUESTIONS[0], 1),
            {
                "id": "test-1",
                "text": "Name the British philosopher who coined the term 'survival of the fittest.'",
                "type": "short-answer",
                "answer": ["Herbert Spencer", "Spencer"],
                "tags": ["philosophy"],
            },
        )

    def test_parse_list_question(self):
        self.assertEqual(
            parse_question("test", TEST_QUESTIONS[1], 1),
            {
                "id": "test-2",
                "text": "Name the two most common forms of municipal government in the United States.",
                "type": "unordered-list",
                "answer": [["mayor-council"], ["council-manager"]],
                "tags": ["politics"],
            },
        )

    def test_parse_multiple_choice_question(self):
        self.assertEqual(
            parse_question("test", TEST_QUESTIONS[2], 1),
            {
                "id": "test-46",
                "text": "How do you pronounce the former Mayor of New York City Ed Koch's last name?",
                "type": "multiple-choice",
                "answer": ["kotch"],
                "choices": ["coke", "coach"],
            },
        )

    def test_parse_ordered_list_question(self):
        self.assertEqual(
            parse_question("test", TEST_QUESTIONS[3], 1),
            {
                "id": "test-abc",
                "text": "List the first three US presidents.",
                "type": "ordered-list",
                "answer": [
                    ["George Washington", "Washington"],
                    ["John Adams", "Adams"],
                    ["Thomas Jefferson", "Jefferson"],
                ],
            },
        )

    def test_score_unordered_list_question(self):
        self.assertEqual(
            score_question(
                {
                    "type": "unordered-list",
                    "answer": [["Fred Astaire"], ["Ginger Rogers"]],
                },
                ["Ginger Rogers", "Fred Astaire"],
            ),
            100,
        )

        self.assertEqual(
            score_question(
                {
                    "type": "unordered-list",
                    "answer": [
                        ["Fred Astaire", "Astaire"],
                        ["Ginger Rogers", "Rogers"],
                    ],
                },
                ["ginger rogers", "Astaire"],
            ),
            100,
        )

    def test_score_ordered_list_question(self):
        self.assertEqual(
            score_question(
                {
                    "type": "ordered-list",
                    "answer": [
                        ["Fred Astaire", "Astaire"],
                        ["Ginger Rogers", "Rogers"],
                    ],
                },
                ["Ginger Rogers", "Astaire"],
            ),
            0,
        )

        self.assertEqual(
            score_question(
                {
                    "type": "ordered-list",
                    "answer": [
                        ["Fred Astaire", "Astaire"],
                        ["Ginger Rogers", "Rogers"],
                    ],
                },
                ["Fred Astaire", "Grace Kelly"],
            ),
            50,
        )

    def test_score_short_answer_question(self):
        question = {
            "type": "short-answer",
            "answer": ["United Kingdom", "UK"],
        }

        self.assertEqual(
            score_question(
                question,
                ["United Kingdom"],
            ),
            100,
        )

        self.assertEqual(
            score_question(
                question,
                ["uk"],
            ),
            100,
        )

        self.assertEqual(
            score_question(
                question,
                ["France"],
            ),
            0,
        )
