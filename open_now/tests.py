from django.test import TestCase

from .models import Login
from .models import Business

# Create your tests here.

class DummyTestCase(TestCase):
    def setUp(self):
        x = 1
    
    def test_dummy_test_case(self):
        self.assertEqual(1, 1)

class LoginModelTest(TestCase):
    def setUp(self):
        self.login = Login.objects.create(text = 'This is a test')
        self.login.save()
    
    def tearDown(self):
        self.login.delete()

    def test_good_text(self):
        t = 'This is a test'
        self.assertEqual(t, self.login.text)

    def test_bad_text(self):
        t = 'bad text'
        self.assertNotEqual(t, Login.text)

class BusinessModelTest(TestCase):
    def setUp(self):
        self.business = Business.objects.create(business_name = 'test business', description = 'we sell tests', website = 'www.test.com', phone_number = '1234567890', business_category = 'REST')
        self.business.save()

    def tearDown(self):
        self.business.delete()    

    def test_business(self):
        name = 'test business'
        description = 'we sell tests'
        website = 'www.test.com'
        phone = '1234567890'
        category = 'REST'
        self.assertEqual(name, self.business.business_name)
        self.assertEqual(description, self.business.description)
        self.assertEqual(website, self.business.website)
        self.assertEqual(phone, self.business.phone_number)
        self.assertEqual(category, self.business.business_category)
        name = 'test'
        description = 'we buy tests'
        website = 'www.testing.com'
        phone = '0987654321'
        category = 'SHOP'
        self.assertNotEqual(name, self.business.business_name)
        self.assertNotEqual(description, self.business.description)
        self.assertNotEqual(website, self.business.website)
        self.assertNotEqual(phone, self.business.phone_number)
        self.assertNotEqual(category, self.business.business_category)