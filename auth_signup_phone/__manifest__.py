# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Auth Signup phone",
    "summary": "This module allows a user to enter their phone number as a login.",
    "version": "16.0.1.0.0",
    "category": "Authentication",
    "website": "https://github.com/nuobit/odoo-addons",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "depends": ["auth_signup"],
    "data": [
        "views/portal_templates.xml",
        "views/signup_templates.xml",
        "views/webclient_templates.xml",
        "views/signup.xml",
    ],
}
