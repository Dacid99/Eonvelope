import django_filters
from ..Models.EMailModel import EMailModel

class EMailFilter(django_filters.FilterSet):
    attachment_name__icontains = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='icontains')
    attachment_name__contains = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='contains')
    attachment_name__exact = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='exact')
    correspondent_name__icontains = django_filters.CharFilter(field_name="emailcorrespondents__correspondent__email_name", lookup_expr='icontains')
    correspondent_name__contains = django_filters.CharFilter(field_name="emailcorrespondents__correspondent__email_name", lookup_expr='contains')
    correspondent_name__exact = django_filters.CharFilter(field_name="emailcorrespondents__correspondent__email_name", lookup_expr='exact')
    correspondent_address__icontains = django_filters.CharFilter(field_name="emailcorrespondents__correspondent__email_address", lookup_expr='icontains')
    correspondent_address__contains = django_filters.CharFilter(field_name="emailcorrespondents__correspondent__email_address", lookup_expr='contains')
    correspondent_address__exact = django_filters.CharFilter(field_name="emailcorrespondents__correspondent__email_address", lookup_expr='exact')
    correspondent_mention__exact = django_filters.CharFilter(field_name='emailcorrespondents__mention', lookup_expr='exact')
    account_address__icontains = django_filters.CharFilter(field_name='in_account__address', lookup_expr="icontains")
    account_address__contains = django_filters.CharFilter(field_name='in_account__address', lookup_expr="contains")
    account_address__exact = django_filters.CharFilter(field_name='in_account__address', lookup_expr="exact")
    account_host__icontains = django_filters.CharFilter(field_name='in_account__mail_host', lookup_expr="icontains")
    account_host__contains = django_filters.CharFilter(field_name='in_account__mail_host', lookup_expr="contains")
    account_host__exact = django_filters.CharFilter(field_name='in_account__mail_host', lookup_expr="exact")

    class Meta:
        model = EMailModel
        fields = {
            'message_id': ['icontains', 'contains', 'exact'],
            'datetime': ['gte', 'lte'],
            'email_subject': ['icontains', 'contains', 'exact'],
            'bodytext': ['icontains', 'contains'],
            'datasize': ['gte', 'lte'],
            'created': ['lte', 'gte']
        }