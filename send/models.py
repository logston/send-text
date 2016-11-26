from django.db import models


class SendLog(models.Model):
    email = models.EmailField()

    sender = models.EmailField()

    subject = models.CharField(max_length=254)

    message = models.TextField(
        max_length=254,
        null=True,
        blank=True,
    )

    attachment = models.URLField(
        null=True,
        blank=True
    )

