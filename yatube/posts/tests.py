from django.test import TestCase, Client

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse

from .models import Post, Group

User = get_user_model()


class Test(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(
            username="tester", password="test1234"
        )
        self.post = Post.objects.create(text="Haha", author=self.user)

    def test_404(self):
        response = self.c.get("/fsqweqeqwewqeqw/")
        self.assertEqual(response.status_code, 404)

    def test_page(self):
        response = self.c.get("/tester/")
        self.assertEqual(response.status_code, 200)

    def test_not_login_can_not_create_post(self):
        response = self.c.get("/new/", follow=True)
        self.assertEqual(response.redirect_chain[0][0], '/auth/login/?next=/new/')

    def test_user_can_create_post(self):
        self.c.force_login(self.user)
        self.c.post("/new/", {
            "text": "jajaj"
        })

        response = self.c.get("/tester/")
        self.assertEqual(response.context["cnt_posts"], 2)

    def test_check_post_create_index_profile_post(self):
        self.post = Post.objects.create(text="This is post no 3", author=self.user)
        response = self.c.get("")
        self.assertContains(response, 'This is post no 3')
        response = self.c.get(f'/{self.user.username}/')
        self.assertContains(response, 'This is post no 3')
        response = self.c.get(f'/{self.user.username}/{self.post.pk}/')
        self.assertContains(response, 'This is post no 3')

    def test_update_post(self):
        self.post.text = "New_update_text"
        self.post.save()
        response = self.c.get("")
        self.assertContains(response, 'New_update_text')
        self.assertNotContains(response, 'This is post no 3')
        response = self.c.get(f'/{self.user.username}/')
        self.assertContains(response, 'New_update_text')
        self.assertNotContains(response, 'This is post no 3')
        response = self.c.get(f'/{self.user.username}/{self.post.pk}/')
        self.assertContains(response, 'New_update_text')
        self.assertNotContains(response, 'This is post no 3')


