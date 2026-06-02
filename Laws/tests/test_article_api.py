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

        cls.url = reverse('id-article-detail',args=[cls.article.pk])
    
    def test_get_article_detail_returns_400_if_id_is_not_article(self):
        url = reverse('id-article-detail',args=[self.law.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_article_detail_success(self):
        """Test that we can fetch an article and its related info."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check data structure
        self.assertCountEqual(response.data['id'], self.article.id)
        self.assertEqual(response.data['title'], "Main Article")
        
        # Check that notes exist
        self.assertTrue(len(response.data['notes']) == 2)
    
    def test_get_article_detail_ordering_is_correct(self):
        response = self.client.get(self.url)

        self.assertEqual(response.data['notes'][0]['type'], "Note")
        self.assertEqual(response.data['notes'][0]['article_no'], 1)
        self.assertEqual(response.data['notes'][0]['note_no'], 1)

        self.assertEqual(response.data['notes'][1]['type'], "Note")
        self.assertEqual(response.data['notes'][1]['article_no'], 1)
        self.assertEqual(response.data['notes'][1]['note_no'], 2)
    

    def test_notes_have_correct_detail(self):
        response = self.client.get(self.url)

        self.assertIn('title', response.data['notes'][0])
        self.assertIn('main_content', response.data['notes'][0])
        self.assertIn('summary', response.data['notes'][0])

    def test_get_article_with_slug_seo(self):
        """Test that the URL works with the SEO slug included."""
        url_with_slug = reverse('slug-article-detail', args=[self.article.slug, self.article.pk ])
        response = self.client.get(url_with_slug)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.article.pk)

    def test_get_article_not_found(self):
        """Test that a non-existent ID returns 404."""
        invalid_url = reverse('id-article-detail', args=['does-not-exist'])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
