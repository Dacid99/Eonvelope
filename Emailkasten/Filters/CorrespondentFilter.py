import django_filters
from ..Models.CorrespondentModel import CorrespondentModel

class CorrespondentFilter(django_filters.FilterSet):
    class Meta:
        model = CorrespondentModel
        fields = {
            'email_name': ['icontains', 'exact'],
            'email_address': ['icontains', 'exact'],
            'correspondentemails__mention': ['exact']
        }