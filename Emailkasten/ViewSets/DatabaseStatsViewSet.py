from rest_framework import viewsets
from rest_framework.response import Response
from ..Models.EMailModel import EMailModel
from ..Models.CorrespondentModel import CorrespondentModel
from ..Models.AttachmentModel import AttachmentModel
from ..Models.AccountModel import AccountModel

class DatabaseStatsViewSet(viewsets.ViewSet):
    def list(self, request):
        email_count = EMailModel.objects.filter(account__user = request.user).count()
        correspondent_count = CorrespondentModel.filter(correspondentemails__email__account__user = request.user).objects.count()
        attachment_count = AttachmentModel.objects.filter(email__account__user = request.user).count()
        account_count = AccountModel.objects.filter(account__user = request.user).count()

        data = {
            'email_count': email_count,
            'correspondent_count': correspondent_count,
            'attachment_count': attachment_count,
            'account_count': account_count,
        }
        return Response(data)