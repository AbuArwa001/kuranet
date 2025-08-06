# polls/models.py
from django.db import models
from users.models import User

class Poll(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('draft', 'Draft'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polls')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closes_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return self.title

class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text
class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poll')

    def __str__(self):
        return f"{self.user} -> {self.option}"
    
    def save(self, *args, **kwargs):
        # Automatically set the poll from the option when saving
        if not self.poll_id:
            self.poll = self.option.poll
        super().save(*args, **kwargs)

# class Vote(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     option = models.ForeignKey(PollOption, on_delete=models.CASCADE)
#     voted_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'option__poll')  # One vote per user per poll

#     def __str__(self):
#         return f"{self.user} -> {self.option}"