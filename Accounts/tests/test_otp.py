from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from unittest.mock import patch

User = get_user_model()

class OTPAPITests(APITestCase):
    def setUp(self):
        self.phonenumber = "09123456789"
        self.otp = "123456"

        self.request_url = reverse("user:request-otp")
        self.verify_url = reverse("user:verify-otp")

    @patch("user.services.external_services.send_sms")
    @patch("user.services.internal_services.save_otp")
    @patch("user.services.internal_services.generate_otp")
    def test_request_otp_success(self, mock_generate, mock_save, mock_send_sms):
        mock_generate.return_value = self.otp

        res = self.client.post(self.request_url, {"phonenumber": self.phonenumber}, format="json")

        self.assertEqual(res.status_code, 200)

        mock_generate.assert_called_once()
        mock_save.assert_called_once_with(self.phonenumber, self.otp)
        mock_send_sms.assert_called_once_with(self.phonenumber, self.otp)

        self.assertEqual(res.data, {"message": "OTP sent"})

    def test_request_otp_missing_phone(self):
        res = self.client.post(self.request_url, {}, format="json")
        self.assertEqual(res.status_code, 400)

    @patch("user.services.internal_services.verify_otp")
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

    # @patch("user.services.internal_services.verify_otp")
    # def test_verify_otp_invalid_returns_400(self, mock_verify):
    #     mock_verify.return_value = False

    #     res = self.client.post(self.verify_url, {
    #         "phonenumber": self.phonenumber,
    #         "otp": "000000"
    #     }, format="json")

    #     self.assertEqual(res.status_code, 400)
    #     self.assertEqual(res.data["error"], "Invalid OTP")
