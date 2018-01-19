from rest_framework.test import APITestCase

from src.apps.core import utils
from ..models import ServiceCategory, Service, DisplayItem
from ..serializers import ServiceCategorySerializer, DisplayItemSerializer


class CategoriesTestCase(APITestCase):
    def setUp(self):
        self.category = ServiceCategory(name='category',
                                        image=utils.make_in_memory_image(
                                            'testfile'))
        self.category.save()
        self.service = Service.objects.create(category=self.category, name='s1',
                                              description='desc', cost=100,
                                              min_duration=100,
                                              max_duration=120)

    def test_serializer(self):
        serializer = ServiceCategorySerializer(instance=self.category)

        data = serializer.data
        self.assertEqual(data['name'], self.category.name)
        self.assertEqual(data['image'], self.category.image.url)

        self.assertEqual(len(data['services']), 1)
        service = data['services'][0]

        self.assertEqual(service['name'], self.service.name)
        self.assertEqual(service['description'], self.service.description)
        self.assertEqual(service['cost'], self.service.cost)
        self.assertEqual(service['min_duration'], self.service.min_duration)
        self.assertEqual(service['max_duration'], self.service.max_duration)

    def test_display_items(self):
        di = DisplayItem.objects.create(name='DI',
                                        image=utils.make_in_memory_image(
                                            'avatar'),
                                        special={
                                            'type': 'supertype'
                                        })
        di.categories.add(self.category)
        serializer = DisplayItemSerializer(di)
        data = serializer.data
        self.assertEqual(data['name'], 'DI')
        self.assertEqual(data['special'], {
            'type': 'supertype'
        })
        self.assertIn('image', data)
        cats = data['categories']
        self.assertEqual(len(cats), 1)
        self.assertEqual(cats[0]['name'], self.category.name)
        self.assertIn('services', cats[0])

    def test_display_items_no_name(self):
        di = DisplayItem.objects.create()
        di.categories.add(self.category)
        serializer = DisplayItemSerializer(di)
        data = serializer.data
        self.assertNotIn('name', data)
        self.assertNotIn('image', data)
        self.assertNotIn('special', data)
        cats = data['categories']
        self.assertEqual(len(cats), 1)
        self.assertEqual(cats[0]['name'], self.category.name)
        self.assertIn('services', cats[0])
