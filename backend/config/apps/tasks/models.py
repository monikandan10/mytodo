from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils.text import slugify


  
class Task(models.Model):
  CATEGORY_CHOICES = [
        ('work', 'Work'),
        ('personal', 'Personal'),
        ('home', 'Home'),
        ('health', 'Health & Fitness'),
        ('education', 'Education'),
        ('finance', 'Finance'),
        ('social', 'Social'),
        ('travel', 'Travel'),
        ('goals', 'Goals'),
        ('miscellaneous', 'Miscellaneous'),
    ]
  STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
  PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
  
  USER = get_user_model()
  
  user = models.ForeignKey(USER, on_delete=models.CASCADE)
  task_name = models.CharField(max_length=255)
  task_description = models.TextField()
  task_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='miscellaneous')
  task_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
  task_priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
  task_due_date = models.DateField()
  task_created_at = models.DateTimeField(auto_now_add=True)
  task_updated_at = models.DateTimeField(auto_now=True)
  task_completed_at = models.DateTimeField(null=True, blank=True)
  slug = models.SlugField()

  def __str__(self):
    return self.task_name


@receiver(pre_save, sender=Task)
def update_slug(sender, instance, **kwargs):
  if instance.task_name:
    instance.slug = slugify(instance.task_name)