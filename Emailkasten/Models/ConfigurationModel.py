from django.db import models

class ConfigurationModel(models.Model):
    CATEGORY_CHOICES = [
        ('DAEMON', 'Daemon Config'),
        ('PARSING', 'Parsing Config'),
        ('STORAGE', 'Storage Config'),
        ('LOGGING', 'Logging Config'),
    ]
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=50)
    key = models.CharField(max_length=255)
    value_bool = models.BooleanField(null=True, blank=True)
    value_int = models.IntegerField(null=True, blank=True)
    value_char = models.CharField(null=True, blank=True)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = "config"
        unique_together = ('category', 'key')

    def __str__(self):
        return f"Setting {self.category}.{self.key}"
    
    def get_value(self):
        if self.value_bool is not None:
            return self.value_bool
        elif self.value_int is not None:
            return self.value_int
        elif self.value_char is not None:
            return self.value_char
        return None