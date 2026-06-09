from rest_framework.test import APITestCase
from Laws.models import Law
from django.urls import reverse
from rest_framework import status

class GetArticleTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.law = Law.objects.create(
            id= "smth",
            title="Main Law",
            type="Law",
            slug="main-law"
        )

        # Create 2 Articles (Child)
        cls.article = Law.objects.create(
            id= "vavkanscan",
            title="Main Article",
            type="Article",
            code="1",
            article_no=1,
            parent=cls.law
        )

        # Create 2 notes for that Article (Child)
        cls.note1 = Law.objects.create(
            id= "vscbtrnrntn",
            title ="Note 1",
            type="Note",
            code="1.1",
            article_no=1,
            note_no=1,
            parent=cls.law
        )
        cls.note2 = Law.objects.create(
            id= "antmyt",
            title ="Note 2",
            type="Note",
            code="1.2",
            article_no=1,
            note_no=2,
            parent=cls.law
        )

        cls.url = reverse('id-law-detail',args=[cls.article.pk])

    def test_get_article_detail_success(self):
        """Test that we can fetch an article and its related info."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check data structure
        self.assertCountEqual(response.data['id'], self.article.id)
        self.assertEqual(response.data['title'], "Main Article")
        
        # Check that notes exist
        self.assertTrue(len(response.data['children']['results'][0]['items']) == 2)
    
    def test_get_article_detail_ordering_is_correct(self):
        response = self.client.get(self.url)

        items = response.data['children']['results'][0]['items']

        self.assertEqual(items[0]['type'], "Note")
        self.assertEqual(items[0]['article_no'], 1)
        self.assertEqual(items[0]['note_no'], 1)

        self.assertEqual(items[1]['type'], "Note")
        self.assertEqual(items[1]['article_no'], 1)
        self.assertEqual(items[1]['note_no'], 2)
        

    def test_notes_have_correct_detail(self):
        response = self.client.get(self.url)

        items = response.data['children']['results'][0]['items']

        self.assertIn('title', items[1])
        self.assertIn('main_content', items[1])
        self.assertIn('summary', items[1])
