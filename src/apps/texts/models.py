from django.db import models


class Text(models.Model):
    key = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    text = models.TextField()

    def __str__(self):
        return f'{self.key} -> {self.name}'
