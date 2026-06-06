from django.test import TestCase
from django.urls import reverse

from Laws.models import Law


class LawSearchViewTests(TestCase):

    def setUp(self):
        self.law = Law.objects.create(
            type=Law.LegalType.law,
            title="قانون مدنی",
            short_summary="خلاصه قانون مدنی",
            priority=10,
            category=Law.Category.law,
        )
        self.article = Law.objects.create(
            type=Law.LegalType.article,
            parent=self.law,
            title="ماده ۱۰ قانون مدنی",
            main_content="متن ماده دهم",
            code="10",
            article_no=10,
            priority=5,
        )
        self.note = Law.objects.create(
            type=Law.LegalType.note,
            parent=self.law,
            title="تبصره ۱ ماده ۱۰",
            summary="متن تبصره",
            code="10.1",
            article_no=10,
            note_no=1,
            priority=3,
        )
        self.other_law = Law.objects.create(
            type=Law.LegalType.law,
            title="قانون تجارت",
            short_summary="خلاصه تجارت",
            priority=8,
            category=Law.Category.regulation,
        )

    def test_search_returns_all_types_without_type_filter(self):
        response = self.client.get(reverse("search:law-search"), {"q": "قانون"})
        self.assertEqual(response.status_code, 200)

        result_types = {item["type"] for item in response.data["results"]}
        self.assertIn(Law.LegalType.law, result_types)
        self.assertIn(Law.LegalType.article, result_types)
        self.assertEqual(response.data["type_filter"], None)
        self.assertEqual(response.data["query"], "قانون")

    def test_facets_show_counts_per_type(self):
        response = self.client.get(reverse("search:law-search"), {"q": "قانون"})
        self.assertEqual(response.status_code, 200)

        facets = response.data["facets"]
        self.assertGreaterEqual(facets["Law"], 2)
        self.assertGreaterEqual(facets["Article"], 1)
        self.assertIn("Note", facets)

    def test_type_filter_limits_results(self):
        response = self.client.get(
            reverse("search:law-search"),
            {"q": "قانون", "type": Law.LegalType.law},
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["type_filter"], Law.LegalType.law)
        self.assertTrue(
            all(item["type"] == Law.LegalType.law for item in response.data["results"])
        )

    def test_type_filter_article_only(self):
        response = self.client.get(
            reverse("search:law-search"),
            {"q": "ماده", "type": Law.LegalType.article},
        )
        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            all(item["type"] == Law.LegalType.article for item in response.data["results"])
        )

    def test_category_filter(self):
        response = self.client.get(
            reverse("search:law-search"),
            {"q": "قانون", "category": Law.Category.regulation},
        )
        self.assertEqual(response.status_code, 200)

        returned_ids = {item["id"] for item in response.data["results"]}
        self.assertIn(self.other_law.id, returned_ids)
        self.assertNotIn(self.law.id, returned_ids)

    def test_invalid_type_returns_400(self):
        response = self.client.get(
            reverse("search:law-search"),
            {"q": "قانون", "type": "Invalid"},
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_category_returns_400(self):
        response = self.client.get(
            reverse("search:law-search"),
            {"q": "قانون", "category": "Invalid"},
        )
        self.assertEqual(response.status_code, 400)

    def test_relevance_prioritizes_title_match(self):
        title_match = Law.objects.create(
            type=Law.LegalType.law,
            title="عبارت منحصربه‌فرد آلفا",
            priority=1,
        )
        Law.objects.create(
            type=Law.LegalType.law,
            title="سایر موضوعات",
            main_content="عبارت منحصربه‌فرد آلفا در متن اصلی",
            priority=100,
        )

        response = self.client.get(
            reverse("search:law-search"),
            {"q": "عبارت منحصربه‌فرد آلفا"},
        )
        self.assertEqual(response.status_code, 200)

        results = response.data["results"]
        self.assertEqual(results[0]["id"], title_match.id)

    def test_parent_title_included_for_child_results(self):
        response = self.client.get(
            reverse("search:law-search"),
            {"q": "تبصره", "type": Law.LegalType.note},
        )
        self.assertEqual(response.status_code, 200)

        note_result = next(
            item for item in response.data["results"] if item["id"] == self.note.id
        )
        self.assertEqual(note_result["parent_title"], self.law.title)

    def test_pagination(self):
        for i in range(25):
            Law.objects.create(
                type=Law.LegalType.law,
                title=f"قانون شماره {i}",
                priority=i,
            )

        response = self.client.get(
            reverse("search:law-search"),
            {"q": "قانون", "page_size": 10},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])
