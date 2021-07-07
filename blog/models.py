from django.db import models

# Create your models here.
class Blogpost(models.Model):
    post_id = models.AutoField(primary_key = True)
    title = models.CharField(max_length=50)
    genre = models.CharField(max_length=50, default="")
    head0 = models.CharField(max_length=100)
    chead0 = models.CharField(max_length=2000)
    head1 = models.CharField(max_length=100)
    chead1 = models.CharField(max_length=2000)
    head2 = models.CharField(max_length=100)
    chead2 = models.CharField(max_length=2000)
    pub_date = models.DateField()
    thumbnail = models.ImageField(upload_to='blog/images', default='')

    def __str__(self):
        return self.title