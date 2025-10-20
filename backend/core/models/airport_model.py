from django.db.models import Model, CharField, FloatField, DateTimeField

class Airport(Model):
    state = CharField(max_length=2)
    iata = CharField(max_length=3, unique=True, db_index=True)
    city = CharField(max_length=100)
    lat = FloatField()
    lon = FloatField()
    created_on = DateTimeField(auto_now_add=True)
    modified_on = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['iata']
        verbose_name = 'Airport'

    def __str__(self):
        return f"{self.city} ({self.iata})"