from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class UserCreationTests(TestCase):
    def test_create_user_with_phonenumber_successful(self):
        phonenumber = '12345678911'
        email = 'test@example.com'
        password = 'testpass123'
        user = User.objects.create_user(
            phonenumber = phonenumber,
            email = email,
            password = password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_with_email_normalized(self):
        sample_emails = [
            ['test1@EXAMPLE.COM', 'test1@example.com'],
            ['test2@EXAMPLE.com', 'test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'test3@example.com']
        ]
        for i, (email, expected) in enumerate(sample_emails):
            user = User.objects.create_user(phonenumber=f'{i}',email = email, password='sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_phonenumber_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(phonenumber='', password='sample123')

    def test_create_super_user(self):
        user = User.objects.create_superuser(
            '09123456789',
            'test1234'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_new_user_with_already_existing_email_fails(self):
        User.objects.create_user(
                phonenumber='09123456789',
                email='duplicated@example.com',
                password='sample123',
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                phonenumber='09987654321',
                email='duplicated@example.com',
                password='sample123',
                )

class UserFieldNormalizationsTests(TestCase):
    def test_phone_is_trimmed(self):
        user = User.objects.create(
            phonenumber=" 09123456789 "
        )
        self.assertEqual(user.phonenumber, "09123456789")

    def test_phone_plus98_is_converted_to_local_format(self):
        user = User.objects.create(
            phonenumber="+989123456789"
        )
        self.assertEqual(user.phonenumber, "09123456789")

    def test_email_is_lowercased_and_trimmed(self):
        user = User.objects.create(
            phonenumber="09111111111",
            email="  TEST@Example.COM  "
        )
        self.assertEqual(user.email, "test@example.com")

    def test_empty_email_becomes_none(self):
        user = User.objects.create(
            phonenumber="09122222222",
            email="   "
        )
        self.assertIsNone(user.email)

    def test_multiple_null_emails_are_allowed(self):
        User.objects.create(
            phonenumber="09133333333",
            email=None
        )

        # Should not raise error
        User.objects.create(
            phonenumber="09144444444",
            email=None
        )

        self.assertEqual(User.objects.count(), 2)

    def test_email_must_be_unique(self):
        User.objects.create(
            phonenumber="09155555555",
            email="unique@test.com"
        )

        with self.assertRaises(IntegrityError):
            User.objects.create(
                phonenumber="09166666666",
                email="unique@test.com"
            )

    def test_str_returns_phonenumber(self):
        user = User.objects.create(
            phonenumber="09177777777"
        )
        self.assertEqual(str(user), "09177777777")