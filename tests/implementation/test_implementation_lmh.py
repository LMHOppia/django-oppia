from django.conf import settings
from django.test import TestCase


class ImplementationCoreTest(TestCase):

    def setUp(self):
        super(ImplementationCoreTest, self).setUp()

    def test_settings(self):
        self.assertEqual(settings.OPPIA_ALLOW_SELF_REGISTRATION, True)
        self.assertEqual(settings.OPPIA_SHOW_GRAVATARS, True)

    def test_theme(self):
        with open("./static/css/oppia.scss", 'r') as oppia_scss:
            css_file = oppia_scss.read().replace("\n", "")

        self.assertNotEqual(css_file.find('$oppia-lighter: #B2B2B2;'), -1)
        self.assertNotEqual(css_file.find('$oppia-light: #C5C9F7;'), - 1)
        self.assertNotEqual(css_file.find('$oppia-mid: #6F79EA;'), -1)
        self.assertNotEqual(css_file.find('$oppia-dark: #6F79EA;'), -1)
