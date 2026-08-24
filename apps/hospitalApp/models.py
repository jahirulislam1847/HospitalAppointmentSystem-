from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Hospital(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    address = models.TextField()
    contact = models.CharField(max_length=20)
    email = models.EmailField()
    image = models.URLField(blank=True, null=True)
    search_count = models.PositiveIntegerField(default=0)

    # Relationship (FK -> Users: Super Admin)
    created_by = models.ForeignKey(
        'userApp.CustomUser',
        on_delete=models.PROTECT, # Protects the hospital record from deletion if the creator is still needed
        related_name='hospitals_created',
        limit_choices_to={'role': 'super_admin'} # Only super admins can create hospitals
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        # Only set slug if not provided manually
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitals'

