import os

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Post


@receiver(post_delete, sender=Post)
def delete_post_image(sender, instance, **kwargs):
    if instance.cover_image and os.path.isfile(instance.cover_image.path):
        os.remove(instance.cover_image.path)


@receiver(pre_save, sender=Post)
def delete_old_cover_image(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        previous = Post.objects.get(pk=instance.pk)
    except Post.DoesNotExist:
        return

    if previous.cover_image and previous.cover_image != instance.cover_image:
        if os.path.isfile(previous.cover_image.path):
            os.remove(previous.cover_image.path)
