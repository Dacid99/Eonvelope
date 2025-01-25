# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Module with the :class:`SimpleEMailSerializer` serializer class."""

from rest_framework import serializers

from core.models.EMailModel import EMailModel


class BaseEMailSerializer(serializers.ModelSerializer):
    """The base serializer for :class:`core.models.EMailModel.EMailModel`.
    Includes all viable fields from the model.
    Sets all constraints that must be implemented in all serializers.
    Other serializers for :class:`core.models.EMailModel.EMailModel` should inherit from this.
    """

    class Meta:
        """Metadata class for the base serializer.
        Contains constraints that must be implemented by all serializers.
        Other serializer metaclasses should inherit from this.
        The read_only_fields must not be shortened in subclasses.
        """

        model = EMailModel
        """The model to serialize."""

        exclude = ['eml_filepath', 'prerender_filepath']
        """Exclude the :attr:`core.models.EMailModel.EMailModel.eml_filepath`
        and :attr:`core.models.EMailModel.EMailModel.prerender_filepath` fields.
        """

        read_only_fields = [
            'message_id',
            'datetime',
            'email_subject',
            'bodytext',
            'inReplyTo',
            'datasize',
            'correspondents',
            'mailinglist',
            'account',
            'comments',
            'keywords',
            'importance',
            'priority',
            'precedence',
            'received',
            'user_agent',
            'auto_submitted',
            'content_type',
            'content_language',
            'content_location',
            'x_priority',
            'x_originated_client',
            'x_spam',
            'created',
            'updated'
        ]
        """All fields except for :attr:`core.models.EMailModel.EMailModel.is_favorite`
        are read-only.
        """
