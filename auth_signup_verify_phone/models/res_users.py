# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _signup_create_user(self, values):
        if self.env.context.get("auth_signup_phone"):
            login = values.get("login")
            if login:
                partner = self.env["res.partner"].search([("mobile", "=", login)])
                if len(partner) == 1:
                    values["partner_id"] = partner.id
                elif len(partner) > 1:
                    _logger.info(
                        "Multiple partners found for mobile %s, signup aborted",
                        login,
                    )
                    return False
        return super()._signup_create_user(values)

    @api.model
    def _format_mobile_number(self, mobile):
        mobile = mobile.strip().replace(" ", "")
        if mobile.startswith("+"):
            mobile = mobile[1:]
        return mobile

    def _get_channel_values(self, gateway):
        mobile = self._format_mobile_number(self.mobile)
        return {
            "metadata": {"phone_number_id": gateway.whatsapp_from_phone},
            "contacts": [{"profile": {"name": self.name}, "wa_id": mobile}],
            "messages": [{"from": gateway.whatsapp_from_phone, "to": mobile}],
        }

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get("auth_signup_phone"):
            for vals in vals_list:
                vals.pop("email", None)
        return super().create(vals_list)

    def action_reset_password(self):
        if self.env.context.get("auth_signup_phone"):
            self.mapped("partner_id").signup_prepare(signup_type="reset")
            lang = self.env.context.get("web_lang", self.env.lang)
            bot_data = (
                self.env["mail.gateway"]
                .with_context(lang=lang)
                ._get_default_registration_gateway()
            )
            dispatcher = self.env["mail.gateway.whatsapp"].with_user(
                bot_data["webhook_user_id"]
            )
            gateway = dispatcher.env["mail.gateway"].browse(bot_data["id"])
            if not gateway:
                raise ValidationError(
                    _("No WhatsApp gateway configured for verification.")
                )
            if not self.mobile:
                raise ValidationError(_("Phone number is required for verification."))
            chat = dispatcher._get_channel(
                gateway,
                self._format_mobile_number(self.mobile),
                self._get_channel_values(gateway),
                force_create=True,
            )
            lang = self.env["res.lang"].search([("code", "=", lang)])
            template_id = bot_data["default_template_by_lang"].get(
                lang.iso_code
            ) or bot_data["default_template_by_lang"].get(lang.code)
            if not template_id:
                raise ValidationError(
                    _("WhatsApp template not found for the language %s.") % lang.name
                )
            whatsapp_template = (
                self.env["mail.whatsapp.template"].browse(template_id).exists()
            )
            body = {}
            for variable in whatsapp_template.variable_ids.filtered(
                lambda x: x.section == "body"
            ):
                if not variable.signup_field_id:
                    raise ValidationError(
                        _("The whatsapp template doesn't have a signup field for %s.")
                        % variable.name
                    )
                body[variable.name] = self[variable.signup_field_id.name]
            variables_values = {"body": body}
            body = whatsapp_template.with_context(
                variables_values=variables_values
            ).get_body()
            return chat.with_context(
                whatsapp_template_id=template_id, variables_values=variables_values
            ).message_post(
                body=body,
                author_id=False,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
                date=fields.Datetime.now(),
                raise_exception=True,
            )
        return super().action_reset_password()
