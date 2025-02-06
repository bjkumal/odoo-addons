# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Verify phone at signup",
    "summary": "Force uninvited users to use a good phone for signup.",
    "version": "16.0.1.0.0",
    "category": "Authentication",
    "website": "https://github.com/nuobit/odoo-addons",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "external_dependencies": {"python": ["phonenumbers"]},
    "depends": [
        "auth_signup_phone",
        "auth_signup_verify_email",
        "mail_gateway_whatsapp",
    ],
    "data": [
        "views/signup.xml",
        "views/auth_signup_login_templates.xml",
        "views/mail_whatsapp_template_variable_views.xml",
        "views/mail_whatsapp_template_views.xml",
        "views/mail_gateway_views.xml",
    ],
}
