import logging

import odoo
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.utils import ensure_db
from odoo.addons.web.controllers.home import CREDENTIAL_PARAMS, Home

_logger = logging.getLogger(__name__)


ROLE_GROUPS = {
    "Fleet Manager": "transit_ops.group_transit_fleet_manager",
    "Dispatcher": "transit_ops.group_transit_dispatcher",
    "Safety Officer": "transit_ops.group_transit_safety_officer",
    "Financial Analyst": "transit_ops.group_transit_financial_analyst",
}

DEMO_ACCOUNTS = [
    {
        "role": "Dispatcher",
        "name": "Raven Kumar",
        "login": "dispatcher@transitops.local",
        "password": "transitops123",
    },
    {
        "role": "Fleet Manager",
        "name": "Meera Fleet",
        "login": "fleet.manager@transitops.local",
        "password": "transitops123",
    },
    {
        "role": "Safety Officer",
        "name": "Ayaan Safety",
        "login": "safety.officer@transitops.local",
        "password": "transitops123",
    },
    {
        "role": "Financial Analyst",
        "name": "Nisha Finance",
        "login": "finance.analyst@transitops.local",
        "password": "transitops123",
    },
]


class TransitOpsHome(Home):
    @http.route("/", type="http", auth="none")
    def index(self, s_action=None, db=None, **kw):
        return request.redirect("/transitops/login?db=transitops", 303)


class TransitOpsAuth(http.Controller):
    def _dashboard_path(self):
        try:
            action = request.env.ref("transit_ops.action_transit_dashboard")
            return "/odoo/action-%s" % action.id
        except Exception:
            return "/odoo"

    def _role_group(self, role):
        role = role if role in ROLE_GROUPS else "Dispatcher"
        return request.env.ref(ROLE_GROUPS[role], raise_if_not_found=False)

    def _role_values(self, role):
        base_group = request.env.ref("base.group_user", raise_if_not_found=False)
        role_group = self._role_group(role)
        group_ids = [group.id for group in (base_group, role_group) if group]
        return role, group_ids

    def _ensure_demo_accounts(self):
        Users = request.env["res.users"].sudo()
        for account in DEMO_ACCOUNTS:
            role, group_ids = self._role_values(account["role"])
            user = Users.search([("login", "=", account["login"])], limit=1)
            values = {
                "name": account["name"],
                "login": account["login"],
                "email": account["login"],
                "group_ids": [(6, 0, group_ids)],
            }
            if user:
                user.write(values)
                continue
            values["password"] = account["password"]
            Users.with_context(no_reset_password=True).create(values)

    def _create_role_user(self, name, login, password, role):
        login = (login or "").strip().lower()
        name = (name or "").strip() or login.split("@")[0].replace(".", " ").title()
        if not login or not password:
            raise ValueError("Email and password are required to create an account.")
        if "@" not in login:
            raise ValueError("Enter a valid email address.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")

        Users = request.env["res.users"].sudo()
        existing = Users.search([("login", "=", login)], limit=1)
        if existing:
            raise ValueError("An account already exists for this email. Use Sign In instead.")

        role, group_ids = self._role_values(role)
        return Users.with_context(no_reset_password=True).create({
            "name": name,
            "login": login,
            "email": login,
            "password": password,
            "group_ids": [(6, 0, group_ids)],
        })

    def _render_login(self, error=None, success=None, login=None, role="Dispatcher", name=None, mode="login"):
        self._ensure_demo_accounts()
        values = {
            "error": error,
            "success": success,
            "login": login or "dispatcher@transitops.local",
            "name": name or "",
            "role": role or "Dispatcher",
            "mode": mode or "login",
            "demo_accounts": DEMO_ACCOUNTS,
            "csrf_token": request.csrf_token(),
        }
        response = request.render("transit_ops.login_page", values)
        response.headers["Cache-Control"] = "no-cache"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response

    def _apply_selected_role(self, role):
        selected_group = self._role_group(role)
        all_groups = [
            request.env.ref(xmlid, raise_if_not_found=False)
            for xmlid in ROLE_GROUPS.values()
        ]
        all_groups = [group for group in all_groups if group]
        if not selected_group:
            return

        commands = [(3, group.id) for group in all_groups]
        commands.append((4, selected_group.id))
        request.env.user.sudo().write({"group_ids": commands})
        request.env.invalidate_all()

    @http.route(["/transitops/login", "/web/login"], type="http", auth="none", methods=["GET", "POST"], readonly=False, csrf=False)
    def transitops_login(self, redirect=None, **kw):
        ensure_db(db=kw.get("db") or "transitops")

        if request.env.uid is None:
            if request.session.uid is None:
                request.env["ir.http"]._auth_method_public()
            else:
                request.update_env(user=request.session.uid)

        login = kw.get("login") or kw.get("email") or ""
        name = kw.get("name") or ""
        role = kw.get("role") or "Dispatcher"
        mode = kw.get("mode") or "login"

        if request.httprequest.method == "POST":
            if mode == "signup":
                try:
                    self._create_role_user(name, login, kw.get("password"), role)
                    success = "Account created. Sign in with the same email and password."
                    return self._render_login(success=success, login=login, role=role, name=name, mode="login")
                except ValueError as exc:
                    return self._render_login(error=str(exc), login=login, role=role, name=name, mode="signup")

            try:
                credential = {key: value for key, value in request.params.items() if key in CREDENTIAL_PARAMS and value}
                if login and "login" not in credential:
                    credential["login"] = login
                credential.setdefault("type", "password")
                auth_info = request.session.authenticate(request.env, credential)
                request.params["login_success"] = True
                request.update_env(user=auth_info["uid"])
                self._apply_selected_role(role)
                request.update_env(user=auth_info["uid"])
                return request.redirect(redirect or self._dashboard_path(), 303)
            except odoo.exceptions.AccessDenied as exc:
                error = "Invalid credentials. Use the demo password or create a new account."
                if exc.args != odoo.exceptions.AccessDenied().args and exc.args:
                    error = exc.args[0]
                return self._render_login(error=error, login=login, role=role, name=name, mode="login")

        return self._render_login(login=login, role=role, name=name, mode=mode)
