from rest_framework.test import APITestCase
from Laws.models import Law
from django.urls import reverse
from rest_framework import status

class GetLawTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.law = Law.objects.create(
            id= "smth",
            title="Main Law",
            type="Law",
            slug="main-law"
        )

        # Create 2 Articles (Child)
        cls.article1 = Law.objects.create(
            id= "vavkanscan",
            title="Article 1",
            type="Article",
            code="1",
            article_no=1,
            parent=cls.law
        )
        cls.article2 = Law.objects.create(
            id= "poqwmdc",
            title="Article 2",
            type="Article",
            code="2",
            article_no=2,
            parent=cls.law
        )

        # Create 2 notes for that Article (Child)
        # article 1 has 2 notes and article 2 has 0 notes
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

        cls.url = reverse('id-law-detail',args=[cls.law.pk])

    def test_get_law_detail_success(self):
        """Test that we can fetch a law and its children."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check data structure
        self.assertEqual(response.data['title'], "Main Law")
        
        # Check that children exist
        self.assertEqual(len(response.data['children']), 4)

    
    def test_get_law_detail_ordering_is_correct(self):
        response = self.client.get(self.url)

        groups = response.data['children']['results']
        items = [item for g in groups for item in g['items']]

        self.assertEqual(items[0]['type'], "Article")
        self.assertEqual(items[0]['article_no'], 1)

        self.assertEqual(items[1]['type'], "Note")
        self.assertEqual(items[1]['article_no'], 1)
        self.assertEqual(items[1]['note_no'], 1)

        self.assertEqual(items[2]['type'], "Note")
        self.assertEqual(items[2]['note_no'], 2)

        self.assertEqual(items[3]['type'], "Article")
        self.assertEqual(items[3]['article_no'], 2)


    def test_children_has_correct_detail(self):
        response = self.client.get(self.url)

        groups = response.data['children']['results']
        items = [item for g in groups for item in g['items']]

        self.assertIn('title', items[0])
        self.assertIn('main_content', items[0])
        self.assertIn('summary', items[0])

    def test_get_law_with_slug_seo(self):
        """Test that the URL works with the SEO slug included."""
        url_with_slug = reverse('slug-law-detail', args=[self.law.slug, self.law.pk ])
        response = self.client.get(url_with_slug)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.law.pk)

    def test_get_law_not_found(self):
        """Test that a non-existent ID returns 404."""
        invalid_url = reverse('id-law-detail', args=['does-not-exist'])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
