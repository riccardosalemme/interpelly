from django.db import models
from django.utils import timezone


class Province(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=1000, unique=True)
    active = models.BooleanField(default=False)
    telegram_thread_id = models.BigIntegerField(null=True, blank=True)
    last_scraped_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Interpello(models.Model):
    province = models.ForeignKey(Province, on_delete=models.PROTECT, related_name="interpelli")
    published_date = models.DateField(null=True, blank=True)
    title = models.TextField()
    description = models.TextField(blank=True)
    url = models.URLField(max_length=2000, unique=True)
    notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)
    telegram_message_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Updated by scraping, not by notification or admin edits.
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-published_date", "-pk"]

    def __str__(self):
        return self.title
