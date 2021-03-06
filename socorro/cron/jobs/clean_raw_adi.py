# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from configman import Namespace
from crontabber.base import BaseCronApp
from crontabber.mixins import (
    with_postgres_transactions,
    with_single_postgres_transaction,
)


SIX_MONTHS = 180


@with_postgres_transactions()
@with_single_postgres_transaction()
class CleanRawADICronApp(BaseCronApp):
    """Deletes old data from raw_adi and raw_adi_logs

    See https://bugzilla.mozilla.org/show_bug.cgi?id=1227131

    """

    app_name = 'clean-raw-adi'
    app_description = 'Delete old data from raw_adi and raw_adi_logs'

    required_config = Namespace()
    required_config.add_option(
        'days_to_keep',
        default=SIX_MONTHS,
        doc='Number of days of raw adi to keep in Postgres')

    def run(self, connection):
        cursor = connection.cursor()
        # Casting to date because stored procs in psql are strongly typed.
        assert self.config.days_to_keep > 0

        # Clean raw_adi
        cursor.execute(
            """
            DELETE FROM raw_adi
            WHERE date < NOW() - INTERVAL '{} days'
            """.format(self.config.days_to_keep)
        )

        # Clean raw_adi_logs
        cursor.execute(
            """
            DELETE FROM raw_adi_logs
            WHERE report_date < NOW() - INTERVAL '{} days'
            """.format(self.config.days_to_keep)
        )
