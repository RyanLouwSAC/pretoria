from django.db import models
from django.core.validators import RegexValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=250, blank=True, null=True)  # Allow null and blank

    def __str__(self):
        return self.name

class Business(models.Model):
    name = models.CharField(max_length=255)
    logo_url = models.URLField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    social_links = models.JSONField(blank=True, null=True)  # Store links in JSON format
    address = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Promotion(models.Model):
      title = models.CharField(max_length=255)
      def __str__(self):
        return self.title

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    published_at = models.DateTimeField()
    name = models.CharField(max_length=255 ,null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    number = models.CharField(
        max_length=13,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,13}$', message="Enter a valid phone number.")],
        verbose_name="Phone Number",
        null=True,  # Allow null values in the database
        blank=True  # Allow blank input in forms
    )


    websiteLink = models.URLField(max_length=255, blank=True, null=True)  # Updated to URLField for validation
    isOnPromotion = models.BooleanField(default=False)  # BooleanField, default set to False

    def __str__(self):
        return self.title

class Membership(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    membership_benefits = models.TextField()
    contact_info = models.TextField()

    def __str__(self):
        return f"{self.business.name} Membership"
