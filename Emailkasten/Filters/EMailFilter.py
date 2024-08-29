import django_filters
from ..Models.EMailModel import EMailModel

class EMailFilter(django_filters.FilterSet):
    attachment_name_icontains = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='icontains')
    attachment_name = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='exact')
    correspondent_name_icontains = django_filters.CharFilter(field_name="emailcorrespondents__email_name", lookup_expr='icontains')
    correspondent_name = django_filters.CharFilter(field_name="emailcorrespondents__email_name", lookup_expr='exact')
    correspondent_address_icontains = django_filters.CharFilter(field_name="emailcorrespondents__email_address", lookup_expr='icontains')
    correspondent_address = django_filters.CharFilter(field_name="emailcorrespondents__email_address", lookup_expr='exact')
    
    class Meta:
        model = EMailModel
        fields = {
            'message_id': ['icontains', 'exact'],
            'datetime': ['gte', 'lte'],
            'email_subject': ['icontains', 'exact'],
            'bodytext': ['icontains'],
            'datasize': ['gte', 'lte']
        }