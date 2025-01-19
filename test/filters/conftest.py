import datetime

import pytest
from freezegun import freeze_time
from model_bakery import baker
from faker import Faker

from Emailkasten.Models.AccountModel import AccountModel
from Emailkasten.Models.AttachmentModel import AttachmentModel
from Emailkasten.Models.CorrespondentModel import CorrespondentModel
from Emailkasten.Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from Emailkasten.Models.ImageModel import ImageModel
from Emailkasten.Models.MailingListModel import MailingListModel
from Emailkasten.Models.MailboxModel import MailboxModel
from Emailkasten.Models.EMailModel import EMailModel
from Emailkasten.Models.DaemonModel import DaemonModel


def datetime_quarter(datetime: datetime.datetime) -> int:
    return (datetime.month - 1) // 3 + 1

INT_TEST_ITEMS = [
    0,
    1,
    2
]
LESSER_INT = -5
GREATER_INT = 6
DISJOINT_INT_RANGE = [7,10]

INT_TEST_PARAMETERS = [
    ("__lte", INT_TEST_ITEMS[1], [0,1]),
    ("__gte", INT_TEST_ITEMS[1], [1,2]),
    ("__lt", INT_TEST_ITEMS[2], [0,1]),
    ("__gt", INT_TEST_ITEMS[0], [1,2]),
    ("", INT_TEST_ITEMS[1], [1]),
    ("__in", INT_TEST_ITEMS[0:2], [0,1]),
    ("__range", INT_TEST_ITEMS[0:2], [0,1]),

    ("__lte", LESSER_INT, []),
    ("__gte", GREATER_INT, []),
    ("__lt", LESSER_INT, []),
    ("__gt", GREATER_INT, []),
    ("", GREATER_INT, []),
    ("__in", DISJOINT_INT_RANGE, []),
    ("__range", DISJOINT_INT_RANGE, [])
]

FLOAT_TEST_ITEMS = [
    0.5,
    1,
    2.3
]
LESSER_FLOAT = -5.4
GREATER_FLOAT = 6.1
DISJOINT_FLOAT_RANGE = [7.3, 10.2]

FLOAT_TEST_PARAMETERS = [
    ("__lte", FLOAT_TEST_ITEMS[1], [0,1]),
    ("__gte", FLOAT_TEST_ITEMS[1], [1,2]),
    ("__range", FLOAT_TEST_ITEMS[0:2], [0,1]),

    ("__lte", LESSER_FLOAT, []),
    ("__gte", GREATER_FLOAT, []),
    ("__range", DISJOINT_FLOAT_RANGE, []),
]

BOOL_TEST_ITEMS = [
    True,
    False,
    False
]

BOOL_TEST_PARAMETERS = [
    ("", BOOL_TEST_ITEMS[0], [0]),
    ("", BOOL_TEST_ITEMS[1], [1,2])
]

TEXT_TEST_ITEMS = [
        'A1bCD',
        'ZyX9D',
        'ZbC8W'
    ]

TEXT_TEST_PARAMETERS = [
        ("__icontains", TEXT_TEST_ITEMS[0][2:4].lower(), [0,2]),
        ("__contains", TEXT_TEST_ITEMS[0][2:4], [0,2]),
        ("", TEXT_TEST_ITEMS[1], [1]),
        ("__iexact", TEXT_TEST_ITEMS[1].lower(), [1]),
        ("__startswith", TEXT_TEST_ITEMS[1][0], [1,2]),
        ("__istartswith", TEXT_TEST_ITEMS[1][0].lower(), [1,2]),
        ("__endswith", TEXT_TEST_ITEMS[1][-1], [0,1]),
        ("__iendswith", TEXT_TEST_ITEMS[1][-1].lower(), [0,1]),
        ("__regex", r'\w{3}\d\w', [1,2]),
        ("__iregex", r'\w{3}\d\w', [1,2]),
        ("__in", TEXT_TEST_ITEMS[0:2], [0,1]),

        ("__icontains", 'op', []),
        ("__contains", 'oP', []),
        ("", 'No5PQ', []),
        ("__iexact", 'no5pq', []),
        ("__startswith", 'N', []),
        ("__istartswith", 'n', []),
        ("__endswith", 'Q', []),
        ("__iendswith", 'q', []),
        ("__regex", r'\w{2}\d\w{2}', []),
        ("__iregex", r'\w{2}\d\w{2}', []),
        ("__in", ['No5PQ'], [])
    ]

DATETIME_TEST_ITEMS = [
    datetime.datetime(2001,3,7,10,20,20),
    datetime.datetime(2002,6,13,11,30,30),
    datetime.datetime(2003,8,15,12,40,40)
]
LESSER_DATETIME = datetime.datetime(1990,2,5,5,10,10)
GREATER_DATETIME = datetime.datetime(2020,10,24,20,50,50)
DISJOINT_DATETIME_RANGE = [datetime.datetime(2020,10,24,20,50,50), datetime.datetime(2021,11,28,21,55,55)]

DATETIME_TEST_PARAMETERS = [
    ("__date", DATETIME_TEST_ITEMS[1], [1]),
    ("__date__gte", DATETIME_TEST_ITEMS[1], [1,2]),
    ("__date__lte", DATETIME_TEST_ITEMS[1], [0,1]),
    ("__date__gt", DATETIME_TEST_ITEMS[0], [1,2]),
    ("__date__lt", DATETIME_TEST_ITEMS[2], [0,1]),
    ("__date__in", DATETIME_TEST_ITEMS[0:2], [0,1]),
    ("__date__range", DATETIME_TEST_ITEMS[1:3], [1,2]),
    ("__time", DATETIME_TEST_ITEMS[1].time(), [1]),
    ("__time__gte", DATETIME_TEST_ITEMS[1].time(), [1,2]),
    ("__time__lte", DATETIME_TEST_ITEMS[1].time(), [0,1]),
    ("__time__gt", DATETIME_TEST_ITEMS[0].time(), [1,2]),
    ("__time__lt", DATETIME_TEST_ITEMS[2].time(), [0,1]),
    ("__time__in", [item.time() for item in DATETIME_TEST_ITEMS[0:2]], [0,1]),
    ("__time__range", [item.time() for item in DATETIME_TEST_ITEMS[1:3]], [1,2]),
    ("__iso_year", DATETIME_TEST_ITEMS[2].isocalendar().year, [2]),
    ("__iso_year__gte", DATETIME_TEST_ITEMS[1].isocalendar().year, [1,2]),
    ("__iso_year__lte", DATETIME_TEST_ITEMS[1].isocalendar().year, [0,1]),
    ("__iso_year__gt", DATETIME_TEST_ITEMS[0].isocalendar().year, [1,2]),
    ("__iso_year__lt", DATETIME_TEST_ITEMS[2].isocalendar().year, [0,1]),
    ("__iso_year__in", [item.isocalendar().year for item in DATETIME_TEST_ITEMS[0:2]], [0,1]),
    ("__iso_year__range", [item.isocalendar().year for item in DATETIME_TEST_ITEMS[1:3]], [1,2]),
    ("__month", DATETIME_TEST_ITEMS[1].month, [1]),
    ("__month__gte", DATETIME_TEST_ITEMS[1].month, [1,2]),
    ("__month__lte", DATETIME_TEST_ITEMS[1].month, [0,1]),
    ("__month__gt", DATETIME_TEST_ITEMS[0].month, [1,2]),
    ("__month__lt", DATETIME_TEST_ITEMS[2].month, [0,1]),
    ("__month__in", [item.month for item in DATETIME_TEST_ITEMS[0:2]], [0,1]),
    ("__month__range", [item.month for item in DATETIME_TEST_ITEMS[1:3]], [1,2]),
    ("__quarter", datetime_quarter(DATETIME_TEST_ITEMS[1]), [1]),
    ("__quarter__gte", datetime_quarter(DATETIME_TEST_ITEMS[1]), [1,2]),
    ("__quarter__lte", datetime_quarter(DATETIME_TEST_ITEMS[1]), [0,1]),
    ("__quarter__gt", datetime_quarter(DATETIME_TEST_ITEMS[0]), [1,2]),
    ("__quarter__lt", datetime_quarter(DATETIME_TEST_ITEMS[2]), [0,1]),
    ("__quarter__in", [datetime_quarter(item) for item in DATETIME_TEST_ITEMS[0:2]], [0,1]),
    ("__quarter__range", [datetime_quarter(item) for item in DATETIME_TEST_ITEMS[1:3]], [1,2]),
    ("__week", DATETIME_TEST_ITEMS[1].isocalendar().week, [1]),
    ("__week__gte", DATETIME_TEST_ITEMS[1].isocalendar().week, [1,2]),
    ("__week__lte", DATETIME_TEST_ITEMS[1].isocalendar().week, [0,1]),
    ("__week__gt", DATETIME_TEST_ITEMS[0].isocalendar().week, [1,2]),
    ("__week__lt", DATETIME_TEST_ITEMS[2].isocalendar().week, [0,1]),
    ("__week__in", [item.isocalendar().week for item in DATETIME_TEST_ITEMS[0:2]], [0,1]),
    ("__week__range", [item.isocalendar().week for item in DATETIME_TEST_ITEMS[1:3]], [1,2]),
    ("__iso_week_day", DATETIME_TEST_ITEMS[1].isoweekday(), [1]),
    ("__iso_week_day__gte", DATETIME_TEST_ITEMS[1].isoweekday(), [1,2]),
    ("__iso_week_day__lte", DATETIME_TEST_ITEMS[1].isoweekday(), [0,1]),
    ("__iso_week_day__gt", DATETIME_TEST_ITEMS[0].isoweekday(), [1,2]),
    ("__iso_week_day__lt", DATETIME_TEST_ITEMS[2].isoweekday(), [0,1]),
    ("__iso_week_day__in", [item.isoweekday() for item in DATETIME_TEST_ITEMS[0:2]], [0,1]),
    ("__iso_week_day__range", [item.isoweekday() for item in DATETIME_TEST_ITEMS[1:3]], [1,2]),
    ("__day", DATETIME_TEST_ITEMS[1].day, [1]),
    ("__day__gte", DATETIME_TEST_ITEMS[1].day, [1,2]),
    ("__day__lte", DATETIME_TEST_ITEMS[1].day, [0,1]),
    ("__day__gt", DATETIME_TEST_ITEMS[0].day, [1,2]),
    ("__day__lt", DATETIME_TEST_ITEMS[2].day, [0,1]),
    ("__day__in", [item.day for item in DATETIME_TEST_ITEMS[0:2]], [0,1]),
    ("__day__range", [item.day for item in DATETIME_TEST_ITEMS[1:3]], [1,2]),
    ("__hour", DATETIME_TEST_ITEMS[1].hour, [1]),
    ("__hour__gte", DATETIME_TEST_ITEMS[1].hour, [1,2]),
    ("__hour__lte", DATETIME_TEST_ITEMS[1].hour, [0,1]),
    ("__hour__gt", DATETIME_TEST_ITEMS[0].hour, [1,2]),
    ("__hour__lt", DATETIME_TEST_ITEMS[2].hour, [0,1]),
    ("__hour__in", [item.hour for item in DATETIME_TEST_ITEMS[0:2]], [0,1]),
    ("__hour__range", [item.hour for item in DATETIME_TEST_ITEMS[1:3]], [1,2]),
    ("__minute", DATETIME_TEST_ITEMS[1].minute, [1]),
    ("__minute__gte", DATETIME_TEST_ITEMS[1].minute, [1,2]),
    ("__minute__lte", DATETIME_TEST_ITEMS[1].minute, [0,1]),
    ("__minute__gt", DATETIME_TEST_ITEMS[0].minute, [1,2]),
    ("__minute__lt", DATETIME_TEST_ITEMS[2].minute, [0,1]),
    ("__minute__in", [item.minute for item in DATETIME_TEST_ITEMS[0:2]], [0,1]),
    ("__minute__range", [item.minute for item in DATETIME_TEST_ITEMS[1:3]], [1,2]),
    ("__second", DATETIME_TEST_ITEMS[1].second, [1]),
    ("__second__gte", DATETIME_TEST_ITEMS[1].second, [1,2]),
    ("__second__lte", DATETIME_TEST_ITEMS[1].second, [0,1]),
    ("__second__gt", DATETIME_TEST_ITEMS[0].second, [1,2]),
    ("__second__lt", DATETIME_TEST_ITEMS[2].second, [0,1]),
    ("__second__in", [item.second for item in DATETIME_TEST_ITEMS[0:2]], [0,1]),
    ("__second__range", [item.second for item in DATETIME_TEST_ITEMS[1:3]], [1,2]),

    ("__date", GREATER_DATETIME, []),
    ("__date__gte", GREATER_DATETIME, []),
    ("__date__lte", LESSER_DATETIME, []),
    ("__date__gt", GREATER_DATETIME, []),
    ("__date__lt", LESSER_DATETIME, []),
    ("__date__in", DISJOINT_DATETIME_RANGE, []),
    ("__date__range", DISJOINT_DATETIME_RANGE, []),
    ("__time", GREATER_DATETIME.time(), []),
    ("__time__gte", GREATER_DATETIME.time(), []),
    ("__time__lte", LESSER_DATETIME.time(), []),
    ("__time__gt", GREATER_DATETIME.time(), []),
    ("__time__lt", LESSER_DATETIME.time(), []),
    ("__time__in", [item.time() for item in DISJOINT_DATETIME_RANGE], []),
    ("__time__range", [item.time() for item in DISJOINT_DATETIME_RANGE], []),
    ("__iso_year", GREATER_DATETIME.isocalendar().year, []),
    ("__iso_year__gte", GREATER_DATETIME.isocalendar().year, []),
    ("__iso_year__lte", LESSER_DATETIME.isocalendar().year, []),
    ("__iso_year__gt", GREATER_DATETIME.isocalendar().year, []),
    ("__iso_year__lt", LESSER_DATETIME.isocalendar().year, []),
    ("__iso_year__in", [item.isocalendar().year for item in DISJOINT_DATETIME_RANGE], []),
    ("__iso_year__range", [item.isocalendar().year for item in DISJOINT_DATETIME_RANGE], []),
    ("__month", GREATER_DATETIME.month, []),
    ("__month__gte", GREATER_DATETIME.month, []),
    ("__month__lte", LESSER_DATETIME.month, []),
    ("__month__gt", GREATER_DATETIME.month, []),
    ("__month__lt", LESSER_DATETIME.month, []),
    ("__month__in", [item.month for item in DISJOINT_DATETIME_RANGE], []),
    ("__month__range", [item.month for item in DISJOINT_DATETIME_RANGE], []),
    ("__quarter", datetime_quarter(GREATER_DATETIME), []),
    ("__quarter__gte", datetime_quarter(GREATER_DATETIME), []),
    ("__quarter__lte", datetime_quarter(LESSER_DATETIME), [0]),
    ("__quarter__gt", datetime_quarter(GREATER_DATETIME), []),
    ("__quarter__lt", datetime_quarter(LESSER_DATETIME), []),
    ("__quarter__in", [datetime_quarter(item) for item in DISJOINT_DATETIME_RANGE], []),
    ("__quarter__range", [datetime_quarter(item) for item in DISJOINT_DATETIME_RANGE], []),
    ("__week", GREATER_DATETIME.isocalendar().week, []),
    ("__week__gte", GREATER_DATETIME.isocalendar().week, []),
    ("__week__lte", LESSER_DATETIME.isocalendar().week, []),
    ("__week__gt", GREATER_DATETIME.isocalendar().week, []),
    ("__week__lt", LESSER_DATETIME.isocalendar().week, []),
    ("__week__in", [item.isocalendar().week for item in DISJOINT_DATETIME_RANGE], []),
    ("__week__range", [item.isocalendar().week for item in DISJOINT_DATETIME_RANGE], []),
    ("__iso_week_day", GREATER_DATETIME.isoweekday(), []),
    ("__iso_week_day__gte", GREATER_DATETIME.isoweekday(), []),
    ("__iso_week_day__lte", LESSER_DATETIME.isoweekday(), []),
    ("__iso_week_day__gt", GREATER_DATETIME.isoweekday(), []),
    ("__iso_week_day__lt", LESSER_DATETIME.isoweekday(), []),
    ("__iso_week_day__in", [item.isoweekday() for item in DISJOINT_DATETIME_RANGE], []),
    ("__iso_week_day__range", [item.isoweekday() for item in DISJOINT_DATETIME_RANGE], []),
    ("__day", GREATER_DATETIME.day, []),
    ("__day__gte", GREATER_DATETIME.day, []),
    ("__day__lte", LESSER_DATETIME.day, []),
    ("__day__gt", GREATER_DATETIME.day, []),
    ("__day__lt", LESSER_DATETIME.day, []),
    ("__day__in", [item.day for item in DISJOINT_DATETIME_RANGE], []),
    ("__day__range", [item.day for item in DISJOINT_DATETIME_RANGE], []),
    ("__hour", GREATER_DATETIME.hour, []),
    ("__hour__gte", GREATER_DATETIME.hour, []),
    ("__hour__lte", LESSER_DATETIME.hour, []),
    ("__hour__gt", GREATER_DATETIME.hour, []),
    ("__hour__lt", LESSER_DATETIME.hour, []),
    ("__hour__in", [item.hour for item in DISJOINT_DATETIME_RANGE], []),
    ("__hour__range", [item.hour for item in DISJOINT_DATETIME_RANGE], []),
    ("__minute", GREATER_DATETIME.minute, []),
    ("__minute__gte", GREATER_DATETIME.minute, []),
    ("__minute__lte", LESSER_DATETIME.minute, []),
    ("__minute__gt", GREATER_DATETIME.minute, []),
    ("__minute__lt", LESSER_DATETIME.minute, []),
    ("__minute__in", [item.minute for item in DISJOINT_DATETIME_RANGE], []),
    ("__minute__range", [item.minute for item in DISJOINT_DATETIME_RANGE], []),
    ("__second", GREATER_DATETIME.second, []),
    ("__second__gte", GREATER_DATETIME.second, []),
    ("__second__lte", LESSER_DATETIME.second, []),
    ("__second__gt", GREATER_DATETIME.second, []),
    ("__second__lt", LESSER_DATETIME.second, []),
    ("__second__in", [item.second for item in DISJOINT_DATETIME_RANGE], []),
    ("__second__range", [item.second for item in DISJOINT_DATETIME_RANGE], [])
]


@pytest.fixture(name='account_queryset')
def fixture_account_queryset():
    for number in range(0,len(TEXT_TEST_ITEMS)):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                AccountModel,
                mail_address=TEXT_TEST_ITEMS[number],
                mail_host=TEXT_TEST_ITEMS[number],
                mail_host_port=INT_TEST_ITEMS[number],
                timeout=FLOAT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                is_healthy=BOOL_TEST_ITEMS[number]
            )

    return AccountModel.objects.all()


@pytest.fixture(name='mailbox_queryset')
def fixture_mailbox_queryset(account_queryset):
    for number in range(0,len(TEXT_TEST_ITEMS)):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                MailboxModel,
                name=TEXT_TEST_ITEMS[number],
                save_toEML=BOOL_TEST_ITEMS[number],
                save_attachments=BOOL_TEST_ITEMS[number],
                save_images=BOOL_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                is_healthy=BOOL_TEST_ITEMS[number],
                account=account_queryset.get(id=number+1)
            )

    return MailboxModel.objects.all()


@pytest.fixture(name='daemon_queryset')
def fixture_daemon_queryset(mailbox_queryset):
    for number in range(0,len(INT_TEST_ITEMS)):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                DaemonModel,
                cycle_interval=INT_TEST_ITEMS[number],
                is_running=BOOL_TEST_ITEMS[number],
                is_healthy=BOOL_TEST_ITEMS[number],
                mailbox=mailbox_queryset.get(id=number+1),
                log_filepath=Faker().file_path()
            )

    return DaemonModel.objects.all()


@pytest.fixture(name='correspondent_queryset')
def fixture_correspondent_queryset():
    for number in range(0,len(TEXT_TEST_ITEMS)):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                CorrespondentModel,
                email_name=TEXT_TEST_ITEMS[number],
                email_address=TEXT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number]
            )

    return CorrespondentModel.objects.all()


@pytest.fixture(name='mailinglist_queryset')
def fixture_mailinglist_queryset(correspondent_queryset):
    for number in range(0,len(TEXT_TEST_ITEMS)):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                MailingListModel,
                list_id=TEXT_TEST_ITEMS[number],
                list_owner=TEXT_TEST_ITEMS[number],
                list_subscribe=TEXT_TEST_ITEMS[number],
                list_unsubscribe=TEXT_TEST_ITEMS[number],
                list_post=TEXT_TEST_ITEMS[number],
                list_help=TEXT_TEST_ITEMS[number],
                list_archive=TEXT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                correspondent=correspondent_queryset.get(id=number+1)
            )

    return MailingListModel.objects.all()


@pytest.fixture(name='email_queryset')
def fixture_email_queryset(account_queryset, correspondent_queryset, mailinglist_queryset):
    for number in range(0,len(TEXT_TEST_ITEMS)):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            new_email = baker.make(
                EMailModel,
                message_id=TEXT_TEST_ITEMS[number],
                datetime=datetime.datetime.now(tz=datetime.UTC),
                email_subject=TEXT_TEST_ITEMS[number],
                bodytext=TEXT_TEST_ITEMS[number],
                datasize=INT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                account=account_queryset.get(id=number+1),
                mailinglist=mailinglist_queryset.get(id=number+1),
                comments = TEXT_TEST_ITEMS[number],
                keywords = TEXT_TEST_ITEMS[number],
                importance = TEXT_TEST_ITEMS[number],
                priority = TEXT_TEST_ITEMS[number],
                precedence = TEXT_TEST_ITEMS[number],
                received = TEXT_TEST_ITEMS[number],
                user_agent = TEXT_TEST_ITEMS[number],
                auto_submitted = TEXT_TEST_ITEMS[number],
                content_type = TEXT_TEST_ITEMS[number],
                content_language = TEXT_TEST_ITEMS[number],
                content_location = TEXT_TEST_ITEMS[number],
                x_priority = TEXT_TEST_ITEMS[number],
                x_originated_client = TEXT_TEST_ITEMS[number],
                x_spam = TEXT_TEST_ITEMS[number]
            )
            baker.make(EMailCorrespondentsModel, email=new_email, correspondent=correspondent_queryset.get(id=number+1))

    return EMailModel.objects.all()


@pytest.fixture(name='attachment_queryset')
def fixture_attachment_queryset(email_queryset):
    for number in range(0,len(TEXT_TEST_ITEMS)):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                AttachmentModel,
                file_path='/path/' + TEXT_TEST_ITEMS[number],
                file_name=TEXT_TEST_ITEMS[number],
                datasize=INT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                email=email_queryset.get(id=number+1)
            )

    return AttachmentModel.objects.all()


@pytest.fixture(name='image_queryset')
def fixture_image_queryset(email_queryset):
    for number in range(0,len(TEXT_TEST_ITEMS)):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                ImageModel,
                file_path='/path/' + TEXT_TEST_ITEMS[number],
                file_name=TEXT_TEST_ITEMS[number],
                datasize=INT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                email=email_queryset.get(id=number+1)
            )

    return ImageModel.objects.all()
