
from django.urls import reverse
from oppia.test import OppiaTestCase


class AppLaunchActivityTest(OppiaTestCase):
    fixtures = ['tests/test_user.json',
                'tests/test_oppia.json',
                'tests/test_quiz.json',
                'tests/test_permissions.json']

    valid_digest = '11cc12291f730160c324b727dd2268b612137'
    invalid_digest = '1ab2c3d4e5f6'

    # all users should be able to access without logging in
    def test_access_valid_digest(self):
        url = ('%s?digest=' + self.valid_digest) \
            % reverse('oppia:app_launch_activity_redirect')
        response = self.client.get(url)
        self.assertTemplateUsed('course/activity_digest.html')
        self.assertEqual(200, response.status_code)

    def test_access_no_digest(self):
        url = reverse('oppia:app_launch_activity_redirect')
        response = self.client.get(url)
        self.assertRaises(ValueError)
        self.assertEqual(404, response.status_code)

    def test_access_invalid_digest(self):
        url = ('%s?digest=' + self.invalid_digest) \
            % reverse('oppia:app_launch_activity_redirect')
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
