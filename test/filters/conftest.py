INT_TEST_ITEMS = [
    0,
    1,
    2
]

INT_TEST_PARAMETERS = [
    ("__lte", INT_TEST_ITEMS[0], 1),
    ("__gte", INT_TEST_ITEMS[2], 1),
    ("__lt", INT_TEST_ITEMS[1], 1),
    ("__gt", INT_TEST_ITEMS[1], 1),
    ("", INT_TEST_ITEMS[0], 1),
    ("__in", INT_TEST_ITEMS[0:1], 1),
    ("__range", INT_TEST_ITEMS[0:1]*2, 1),

    ("__lte", INT_TEST_ITEMS[1], 2),
    ("__gte", INT_TEST_ITEMS[1], 2),
    ("__lt", INT_TEST_ITEMS[2], 2),
    ("__gt", INT_TEST_ITEMS[0], 2),
    ("", INT_TEST_ITEMS[1], 1),
    ("__in", INT_TEST_ITEMS[0:2], 2),
    ("__range", INT_TEST_ITEMS[0:2], 2),

    ("__lte", -5, 0),
    ("__gte", 5, 0),
    ("__lt", -5, 0),
    ("__gt", 5, 0),
    ("", 5, 0),
    ("__in", [-2,3] , 0),
    ("__range", [-10,-7], 0)
]

FLOAT_TEST_ITEMS = [
    0.5,
    1,
    2.3
]

FLOAT_TEST_PARAMETERS = [
    ("__lte", FLOAT_TEST_ITEMS[0], 1),
    ("__gte", FLOAT_TEST_ITEMS[2], 1),
    ("__lt", FLOAT_TEST_ITEMS[1], 1),
    ("__gt", FLOAT_TEST_ITEMS[1], 1),
    ("", FLOAT_TEST_ITEMS[0], 1),
    ("__in", FLOAT_TEST_ITEMS[0:1], 1),
    ("__range", FLOAT_TEST_ITEMS[0:1]*2, 2),

    ("__lte", FLOAT_TEST_ITEMS[1], 2),
    ("__gte", FLOAT_TEST_ITEMS[1], 2),
    ("__lt", FLOAT_TEST_ITEMS[2], 2),
    ("__gt", FLOAT_TEST_ITEMS[0], 2),
    ("", FLOAT_TEST_ITEMS[1], 1),
    ("__in", FLOAT_TEST_ITEMS[0:2], 2),
    ("__range", FLOAT_TEST_ITEMS[0:2], 2),

    ("__lte", -5.1, 0),
    ("__gte", 5.1, 0),
    ("__lt", -5.1, 0),
    ("__gt", 5.1, 0),
    ("", 5.1, 0),
    ("__in", [-2, 3.6] , 0),
    ("__range", [-10,-7.3], 2),
]

BOOL_TEST_ITEMS = [
    True,
    False,
    False
]

BOOL_TEST_PARAMETERS = [
    ("", BOOL_TEST_ITEMS[0], 1),
    ("", BOOL_TEST_ITEMS[1], 2)
]

TEXT_TEST_ITEMS = [
        'A1bCD',
        'ZyX9W',
        'ZyX8W'
    ]

TEXT_TEST_PARAMETERS = [
        ("__icontains", TEXT_TEST_ITEMS[0][2:4].lower(), 1),
        ("__contains", TEXT_TEST_ITEMS[0][2:4], 1),
        ("", TEXT_TEST_ITEMS[0], 1),
        ("__iexact", TEXT_TEST_ITEMS[0].lower(), 1),
        ("__startswith", TEXT_TEST_ITEMS[0][0], 1),
        ("__istartswith", TEXT_TEST_ITEMS[0][0].lower(), 1),
        ("__endswith", TEXT_TEST_ITEMS[0][-1], 1),
        ("__iendswith", TEXT_TEST_ITEMS[0][-1].lower(), 1),
        ("__regex", r'\w\d\w{3}', 1),
        ("__iregex", r'\w\d\w{3}', 1),
        ("__in", [TEXT_TEST_ITEMS[0]], 1),

        ("__icontains", TEXT_TEST_ITEMS[1][1:3].lower(), 2),
        ("__contains", TEXT_TEST_ITEMS[1][1:3], 2),
        ("", TEXT_TEST_ITEMS[1], 1),
        ("__iexact", TEXT_TEST_ITEMS[1].lower(), 1),
        ("__startswith", TEXT_TEST_ITEMS[1][0], 2),
        ("__istartswith", TEXT_TEST_ITEMS[1][0].lower(), 2),
        ("__endswith", TEXT_TEST_ITEMS[1][-1], 2),
        ("__iendswith", TEXT_TEST_ITEMS[1][-1].lower(), 2),
        ("__regex", r'\w{3}\d\w', 2),
        ("__iregex", r'\w{3}\d\w', 2),
        ("__in", TEXT_TEST_ITEMS[1:3], 2),

        ("__icontains", 'op', 0),
        ("__contains", 'oP', 0),
        ("", 'No5PQ', 0),
        ("__iexact", 'no5pq', 0),
        ("__startswith", 'N', 0),
        ("__istartswith", 'n', 0),
        ("__endswith", 'Q', 0),
        ("__iendswith", 'q', 0),
        ("__regex", r'\w{2}\d\w{2}', 0),
        ("__iregex", r'\w{2}\d\w{2}', 0),
        ("__in", ['No5PQ'], 0)
    ]
