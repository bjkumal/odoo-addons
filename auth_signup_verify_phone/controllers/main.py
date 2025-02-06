# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

import phonenumbers
from phonenumbers import NumberParseException

from odoo import _
from odoo.http import request

from odoo.addons.auth_signup_verify_email.controllers.main import SignupVerifyEmail

_logger = logging.getLogger(__name__)


class SignupVerifyPhone(SignupVerifyEmail):
    def passwordless_signup(self):
        values = request.params
        qcontext = self.get_auth_signup_qcontext()

        try:
            phone_number = phonenumbers.parse(values.get("login", ""))
            if not phonenumbers.is_valid_number(phone_number):
                qcontext["error"] = _("That does not seem to be a valid phone number.")
                return request.render("auth_signup.signup", qcontext)
            mobile = phonenumbers.format_number(
                phone_number, phonenumbers.PhoneNumberFormat.E164
            )
        except NumberParseException as error:
            if error.error_type == NumberParseException.NOT_A_NUMBER:
                return super().passwordless_signup()
            qcontext["error"] = _(
                "Invalid phone number format. Please use the format:<br/>"
                "+[Country Code][Number]<br/>"
                "Example: +34612345758"
            )
            return request.render("auth_signup.signup", qcontext)
        except Exception as error:
            qcontext["error"] = str(error)
            return request.render("auth_signup.signup", qcontext)
        if not values.get("mobile"):
            values["mobile"] = mobile

        # remove values that could raise "Invalid field '*' on model 'res.users'"
        values.pop("redirect", "")
        values.pop("token", "")

        # Remove password
        values["password"] = ""
        sudo_users = (
            request.env["res.users"]
            .with_context(create_user=True, auth_signup_phone=True)
            .sudo()
        )

        try:
            with request.cr.savepoint():
                sudo_users.signup(values, qcontext.get("token"))
                sudo_users.with_context(
                    web_lang=request.params.get("lang")
                ).reset_password(values.get("login"))
        except Exception as error:
            _logger.exception(error)
            if (
                request.env["res.users"]
                .sudo()
                .search([("login", "=", qcontext.get("login"))])
            ):
                qcontext["error"] = _(
                    "Another user is already registered using this phone number."
                )
            else:
                # Agnostic message for security
                qcontext["error"] = _(
                    "Something went wrong, please try again later or" " contact us."
                )
            return request.render("auth_signup.signup", qcontext)

        qcontext["message"] = _("Check your phone to activate your account!")
        return request.render("auth_signup.reset_password", qcontext)
