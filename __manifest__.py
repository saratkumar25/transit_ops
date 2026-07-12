{
    "name": "TransitOps",
    "version": "19.0.1.0.0",
    "category": "Transportation",
    "summary": "Transit fleet management, dispatch, maintenance, and operational dashboard",
    "description": """
TransitOps — Transit Fleet Management
======================================

Digitizes the transport workflow:
- Vehicle and driver registration
- Trip creation, dispatch, completion, and cancellation
- Maintenance start/close automation
- Fuel and expense tracking
- Custom Owl dashboard with live KPIs, filters, and recent trips
- Four RBAC roles: Fleet Manager, Dispatcher, Safety Officer, Financial Analyst
    """,
    "author": "TransitOps Team",
    "website": "",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        # 1. Security — must load before any views
        "security/security.xml",
        "security/ir.model.access.csv",
        # 2. Data — sequences
        "data/sequence.xml",
        # 3. Member 1 core views
        "views/vehicle_views.xml",
        "views/driver_views.xml",
        "views/trip_views.xml",
        # 4. Member 3 operational views
        "views/maintenance_views.xml",
        "views/fuel_log_views.xml",
        "views/expense_views.xml",
        # 5. Dashboard client action and analytics
        "views/dashboard_action.xml",
        # 6. Menu views — must be last (references all actions)
        "views/menu_views.xml",
    ],
    "demo": [
        "data/demo_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "transit_ops/static/src/components/dashboard/dashboard.js",
            "transit_ops/static/src/components/dashboard/dashboard.xml",
            "transit_ops/static/src/components/dashboard/dashboard.scss",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
