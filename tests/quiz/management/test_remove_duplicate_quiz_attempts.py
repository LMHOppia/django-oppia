from io import StringIO
from django.core.management import call_command
from django.test import TestCase

from quiz.models import QuizAttempt


class RemoveDuplicateQuizAttemptsTest(TestCase):
    fixtures = ['tests/test_user.json',
                'tests/test_oppia.json',
                'tests/test_quiz.json',
                'tests/test_permissions.json']

    def test_remove_duplicate_quiz_attempts(self):
        out = StringIO()
        quiz_attempt_count_start = QuizAttempt.objects.all().count()

        call_command('remove_duplicate_quiz_attempts', stdout=out)

        quiz_attempt_count_end = QuizAttempt.objects.all().count()
        self.assertEqual(quiz_attempt_count_start, quiz_attempt_count_end)
        