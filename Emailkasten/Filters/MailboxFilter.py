import django_filters
from ..Models.MailboxModel import MailboxModel

class MailboxFilter(django_filters.FilterSet):

    mail_address__icontains = django_filters.CharFilter(field_name='account__mail_address', lookup_expr='icontains')
    mail_address__contains = django_filters.CharFilter(field_name='account__mail_address', lookup_expr='contains')
    mail_address__exact = django_filters.CharFilter(field_name='account__mail_address', lookup_expr='exact')
    mail_address__iexact = django_filters.CharFilter(field_name='account__mail_address', lookup_expr='iexact')
    mail_address__startswith = django_filters.CharFilter(field_name='account__mail_address', lookup_expr='startswith')
    mail_address__istartswith = django_filters.CharFilter(field_name='account__mail_address', lookup_expr='istartswith')
    mail_address__endswith = django_filters.CharFilter(field_name='account__mail_address', lookup_expr='endswith')
    mail_address__iendswith = django_filters.CharFilter(field_name='account__mail_address', lookup_expr='iendswith')
    mail_address__regex = django_filters.CharFilter(field_name='account__mail_address', lookup_expr='regex')
    mail_address__iregex = django_filters.CharFilter(field_name='account__mail_address', lookup_expr='iregex')
    mail_address__in = django_filters.BaseInFilter(field_name='account__mail_address', lookup_expr='in')

    mail_host__icontains = django_filters.CharFilter(field_name='account__mail_host', lookup_expr='icontains')
    mail_host__contains = django_filters.CharFilter(field_name='account__mail_host', lookup_expr='contains')
    mail_host__exact = django_filters.CharFilter(field_name='account__mail_host', lookup_expr='exact')
    mail_host__iexact = django_filters.CharFilter(field_name='account__mail_host', lookup_expr='iexact')
    mail_host__startswith = django_filters.CharFilter(field_name='account__mail_host', lookup_expr='startswith')
    mail_host__istartswith = django_filters.CharFilter(field_name='account__mail_host', lookup_expr='istartswith')
    mail_host__endswith = django_filters.CharFilter(field_name='account__mail_host', lookup_expr='endswith')
    mail_host__iendswith = django_filters.CharFilter(field_name='account__mail_host', lookup_expr='iendswith')
    mail_host__regex = django_filters.CharFilter(field_name='account__mail_host', lookup_expr='regex')
    mail_host__iregex = django_filters.CharFilter(field_name='account__mail_host', lookup_expr='iregex')
    mail_host__in = django_filters.BaseInFilter(field_name='account__mail_host', lookup_expr='in')

    protocol__iexact = django_filters.CharFilter(field_name='account__protocol', lookup_expr='iexact')
    protocol__icontains = django_filters.CharFilter(field_name='account__protocol', lookup_expr='icontains')
    protocol__in = django_filters.BaseInFilter(field_name='account__protocol', lookup_expr='in')

    is_healthy__exact = django_filters.BooleanFilter(field_name='account__is_healthy', lookup_expr='exact')
    
    class Meta:
        model = MailboxModel
        fields = {
            'name': ['icontains', 'contains', 'exact', 'iexact', 'startswith', 'istartswith', 'endswith', 'iendswith', 'regex', 'iregex', 'in'],
            'cycle_interval': ['exact', 'lte', 'gte', 'lt', 'gt'],
            'fetching_criterion': ['iexact'],
            'save_toEML': ['exact'],
            'save_attachments': ['exact'],
            'is_fetched': ['exact'],
            'created': ['lte', 'gte'],
            'updated': ['lte', 'gte']
        }