from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token
from src.apps.core import utils
from src.apps.masters.models import Master, Feedback
from src.utils.object_creation import make_client, make_order, \
    make_everything
from src.apps.masters.views import AddFeedbackView


class AddFeedbackTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.master_object = Master.objects.get(first_name='VASYA')
        self.client_object = make_client()
        self.order,_ = make_order(self.client_object,
                                self.master_object.services.all()[0],
                                self.master_object, '11:30')
        self.user = self.client_object.user
        token, _ = Token.objects.get_or_create(client=self.client_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_add_first_feedback(self):
        resp = self.client.post(
            reverse(AddFeedbackView.view_name, args=[self.master_object.id]),
            data={
                'rating': 4.0,
                'text': 'superb',
                'date': utils.get_date(0),
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.master_object = Master.objects.get(first_name='VASYA')
        feedback_items = list(self.master_object.feedback.all())
        self.assertEqual(len(feedback_items), 1)
        self.assertEqual(self.master_object.rating, 4.0)

        self.assertEqual(feedback_items[0].text, 'superb')
        self.assertEqual(feedback_items[0].rating, 4.0)
        self.assertEqual(feedback_items[0].client, self.client_object)
        self.assertEqual(feedback_items[0].master, self.master_object)
        self.assertEqual(feedback_items[0].date.strftime('%Y-%m-%d'),
                         utils.get_date(0))

    def test_add_feedback_fail_no_orders(self):
        self.order.delete()
        resp = self.client.post(
            reverse(AddFeedbackView.view_name, args=[self.master_object.id]),
            data={
                'rating': 4.0,
                'text': 'superb',
                'date': utils.get_date(0),
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_second_feedback(self):
        feedback = Feedback.objects.create(client=self.client_object,
                                           master=self.master_object,
                                           rating=5, text='kek',
                                           date=utils.get_date(0))
        self.master_object.add_rating(feedback.rating)
        self.master_object.save()

        resp = self.client.post(
            reverse(AddFeedbackView.view_name, args=[self.master_object.id]),
            data={
                'rating': 4.0,
                'text': 'superb',
                'date': utils.get_date(0),
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.master_object = Master.objects.get(first_name='VASYA')
        feedback_items = list(self.master_object.feedback.all())
        self.assertEqual(len(feedback_items), 2)
        self.assertEqual(self.master_object.rating, 4.5)
