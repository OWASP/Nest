"""Analytics app UserSearchQuery model."""

from django.db import models

class UserSearchQuery(models.Model):
    """UserSearchQuery model."""
    
    class Meta:
        db_table = "analytics_usersearchquery"
        verbose_name = "User Search Query"
        verbose_name_plural = "User Search Queries"
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['category']),
            models.Index(fields=['source']),
            models.Index(fields=['timestamp']),
        ]
        
    query = models.TextField()
    source = models.CharField(
        max_length=50,
        choices=[
            ('nestbot', 'NestBot'),
            ('frontend', 'Frontend'),
        ],
        default='frontend'
    )
    category = models.CharField(
        max_length=20,
        choices=[
        ('projects', 'Projects'),
        ('chapters', 'Chapters'),
        ('committees', 'Committees'),
        ('others', 'Others'),
        ],
        default='others',
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.query:
            self.query_length = len(self.query)
        super(UserSearchQuery, self).save(*args, **kwargs)

    def __str__(self):
        """UserSearchQuery human readable representation."""
        return f"Query: {self.query} | Source: {self.source} | Time: {self.timestamp}"

    
