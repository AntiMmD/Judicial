from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from unittest.mock import patch

from Accounts.exceptions import RateLimitExceeded, InvalidOTPError

User = get_user_model()

class OTPAPITests(APITestCase):
    def setUp(self):
        self.phonenumber = "09123456789"
        self.otp = "123456"

        self.request_url = reverse("Accounts:request-otp")
        self.verify_url = reverse("Accounts:verify-otp")

    @patch("Accounts.services.external_services.send_sms")
    @patch("Accounts.services.internal_services.generate_and_save_otp")
    def test_request_otp_success(self, mock_generate_and_save_otp, mock_send_sms):
        mock_generate_and_save_otp.return_value = self.otp

        res = self.client.post(self.request_url, {"phonenumber": self.phonenumber}, format="json")

        self.assertEqual(res.status_code, 200)

        mock_generate_and_save_otp.assert_called_once_with(self.phonenumber)
        mock_send_sms.assert_called_once_with(self.phonenumber, self.otp)

        self.assertEqual(res.data, {"message": "OTP sent"})

    def test_request_otp_missing_phone(self):
        res = self.client.post(self.request_url, {}, format="json")
        self.assertEqual(res.status_code, 400)

    @patch("Accounts.services.internal_services.verify_otp")
    def test_verify_otp_success_returns_tokens(self, mock_verify):
        mock_verify.return_value = True

        # Ensure user does not exist first
        User.objects.filter(phonenumber=self.phonenumber).delete()

        res = self.client.post(self.verify_url, {
            "phonenumber": self.phonenumber,
            "otp": self.otp
        }, format="json")

        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

        # user should exist now
        self.assertTrue(User.objects.filter(phonenumber=self.phonenumber).exists())

    @patch("Accounts.services.internal_services.generate_and_save_otp")
    def test_request_otp_rate_limited(self, mock_gen_otp):
        """Test that reaching the request limit triggers 429"""
        mock_gen_otp.side_effect = RateLimitExceeded()

        res = self.client.post(self.request_url, {"phonenumber": self.phonenumber}, format="json")

        self.assertEqual(res.status_code, 429)
        self.assertEqual(res.data['detail'], RateLimitExceeded.default_detail)

    @patch("Accounts.services.internal_services.verify_otp")
    def test_verify_otp_invalid_error(self, mock_verify):
        """Test that incorrect OTP triggers 401 via InvalidOTPError"""
        mock_verify.side_effect = InvalidOTPError()

        res = self.client.post(self.verify_url, {
            "phonenumber": self.phonenumber,
            "otp": "wrong-otp"
        }, format="json")

        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data['detail'], InvalidOTPError.default_detail)

    @patch("Accounts.services.internal_services.verify_otp")
    def test_verify_otp_too_many_retries(self, mock_verify):
        """Test that brute-force protection (too many verify attempts) triggers 429"""

        mock_verify.side_effect = RateLimitExceeded()

        res = self.client.post(self.verify_url, {
            "phonenumber": self.phonenumber,
            "otp": self.otp
        }, format="json")

        self.assertEqual(res.status_code, 429)


from Accounts.services.internal_services import redis_client
class OTPIntegrationTests(APITestCase):
    def setUp(self):
        redis_client.flushdb()
        self.phonenumber = "09123456789"
        self.otp_url = reverse("Accounts:request-otp")
        self.verify_url = reverse("Accounts:verify-otp")

    def test_integration_generate_and_save_otp_creation(self):
        from Accounts.services.internal_services import generate_and_save_otp

        otp = generate_and_save_otp(self.phonenumber)
        
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())

    @patch("Accounts.services.external_services.send_sms") 
    def test_request_otp_rate_limit_integration(self, mock_send):
        """
        Integration: Test that multiple requests for OTP within 120s 
        triggers RateLimitExceeded.
        """
        res1 = self.client.post(self.otp_url, {"phonenumber": self.phonenumber})
        self.assertEqual(res1.status_code, 200)

        # Second request: (default limit is 1) should be blocked immediately
        res2 = self.client.post(self.otp_url, {"phonenumber": self.phonenumber})
        self.assertEqual(res2.status_code, 429)
        self.assertEqual(res2.data['detail'], 'درخواست‌های شما بیش از حد مجاز است. لطفاً بعداً دوباره تلاش کنید.')

    def test_verify_otp_brute_force_protection_integration(self):
        """
        Integration: Test that failing OTP verification multiple times 
        blocks the user even if they eventually provide the right OTP.
        """
        from Accounts.services.internal_services import _save_otp
        correct_otp = "123456"
        _save_otp(self.phonenumber, correct_otp)

        # Fail 3 times (assuming allowed_retry_attempts=3)
        for _ in range(3):
            res = self.client.post(self.verify_url, {
                "phonenumber": self.phonenumber, 
                "otp": "000000"
            })
            self.assertEqual(res.status_code, 401)

        # The 4th fail triggers the Rate Limit
        res_limit = self.client.post(self.verify_url, {
            "phonenumber": self.phonenumber, 
            "otp": "000000"
        })
        self.assertEqual(res_limit.status_code, 429)

        # Even if they now provide the CORRECT OTP, they are still blocked
        res_correct_but_blocked = self.client.post(self.verify_url, {
            "phonenumber": self.phonenumber, 
            "otp": correct_otp
        })
        self.assertEqual(res_correct_but_blocked.status_code, 429)
