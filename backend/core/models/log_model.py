from django.db import models
from django.utils import timezone


class ApplicationLog(models.Model):
    """Model to store application logs in the database."""
    
    class LogLevel(models.TextChoices):
        DEBUG = 'DEBUG', 'Debug'
        INFO = 'INFO', 'Info'
        WARNING = 'WARNING', 'Warning'
        ERROR = 'ERROR', 'Error'
        CRITICAL = 'CRITICAL', 'Critical'
    
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    level = models.CharField(max_length=10, choices=LogLevel.choices, db_index=True)
    module = models.CharField(max_length=255, help_text="Module or file where the log originated")
    message = models.TextField()
    extra_data = models.JSONField(null=True, blank=True, help_text="Additional context data")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'level']),
        ]
    
    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.level}: {self.message[:50]}"
