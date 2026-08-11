import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class SignUpTests(APITestCase):
    def setUp(self):
        self.url = reverse('sign_up')
        self.payload = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': 'janedoe',
            'email': 'jane.doe@example.com',
            'dob': '1995-05-20',
            'phone_number': '+15551234567',
            'password': 'Str0ng!Pass',
        }

    def test_sign_up_creates_user_with_default_role_and_active_status(self):
        response = self.client.post(self.url, self.payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get(email=self.payload['email'])
        self.assertEqual(user.role, 'member')
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password(self.payload['password']))
        self.assertNotIn('password', response.data['user'])

    def test_sign_up_ignores_client_supplied_role_and_active_status(self):
        payload = {**self.payload, 'role': 'admin', 'is_active': False}
        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.payload['email'])
        self.assertEqual(user.role, 'member')
        self.assertTrue(user.is_active)

    def test_sign_up_fails_with_duplicate_email(self):
        User.objects.create_user(
            email=self.payload['email'],
            password='Str0ng!Pass',
            first_name='Existing',
            last_name='User',
            username='existinguser',
            dob='1990-01-01',
            phone_number='+15559998888',
        )

        response = self.client.post(self.url, self.payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])

    def test_sign_up_fails_with_duplicate_username(self):
        User.objects.create_user(
            email='someone.else@example.com',
            password='Str0ng!Pass',
            first_name='Existing',
            last_name='User',
            username=self.payload['username'],
            dob='1990-01-01',
            phone_number='+15559998888',
        )

        response = self.client.post(self.url, self.payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data['errors'])

    def test_sign_up_fails_when_missing_required_field(self):
        payload = {**self.payload}
        del payload['email']

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])

    def test_sign_up_fails_when_password_too_short(self):
        payload = {**self.payload, 'password': 'Sh0rt!'}

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['errors'])

    def test_sign_up_fails_when_password_missing_letter(self):
        payload = {**self.payload, 'password': '12345678!'}

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['errors'])

    def test_sign_up_fails_when_password_missing_number(self):
        payload = {**self.payload, 'password': 'Password!'}

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['errors'])

    def test_sign_up_fails_when_password_missing_symbol(self):
        payload = {**self.payload, 'password': 'Password1'}

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['errors'])


class LoginTests(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.password = 'Str0ng!Pass'
        self.user = User.objects.create_user(
            email='jane.doe@example.com',
            password=self.password,
            first_name='Jane',
            last_name='Doe',
            username='janedoe',
            dob='1995-05-20',
            phone_number='+15551234567',
        )

    def test_login_succeeds_with_valid_credentials(self):
        response = self.client.post(self.url, {
            'email': self.user.email,
            'password': self.password,
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tokens = response.data['tokens']
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertEqual(tokens['role'], self.user.role)

    def test_login_fails_with_wrong_password(self):
        response = self.client.post(self.url, {
            'email': self.user.email,
            'password': 'WrongPassword1!',
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('tokens', response.data)

    def test_login_fails_for_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.url, {
            'email': self.user.email,
            'password': self.password,
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('tokens', response.data)

    def test_login_fails_with_nonexistent_email(self):
        response = self.client.post(self.url, {
            'email': 'nobody@example.com',
            'password': 'WhoKnows1!',
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_error_does_not_reveal_whether_email_or_password_was_wrong(self):
        wrong_password_response = self.client.post(self.url, {
            'email': self.user.email,
            'password': 'WrongPassword1!',
        })
        nonexistent_email_response = self.client.post(self.url, {
            'email': 'nobody@example.com',
            'password': 'WhoKnows1!',
        })

        self.assertEqual(wrong_password_response.data, nonexistent_email_response.data)

    def test_login_fails_when_missing_password(self):
        response = self.client.post(self.url, {'email': self.user.email})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['errors'])

    def test_login_fails_when_missing_email(self):
        response = self.client.post(self.url, {'password': self.password})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])


class RefreshTests(APITestCase):
    def setUp(self):
        self.url = reverse('token_refresh')
        self.user = User.objects.create_user(
            email='jane.doe@example.com',
            password='Str0ng!Pass',
            first_name='Jane',
            last_name='Doe',
            username='janedoe',
            dob='1995-05-20',
            phone_number='+15551234567',
        )
        self.refresh_token = str(RefreshToken.for_user(self.user))

    def test_refresh_succeeds_with_valid_token(self):
        response = self.client.post(self.url, {'refresh': self.refresh_token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertNotEqual(response.data['refresh'], self.refresh_token)

    def test_refresh_fails_when_reusing_a_rotated_token(self):
        self.client.post(self.url, {'refresh': self.refresh_token})

        response = self.client.post(self.url, {'refresh': self.refresh_token})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Token refresh failed')
        self.assertIn('refresh', response.data['errors'])

    def test_refresh_fails_with_invalid_token(self):
        response = self.client.post(self.url, {'refresh': 'not-a-real-token'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('refresh', response.data['errors'])

    def test_refresh_fails_when_missing_token(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('refresh', response.data['errors'])


class UpdateUserStatusTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='Str0ng!Pass',
            first_name='Admin',
            last_name='User',
            username='adminuser',
            dob='1990-01-01',
            phone_number='+15550000001',
            role='admin',
        )
        self.member = User.objects.create_user(
            email='jane.doe@example.com',
            password='Str0ng!Pass',
            first_name='Jane',
            last_name='Doe',
            username='janedoe',
            dob='1995-05-20',
            phone_number='+15551234567',
        )
        self.url = reverse('update_user_status', args=[self.member.id])

    def test_update_user_status_deactivates_user_as_admin(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(self.url, {'is_active': False})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User deactivated successfully')
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_active)

    def test_update_user_status_reactivates_user_as_admin(self):
        self.member.is_active = False
        self.member.save()
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(self.url, {'is_active': True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User activated successfully')
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_active)

    def test_update_user_status_fails_for_non_admin(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.patch(self.url, {'is_active': False})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {
            'status': False,
            'message': 'You do not have permission to perform this action.',
        })
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_active)

    def test_update_user_status_fails_when_targeting_self(self):
        self.client.force_authenticate(user=self.admin)
        own_url = reverse('update_user_status', args=[self.admin.id])

        response = self.client.patch(own_url, {'is_active': False})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'You cannot update your own status')
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_update_user_status_fails_when_unauthenticated(self):
        response = self.client.patch(self.url, {'is_active': False})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_status_fails_for_nonexistent_user(self):
        self.client.force_authenticate(user=self.admin)
        missing_url = reverse('update_user_status', args=[uuid.uuid4()])

        response = self.client.patch(missing_url, {'is_active': False})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user_status_fails_with_invalid_payload(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(self.url, {'is_active': 'not-a-boolean'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('is_active', response.data['errors'])
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_active)

    def test_update_user_status_fails_when_is_active_missing(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('is_active', response.data['errors'])