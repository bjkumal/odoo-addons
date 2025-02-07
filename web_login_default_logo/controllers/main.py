# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


import logging

from odoo import http
from odoo.tools.misc import file_path

_logger = logging.getLogger(__name__)


class Binary(http.Controller):
    @http.route(
        [
            "/nologo.png",
        ],
        type="http",
        auth="none",
        cors="*",
    )
    def no_logo(self, dbname=None, **kw):
        return http.Stream(file_path("web/static/img/nologo.png"))
