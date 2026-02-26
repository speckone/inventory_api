import threading
from flask import current_app, render_template
from flask_mail import Message
from inventory_api_app.extensions import mail


class EmailService:
    @staticmethod
    def send_async(app, msg):
        """Send email in background thread with app context."""
        with app.app_context():
            try:
                mail.send(msg)
            except Exception:
                app.logger.exception("Failed to send email: subject=%s", msg.subject)

    @classmethod
    def send_order_email(cls, order):
        """Compose and send order submission email."""
        config = current_app.config
        to_email = config.get("MAIL_ORDER_RECIPIENT")
        if not to_email:
            current_app.logger.warning("MAIL_ORDER_RECIPIENT not configured, skipping email")
            return

        # Build order details grouped by vendor
        vendor = None
        order_lines = []
        for order_item in sorted(order.order_items, key=lambda o: o.product.vendor_id):
            if vendor != order_item.product.vendor:
                vendor = order_item.product.vendor
                order_lines.append({"vendor": str(vendor), "products": []})
            inventory = order_item.product.inventory_item[0]
            order_lines[-1]["products"].append({
                "quantity": order_item.quantity,
                "unit": order_item.product.unit.name,
                "product": order_item.product.name,
                "current_qty": inventory.quantity,
            })

        html = render_template(
            "emails/order_submitted.html",
            order_lines=order_lines,
            total_cost=f"{order.cost:.2f}",
        )

        msg = Message(
            subject="New Inventory Order",
            recipients=[to_email],
            html=html,
        )

        app = current_app._get_current_object()
        thread = threading.Thread(target=cls.send_async, args=(app, msg))
        thread.start()
