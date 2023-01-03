from django.contrib.auth.models import User
from .models import Post
from rest_framework import status
from rest_framework.test import APITestCase


class PostListViewTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username='test', password='pass')

    def test_can_list_posts(self):
        test = User.objects.get(username='test')
        Post.objects.create(owner=test, title='test title')
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logged_in_can_create_post(self):
        self.client.login(username='test', password='pass')
        response = self.client.post('/posts/', {'title': 'test title'})
        count = Post.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(count, 1)

    def test_unauthenticated_cannot_create_post(self):
        response = self.client.post('/posts/',
                                    {'title': 'unauthenticated post'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PostDetailViewTests(APITestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='pass')
        user2 = User.objects.create_user(username='user2', password='pass')
        Post.objects.create(
            owner=user1, title='test title', content='user1 content'
        )
        Post.objects.create(
            owner=user2, title='test title', content='user2 content'
        )

    def test_can_retrieve_post_valid_id(self):
        response = self.client.get('/posts/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'user1 content')

    def test_cannot_retrieve_post_invalid_id(self):
        response = self.client.get('/posts/3')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_their_post(self):
        self.client.login(username='user1', password='pass')
        response = self.client.put('/posts/1', {'title': 'changed title'})
        post = Post.objects.filter(pk=1).first()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(post.content, 'user1 content')
        self.assertEqual(post.title, 'changed title')

    def test_user_cannot_update_other_users_post(self):
        self.client.login(username='user1', password='pass')
        response = self.client.put('/posts/2', {'title': 'changed title'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
