from django.test import TestCase
from job.models import Job


class JobModelTests(TestCase):
    def test_occupation_can_be_null(self):
        """occupation can be omitted (NULL in DB)."""
        job = Job.objects.create(occupation=None, description="No occupation")
        self.assertIsNone(job.occupation)

    def test_occupation_can_be_blank_string_and_becomes_null(self):
        """Blank string occupation should be normalized to None (NULL)."""
        job = Job.objects.create(occupation="", description="Blank occupation")
        job.refresh_from_db()
        self.assertIsNone(job.occupation)

    def test_occupation_is_stripped_and_lowercased(self):
        """occupation should be strip()'d and lower()'d on save."""
        job = Job.objects.create(occupation="  Senior Engineer  ", description="Test")
        job.refresh_from_db()
        self.assertEqual(job.occupation, "senior engineer")

    def test_multiple_null_occupations_allowed(self):
        """Multiple jobs with NULL occupation are allowed despite unique=True."""
        Job.objects.create(occupation=None, description="First")
        Job.objects.create(occupation=None, description="Second")
        self.assertEqual(Job.objects.filter(occupation__isnull=True).count(), 2)

    def test_unique_occupation_enforced_after_normalization(self):
        """
        Unique constraint should apply after strip() + lower().
        ' Engineer ' and 'engineer' must conflict.
        """
        Job.objects.create(occupation=" Engineer ", description="First engineer")

        with self.assertRaises(Exception):
            Job.objects.create(occupation="engineer", description="Duplicate engineer")

    def test_is_active_default_true(self):
        """is_active should default to True."""
        job = Job.objects.create(occupation=None, description="Active by default")
        self.assertTrue(job.is_active)

    def test_update_occupation_reapplies_normalization(self):
        """Changing occupation later should also be normalized on save."""
        job = Job.objects.create(occupation="dev", description="test")
        job.occupation = "  DEV OPS "
        job.save()
        job.refresh_from_db()
        self.assertEqual(job.occupation, "dev ops")