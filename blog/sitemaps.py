from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import BlogPost, Category
from playlists.models import Playlist

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return [
            'blog:home',
            'blog:about',
            'blog:contact',
            'blog:list',
            'blog:trending',

        ]

    def location(self, item):
        return reverse(item)

class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return BlogPost.objects.filter(published_at__lte=timezone.now())


    def lastmod(self, obj):
        return obj.created_at

class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('blog:list') + f'?category={obj.slug}'

class PlaylistSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Playlist.objects.all()

    def location(self, obj):
        return reverse('playlist_detail')

# Combine all sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'blog_posts': BlogPostSitemap,
    'categories': CategorySitemap,
    'playlists': PlaylistSitemap,
}