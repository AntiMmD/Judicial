# laws/tests/test_slug.py
from django.test import TestCase
from Laws.models import Law


class LawSlugTests(TestCase):
    def test_slug_is_generated_on_save(self):
        law = Law.objects.create(
            id="697e1cf73710bfbbf9aaa7ef",
            title="  قانون مدنی  ",
            type='Law'
        )
        self.assertEqual(law.slug, "قانون-مدنی")

    def test_custom_slug_is_not_automaticaly_generated(self):
        law = Law.objects.create(
            id="697e1cf73710bfbbf9aaa7ef",
            title="قانون مدنی",
            slug="custom-slug",
            type='Law'
        )
        self.assertEqual(law.slug, "custom-slug")

    def test_slug_falls_back_to_id_prefix_when_title_is_empty(self):
        law = Law.objects.create(
            id="697e1cf73710bfbbf9aaa7ef",
            title="",
            type='Law'
        )
        self.assertEqual(law.slug, None)
