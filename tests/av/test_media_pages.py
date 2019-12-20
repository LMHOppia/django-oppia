from django.urls import reverse
from oppia.test import OppiaTestCase


class AVPagesViewTest(OppiaTestCase):

    def setUp(self):
        super(AVPagesViewTest, self).setUp()

    def test_home_view(self):
        url = reverse('oppia_av_home')
        allowed_users = [self.admin_user,
                         self.staff_user,
                         self.staff_user,
                         self.normal_user]

        for allowed_user in allowed_users:
            self.client.force_login(allowed_user)
            response = self.client.get(url)
            self.assertTemplateUsed(response, 'av/home.html')
            self.assertEqual(response.status_code, 200)
