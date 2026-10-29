from datetime import timedelta
import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Post, Tag
from .views import custom_500
from .templatetags.reading_time import reading_time


class ReadingTimeTests(TestCase):
    def test_estimate_rounds_up_and_has_a_one_minute_minimum(self):
        self.assertEqual(reading_time(None), 1)
        self.assertEqual(reading_time(""), 1)
        self.assertEqual(reading_time("word " * 200), 1)
        self.assertEqual(reading_time("word " * 201), 2)
        self.assertEqual(reading_time("<p>" + "word " * 400 + "</p>"), 2)


class MagazineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(username="author")
        cls.games = Category.objects.create(name="Games")
        cls.tech = Category.objects.create(name="Tecnologia")
        cls.posts = []
        for index in range(8):
            post = Post.objects.create(
                author=cls.author,
                title=f"Descoberta número {index}",
                slug=f"descoberta-{index}",
                content="Uma nova perspectiva para compartilhar. " * 70,
                status="published",
                category=cls.games if index < 5 else cls.tech,
            )
            Post.objects.filter(pk=post.pk).update(
                created_at=timezone.now() + timedelta(minutes=index)
            )
            cls.posts.append(post)
        cls.draft = Post.objects.create(
            author=cls.author,
            title="Rascunho secreto",
            slug="rascunho-secreto",
            content="Este texto ainda está em preparação.",
            status="draft",
            category=cls.games,
        )

    def test_home_renders_newest_published_feature_and_categories(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_list.html")
        self.assertTemplateUsed(response, "blog/includes/post_card.html")
        self.assertEqual(response.context["featured_post"].pk, self.posts[-1].pk)
        self.assertEqual(len(response.context["page_obj"]), 6)
        counts = {cat.name: cat.published_count for cat in response.context["categories"]}
        self.assertEqual(counts, {"Games": 5, "Tecnologia": 3})
        self.assertContains(response, "NEO")
        self.assertContains(response, "blog/favicon.svg")
        self.assertContains(response, "Featured")
        self.assertContains(response, "Next")
        self.assertNotContains(response, self.draft.title)

    def test_pagination_shows_remaining_posts_without_repeating_hero(self):
        response = self.client.get(reverse("home"), {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 2)
        self.assertContains(response, "Previous")
        self.assertNotContains(response, "Featured")
        self.assertNotContains(response, self.draft.title)

    def test_related_articles_share_category_and_exclude_current_and_drafts(self):
        current = self.posts[0]
        response = self.client.get(reverse("post_detail", args=[current.slug]))
        self.assertEqual(response.status_code, 200)
        related = list(response.context["related_posts"])
        self.assertEqual(len(related), 3)
        self.assertEqual([p.pk for p in related], [p.pk for p in reversed(self.posts[2:5])])
        self.assertTrue(all(p.category_id == current.category_id for p in related))
        self.assertNotIn(current.pk, [p.pk for p in related])
        self.assertNotIn(self.draft.pk, [p.pk for p in related])
        self.assertContains(response, "min read")
        self.assertContains(response, reverse("post_edit", args=[current.slug]))
        self.assertContains(response, reverse("post_delete", args=[current.slug]))

    def test_draft_detail_remains_unavailable(self):
        response = self.client.get(reverse("post_detail", args=[self.draft.slug]))
        self.assertEqual(response.status_code, 404)

    def test_authenticated_author_can_view_own_draft(self):
        self.client.force_login(self.author)

        response = self.client.get(reverse("post_detail", args=[self.draft.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.draft.title)

    def test_other_authenticated_user_cannot_view_draft(self):
        visitor = get_user_model().objects.create_user(username="visitor")
        self.client.force_login(visitor)

        response = self.client.get(reverse("post_detail", args=[self.draft.slug]))

        self.assertEqual(response.status_code, 404)

    def test_non_author_sees_custom_forbidden_page_when_editing_post(self):
        user_model = get_user_model()
        visitor = user_model.objects.create_user(username="visitor")
        post = self.posts[0]
        self.client.force_login(visitor)

        response = self.client.get(reverse("post_edit", args=[post.slug]))

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "blog/403.html")
        self.assertContains(response, "You can't access this page.", status_code=403)

    def test_anonymous_user_sees_custom_forbidden_page_when_editing_or_deleting_post(self):
        post = self.posts[0]

        for url_name in ("post_edit", "post_delete"):
            with self.subTest(action=url_name):
                response = self.client.get(reverse(url_name, args=[post.slug]))

                self.assertEqual(response.status_code, 403)
                self.assertTemplateUsed(response, "blog/403.html")
                self.assertContains(
                    response,
                    "You can't access this page.",
                    status_code=403,
                )

    def test_post_creation_shows_success_message(self):
        self.client.force_login(self.author)

        response = self.client.post(reverse("post_create"), {
            "title": "Mensagem de sucesso no artigo",
            "content": "Uma publicação criada para testar a mensagem.",
            "category": self.games.pk,
            "status": "published",
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Post published successfully!")

    def test_password_reset_flow_sends_link_and_changes_password(self):
        user = get_user_model().objects.create_user(
            username="reset-user",
            email="reset@example.com",
            password="OriginalPassword!234",
        )

        with self.settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"):
            response = self.client.post(reverse("password_reset"), {
                "email": user.email,
            })

        self.assertRedirects(response, reverse("password_reset_done"))
        response = self.client.get(reverse("password_reset_done"))
        self.assertTemplateUsed(response, "blog/password_reset_done.html")
        self.assertEqual(len(mail.outbox), 1)
        reset_url_match = re.search(
            r"http://testserver(?P<path>/reset/[^\s]+)",
            mail.outbox[0].body,
        )
        self.assertIsNotNone(reset_url_match)
        reset_path = reset_url_match.group("path")
        response = self.client.get(reset_path, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/password_reset_confirm.html")
        confirm_path = response.request["PATH_INFO"]

        response = self.client.post(confirm_path, {
            "new_password1": "NewStrongPassword!456",
            "new_password2": "NewStrongPassword!456",
        })

        self.assertRedirects(response, reverse("password_reset_complete"))
        response = self.client.get(reverse("password_reset_complete"))
        self.assertTemplateUsed(response, "blog/password_reset_complete.html")
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewStrongPassword!456"))

    def test_empty_blog_displays_real_create_link(self):
        Post.objects.all().delete()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["featured_post"])
        self.assertContains(response, "The whole universe starts with one idea.")
        self.assertContains(response, reverse("post_create"))
        self.assertNotContains(response, "Featured")

    def test_custom_not_found_page_is_used(self):
        response = self.client.get("/page-that-does-not-exist/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(response, "This page doesn’t exist.", status_code=404)

    def test_custom_server_error_page_renders(self):
        response = custom_500(RequestFactory().get("/"))

        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "Something went wrong.", status_code=500)

    def test_no_cover_no_category_and_no_tags_render(self):
        post = Post.objects.create(
            title="Uma história independente",
            slug="sem-categoria",
            content="Texto sem uma capa ou categoria.",
            status="published",
        )
        response = self.client.get(reverse("post_detail", args=[post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Article")
        self.assertNotContains(response, "article-cover")
        self.assertEqual(len(response.context["related_posts"]), 3)
        home = self.client.get(reverse("home"))
        self.assertContains(home, "post-card__cover--empty")

    def test_article_content_remains_escaped_and_tags_render(self):
        post = self.posts[0]
        post.content = '<script>alert("x")</script>\n\nTexto normal.'
        post.save()
        tag = Tag.objects.create(name="Django")
        post.tags.add(tag)
        response = self.client.get(reverse("post_detail", args=[post.slug]))
        self.assertContains(response, "#Django")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, '<script>alert("x")</script>')

    def test_existing_static_and_crud_pages_render(self):
        self.client.force_login(self.author)

        for name, args in [
            ("about", []),
            ("contact", []),
            ("post_create", []),
            ("post_edit", [self.posts[0].slug]),
            ("post_delete", [self.posts[0].slug]),
        ]:
            with self.subTest(page=name):
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Neo Niigata")

    def test_existing_publish_edit_and_delete_flow(self):
        self.client.force_login(self.author)

        response = self.client.post(reverse("post_create"), {
            "title": "Um projeto que vale compartilhar",
            "content": "Descobertas feitas durante a criação do primeiro portal.",
            "category": self.games.pk,
            "status": "published",
        })
        post = Post.objects.get(title="Um projeto que vale compartilhar")
        self.assertRedirects(response, reverse("post_detail", args=[post.slug]))
        response = self.client.post(reverse("post_edit", args=[post.slug]), {
            "title": "Um projeto que vale compartilhar",
            "content": "Aprendizados atualizados depois de construir o portal.",
            "category": self.games.pk,
            "status": "published",
        })
        self.assertRedirects(response, reverse("post_detail", args=[post.slug]))
        post.refresh_from_db()
        self.assertIn("atualizados", post.content)
        response = self.client.post(reverse("post_delete", args=[post.slug]))
        self.assertRedirects(response, reverse("home"))
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())
