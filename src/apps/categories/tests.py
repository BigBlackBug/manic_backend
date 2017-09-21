from rest_framework.test import APITestCase

from src.apps.core import utils
from .models import ServiceCategory, Service
from .serializers import ServiceCategorySerializer


class CategoriesTestCase(APITestCase):
    def tearDown(self):
        self.category.delete()

    def setUp(self):
        self.category = ServiceCategory(name='category',
                                        image=utils.make_in_memory_image('testfile'))
        self.category.save()
        self.service = Service.objects.create(category=self.category, name='s1',
                                              description='desc', cost=100, duration=100)

    def test_serializer(self):
        serializer = ServiceCategorySerializer(instance=self.category)

        data = serializer.data
        self.assertEqual(data['name'], self.category.name)
        self.assertEqual(data['image'], self.category.image.url)

        self.assertEqual(len(data['services']), 1)
        service = data['services'][0]

        self.assertEqual(service['category'], self.category.id)
        self.assertEqual(service['name'], self.service.name)
        self.assertEqual(service['description'], self.service.description)
        self.assertEqual(service['cost'], self.service.cost)
        self.assertEqual(service['duration'], self.service.duration)
