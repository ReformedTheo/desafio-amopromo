from django.db.models import Model, TextChoices ,DateTimeField, CharField, PositiveIntegerField, TextField, JSONField

class ImportLogModel(Model):
    class Status(TextChoices):
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    start_time = DateTimeField(auto_now_add=True)
    end_time = DateTimeField(null=True, blank=True)
    status = CharField(max_length=10, choices=Status.choices)
    
    airports_created = PositiveIntegerField(default=0)
    airports_updated = PositiveIntegerField(default=0)

    created_iatas = JSONField(default=list, help_text="List of IATA codes for newly created airports.")
    updated_iatas = JSONField(default=list, help_text="List of IATA codes for updated airports.")
    
    details = TextField(blank=True, help_text="Contains error messages or other details.")

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"Import run on {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} - {self.status}"