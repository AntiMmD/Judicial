from django.test import TestCase
from django.urls import reverse

from Laws.models import Law


class LawsListViewTests(TestCase):

    def setUp(self):
        Law.objects.create(type=Law.Types.law, title="Law A", priority=2)
        Law.objects.create(type=Law.Types.law, title="Law B", priority=5)
        Law.objects.create(type=Law.Types.article, title="Article X", priority=10, code='1')

    def test_only_laws_returned(self):
        response = self.client.get(reverse("laws-list"))
        self.assertEqual(response.status_code, 200)

        results = response.data["results"]
        self.assertEqual(len(results), 2)
        returned_ids  = {item["id"] for item in results}
        returned_types = set(
            Law.objects.filter(id__in= returned_ids ).values_list("type", flat=True)
        )

        self.assertTrue(all(type == Law.Types.law for type in returned_types))

        expected_ids = set(
            Law.objects.filter(type=Law.Types.law).values_list("id", flat=True)
        )
        self.assertEqual(returned_ids, expected_ids)

    def test_ordering_by_priority(self):
        response = self.client.get(reverse("laws-list"))
        results = response.data["results"]
        priorities = [item["priority"] for item in results]

        self.assertEqual(priorities, sorted(priorities, reverse=True))