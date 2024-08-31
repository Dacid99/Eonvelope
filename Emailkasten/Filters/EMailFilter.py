import django_filters
from ..Models.EMailModel import EMailModel

class EMailFilter(django_filters.FilterSet):
    attachment_name__icontains = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='icontains')
    attachment_name__contains = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='contains')
    attachment_name__exact = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='exact')
    attachment_name__iexact = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='iexact')
    attachment_name__startswith = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='startswith')
    attachment_name__istartswith = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='istartswith')
    attachment_name__endswith = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='endswith')
    attachment_name__iendswith = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='iendswith')
    attachment_name__regex = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='regex')
    attachment_name__iregex = django_filters.CharFilter(field_name='attachments__file_name', lookup_expr='iregex')
    attachment_name__in = django_filters.BaseInFilter(field_name='attachments__file_name', lookup_expr='in')

    correspondent_name__icontains = django_filters.CharFilter(field_name="emailcorrespondents__correspondent__email_name", lookup_expr='icontains')
    correspondent_name__contains = django_filters.CharFilter(field_name="emailcorrespondents__correspondent__email_name", lookup_expr='contains')
    correspondent_name__exact = django_filters.CharFilter(field_name="emailcorrespondents__correspondent__email_name", lookup_expr='exact')
    correspondent_name__iexact = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_name', lookup_expr='iexact')
    correspondent_name__startswith = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_name', lookup_expr='startswith')
    correspondent_name__istartswith = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_name', lookup_expr='istartswith')
    correspondent_name__endswith = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_name', lookup_expr='endswith')
    correspondent_name__iendswith = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_name', lookup_expr='iendswith')
    correspondent_name__regex = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_name', lookup_expr='regex')
    correspondent_name__iregex = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_name', lookup_expr='iregex')
    correspondent_name__in = django_filters.BaseInFilter(field_name='emailcorrespondents__correspondent__email_name', lookup_expr='in')

    correspondent_address__icontains = django_filters.CharFilter(field_name="emailcorrespondents__correspondent__email_address", lookup_expr='icontains')
    correspondent_address__contains = django_filters.CharFilter(field_name="emailcorrespondents__correspondent__email_address", lookup_expr='contains')
    correspondent_address__exact = django_filters.CharFilter(field_name="emailcorrespondents__correspondent__email_address", lookup_expr='exact')
    correspondent_address__iexact = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_address', lookup_expr='iexact')
    correspondent_address__startswith = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_address', lookup_expr='startswith')
    correspondent_address__istartswith = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_address', lookup_expr='istartswith')
    correspondent_address__endswith = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_address', lookup_expr='endswith')
    correspondent_address__iendswith = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_address', lookup_expr='iendswith')
    correspondent_address__regex = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_address', lookup_expr='regex')
    correspondent_address__iregex = django_filters.CharFilter(field_name='emailcorrespondents__correspondent__email_address', lookup_expr='iregex')
    correspondent_address__in = django_filters.BaseInFilter(field_name='emailcorrespondents__correspondent__email_address', lookup_expr='in')

    correspondent_mention__exact = django_filters.CharFilter(field_name='emailcorrespondents__mention', lookup_expr='exact')

    account_address__icontains = django_filters.CharFilter(field_name='in_account__address', lookup_expr="icontains")
    account_address__contains = django_filters.CharFilter(field_name='in_account__address', lookup_expr="contains")
    account_address__exact = django_filters.CharFilter(field_name='in_account__address', lookup_expr="exact")
    account_address__iexact = django_filters.CharFilter(field_name='in_account__address', lookup_expr='iexact')
    account_address__startswith = django_filters.CharFilter(field_name='in_account__address', lookup_expr='startswith')
    account_address__istartswith = django_filters.CharFilter(field_name='in_account__address', lookup_expr='istartswith')
    account_address__endswith = django_filters.CharFilter(field_name='in_account__address', lookup_expr='endswith')
    account_address__iendswith = django_filters.CharFilter(field_name='in_account__address', lookup_expr='iendswith')
    account_address__regex = django_filters.CharFilter(field_name='in_account__address', lookup_expr='regex')
    account_address__iregex = django_filters.CharFilter(field_name='in_account__address', lookup_expr='iregex')
    account_address__in = django_filters.BaseInFilter(field_name='in_account__address', lookup_expr='in')

    account_host__icontains = django_filters.CharFilter(field_name='in_account__mail_host', lookup_expr="icontains")
    account_host__contains = django_filters.CharFilter(field_name='in_account__mail_host', lookup_expr="contains")
    account_host__exact = django_filters.CharFilter(field_name='in_account__mail_host', lookup_expr="exact")
    account_host__iexact = django_filters.CharFilter(field_name='in_account__mail_host', lookup_expr='iexact')
    account_host__startswith = django_filters.CharFilter(field_name='in_account__mail_host', lookup_expr='startswith')
    account_host__istartswith = django_filters.CharFilter(field_name='in_account__mail_host', lookup_expr='istartswith')
    account_host__endswith = django_filters.CharFilter(field_name='in_account__mail_host', lookup_expr='endswith')
    account_host__iendswith = django_filters.CharFilter(field_name='in_account__mail_host', lookup_expr='iendswith')
    account_host__regex = django_filters.CharFilter(field_name='in_account__mail_host', lookup_expr='regex')
    account_host__iregex = django_filters.CharFilter(field_name='in_account__mail_host', lookup_expr='iregex')
    account_host__in = django_filters.BaseInFilter(field_name='in_account__mail_host', lookup_expr='in')

    class Meta:
        model = EMailModel
        fields = {
            'message_id': ['icontains', 'contains', 'exact', 'iexact', 'startswith', 'istartswith', 'endswith', 'iendswith', 'regex', 'iregex', 'in'],
            'datetime': ['gte', 'lte'],
            'email_subject': ['icontains', 'contains', 'exact', 'iexact', 'startswith', 'istartswith', 'endswith', 'iendswith', 'regex', 'iregex', 'in'],
            'bodytext': ['icontains', 'contains', 'exact', 'iexact', 'startswith', 'istartswith', 'endswith', 'iendswith', 'regex', 'iregex', 'in'],
            'datasize': ['gte', 'lte', 'gt', 'lt'],
            'created': ['lte', 'gte']
        }