"""Sitemaps for search engines: the main pages and every category gallery."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from portfolio.models import Category


class StaticPageSitemap(Sitemap):
    def items(self):
        return ["home", "about", "contact"]

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    def items(self):
        return Category.objects.all()