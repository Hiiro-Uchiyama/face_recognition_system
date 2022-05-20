from django.db import models

class FaceData(models.Model):
    user_id = models.IntegerField()
    name = models.CharField('名前', max_length=50)

class FaceDataImage(models.Model):
    images = models.ImageField(upload_to='dataset')

class FaceDataGallery(models.Model):
    images = models.ImageField(upload_to='dataset', max_length=255)