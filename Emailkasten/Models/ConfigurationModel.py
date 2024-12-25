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

"""Module with the :class:`ConfigurationModel` model class."""

from django.db import models


class ConfigurationModel(models.Model):
    """Database model for the configuration of the Emailkasten instance."""

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
    value_char = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    def __str__(self):
        return f"Setting {self.category}.{self.key}"

    class Meta:
        """Metadata class for the model."""

        db_table = "config"
        """The name of the database table for the configuations."""

        unique_together = ('category', 'key')
        """:attr:`category` and :attr:`key` in combination are unique."""


    def get_value(self):
        """Get the value for a configuration."""
        if self.value_bool is not None:
            return self.value_bool
        elif self.value_int is not None:
            return self.value_int
        elif self.value_char is not None:
            return self.value_char
        return None
