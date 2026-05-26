def register_blueprints(app):
    from routes.auth import bp as auth_bp
    from routes.products import bp as products_bp
    from routes.suppliers import bp as suppliers_bp
    from routes.purchases import bp as purchases_bp
    from routes.warehouses import bp as warehouses_bp
    from routes.sales import bp as sales_bp
    from routes.members import bp as members_bp
    from routes.employees import bp as employees_bp
    from routes.finance import bp as finance_bp
    from routes.system import bp as system_bp
    from routes.dashboard import bp as dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(warehouses_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(dashboard_bp)
