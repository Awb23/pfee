from django.db import models
from PPFE.settings import AUTH_USER_MODEL

class Category(models.Model):
    name = models.CharField(max_length=12)  # A, B, C...
    description = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_locked = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Word(models.Model):
    TYPES = (
        ('hayawan', 'Hayawan'),
        ('verb', 'Verb'),
        ('insan', 'Insan'),
        ('phrase', 'Phrase'),
        ('dessin', 'Dessin'),
        ('test', 'test'),
    )
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPES)
    level = models.IntegerField(default=1)
    image = models.ImageField(upload_to='words/', null=True, blank=True)

    def __str__(self):
        return self.name

class Paragraph(models.Model):
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    level = models.IntegerField(default=3)
    image = models.ImageField(upload_to='paragraphs/', null=True, blank=True)

    def __str__(self):
        return self.text[:50]

class UserProgress(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, null=True, blank=True, on_delete=models.CASCADE)
    paragraph = models.ForeignKey(Paragraph, null=True, blank=True, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    time_taken = models.FloatField(null=True)
    difficulty = models.FloatField(default=0.0)
    

    def __str__(self):
        return f"{self.user.username} - {self.word or self.paragraph}"

class UserCategoryScore(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'category')  # Kul user 3ndo score wahd ghir f kul category

    def __str__(self):
        return f"{self.user.username} - {self.category.name} - {self.score}"

class UserProgressHistory(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, null=True, blank=True, on_delete=models.CASCADE)
    paragraph = models.ForeignKey(Paragraph, null=True, blank=True, on_delete=models.CASCADE)
    correct_answer_date = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)
    time_taken = models.FloatField(null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.word or self.paragraph} - {self.correct_answer_date}"