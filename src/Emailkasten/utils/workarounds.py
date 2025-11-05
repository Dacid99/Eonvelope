# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""Module with utility for the :mod:`Emailkasten` project ."""

from __future__ import annotations

import logging
from typing import Any

from constance import config

from Emailkasten.settings import CONSTANCE_CONFIG


logger = logging.getLogger(__name__)


def get_config(setting: str) -> Any:  # noqa: ANN401 ; can truly return anything
    """A dirty workaround to enable constance to do the initial migration.

    Initial migrations fail otherwise because the models depend on constance that is not initialized yet.

    References:
        https://github.com/jazzband/django-constance/issues/229

    Args:
        setting: The config value to retrieve

    Returns:
        The requested setting value.

    Raises:
        KeyError: Raised from any exception that is related to a settings value not existing.
    """
    try:
        return getattr(config, setting)
    except Exception as exc:
        logger.debug(
            "Failed to retrieve a constance config value, using workaround ..."
        )
        try:
            return CONSTANCE_CONFIG[setting][0]
        except KeyError as keyexc:
            logger.critical(
                "A config value was not found, reraising from original exception!",
                exc_info=True,
            )
            raise keyexc from exc
