import asyncio
import logging
import threading
from datetime import datetime, date

from sqlalchemy import func

logger = logging.getLogger(__name__)


class TelegramService:
    """Telegram bot service using long polling.

    The bot runs in a background daemon thread making outbound-only connections
    to api.telegram.org. No inbound webhook is needed, so it works behind a
    firewall.
    """

    _thread = None

    @staticmethod
    def get_bot_token(app):
        """Get bot token from AppSettings."""
        with app.app_context():
            from inventory_api_app.extensions import db
            from inventory_api_app.models.settings import AppSetting
            setting = db.session.get(AppSetting, 'telegram_bot_token')
            return setting.value if setting and setting.value else None

    @staticmethod
    def get_allowed_users(app):
        """Get list of allowed Telegram user IDs from AppSettings."""
        with app.app_context():
            from inventory_api_app.extensions import db
            from inventory_api_app.models.settings import AppSetting
            setting = db.session.get(AppSetting, 'telegram_allowed_users')
            if not setting or not setting.value:
                return []
            return [int(uid.strip()) for uid in setting.value.split(',') if uid.strip().isdigit()]

    @staticmethod
    def parse_shorthand(text):
        """Parse shorthand message: CUSTOMER_CODE TEMPLATE_CODE QUANTITY

        First token = customer code, last token = quantity,
        everything in between = template code (supports multi-word codes).
        Returns (customer_code, template_code, quantity) or raises ValueError.
        """
        parts = text.strip().split()
        if len(parts) < 3:
            raise ValueError("Format: CUSTOMER_CODE TEMPLATE_CODE QUANTITY")
        quantity_str = parts[-1]
        try:
            quantity = float(quantity_str)
        except ValueError:
            raise ValueError(f"Invalid quantity: {quantity_str}")
        customer_code = parts[0]
        template_code = ' '.join(parts[1:-1])
        return customer_code, template_code, quantity

    @staticmethod
    def process_shorthand(customer_code, template_code, quantity):
        """Look up customer and template, find/create invoice, add item.

        Must be called inside a Flask app context.
        Returns a dict with result info or raises ValueError.
        """
        from inventory_api_app.extensions import db
        from inventory_api_app.models.invoice import (
            Customer, InvoiceItemTemplate, Invoice, InvoiceItem,
        )

        customer = Customer.query.filter(
            func.lower(Customer.short_code) == customer_code.lower()
        ).first()
        if not customer:
            raise ValueError(f"Customer not found for code: {customer_code}")

        template = InvoiceItemTemplate.query.filter(
            func.lower(InvoiceItemTemplate.short_code) == template_code.lower()
        ).first()
        if not template:
            raise ValueError(f"Template not found for code: {template_code}")

        if not template.price_per_unit:
            raise ValueError(f"Template '{template.name}' has no price set")

        invoice = Invoice.query.filter_by(
            customer_id=customer.id,
            paid=False,
            sent=False,
        ).first()

        created_new = False
        if not invoice:
            max_num = db.session.query(func.max(Invoice.invoice_number)).scalar() or 0
            invoice = Invoice.create(
                invoice_number=max_num + 1,
                customer_id=customer.id,
                date=datetime.now(),
                paid=False,
                sent=False,
            )
            created_new = True

        InvoiceItem.create(
            invoice_id=invoice.id,
            description=template.name,
            price_per_unit=template.price_per_unit,
            quantity=quantity,
            date_of_service=date.today(),
        )

        return {
            "customer_name": customer.name,
            "invoice_number": invoice.invoice_number,
            "created_new": created_new,
            "item_description": template.name,
            "quantity": quantity,
            "price_per_unit": template.price_per_unit,
            "line_total": template.price_per_unit * quantity,
            "invoice_total": invoice.subtotal,
        }

    @classmethod
    def start_polling(cls, app):
        """Start the Telegram bot in a background daemon thread.

        Checks for a bot token in AppSettings. If not configured, logs a
        warning and returns without starting.
        """
        token = cls.get_bot_token(app)
        if not token:
            logger.info("Telegram bot token not configured, skipping bot startup")
            return

        if cls._thread and cls._thread.is_alive():
            logger.warning("Telegram bot is already running")
            return

        def run_bot():
            try:
                asyncio.run(cls._run_polling(app, token))
            except Exception:
                logger.exception("Telegram bot polling crashed")

        cls._thread = threading.Thread(target=run_bot, daemon=True)
        cls._thread.start()
        logger.info("Telegram bot polling started")

    @classmethod
    async def _run_polling(cls, app, token):
        """Async entry point - builds the Application and starts polling."""
        from telegram.ext import Application, CommandHandler, MessageHandler, filters

        application = Application.builder().token(token).build()
        application.bot_data["flask_app"] = app

        application.add_handler(CommandHandler("start", cls._handle_start))
        application.add_handler(CommandHandler("help", cls._handle_help))
        application.add_handler(CommandHandler("id", cls._handle_id))
        application.add_handler(CommandHandler("codes", cls._handle_codes))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, cls._handle_shorthand)
        )

        async with application:
            await application.start()
            await application.updater.start_polling()
            stop_event = asyncio.Event()
            await stop_event.wait()

    @staticmethod
    async def _handle_start(update, context):
        await update.message.reply_text(
            "Esso Invoice Bot\n\n"
            "Send shorthand to add invoice items:\n"
            "CUSTOMER_CODE TEMPLATE_CODE QUANTITY\n\n"
            "Example: JOES CATERING 5\n\n"
            "Commands:\n"
            "/help - Show this message\n"
            "/codes - List all short codes\n"
            "/id - Show your Telegram user ID"
        )

    @staticmethod
    async def _handle_help(update, context):
        await update.message.reply_text(
            "Send shorthand to add invoice items:\n"
            "CUSTOMER_CODE TEMPLATE_CODE QUANTITY\n\n"
            "Example: JOES CATERING 5\n\n"
            "The bot will:\n"
            "1. Look up the customer by short code\n"
            "2. Look up the item template by short code\n"
            "3. Find an unsent invoice (or create one)\n"
            "4. Add the line item\n\n"
            "Commands:\n"
            "/help - Show this message\n"
            "/codes - List all short codes\n"
            "/id - Show your Telegram user ID"
        )

    @staticmethod
    async def _handle_id(update, context):
        user_id = update.effective_user.id
        await update.message.reply_text(f"Your Telegram user ID: {user_id}")

    @classmethod
    async def _handle_codes(cls, update, context):
        app = context.bot_data["flask_app"]
        user_id = update.effective_user.id

        allowed = cls.get_allowed_users(app)
        if user_id not in allowed:
            await update.message.reply_text(
                "Unauthorized. Your Telegram user ID is not whitelisted."
            )
            return

        with app.app_context():
            from inventory_api_app.models.invoice import Customer, InvoiceItemTemplate

            customers = Customer.query.filter(
                Customer.short_code.isnot(None),
                Customer.short_code != '',
            ).order_by(Customer.short_code).all()

            templates = InvoiceItemTemplate.query.filter(
                InvoiceItemTemplate.short_code.isnot(None),
                InvoiceItemTemplate.short_code != '',
            ).order_by(InvoiceItemTemplate.short_code).all()

        lines = ["Customers:"]
        if customers:
            for c in customers:
                lines.append(f"  {c.short_code} \u2192 {c.name}")
        else:
            lines.append("  (none configured)")

        lines.append("")
        lines.append("Templates:")
        if templates:
            for t in templates:
                price = f" (${t.price_per_unit:.2f})" if t.price_per_unit else ""
                lines.append(f"  {t.short_code} \u2192 {t.name}{price}")
        else:
            lines.append("  (none configured)")

        await update.message.reply_text("\n".join(lines))

    @classmethod
    async def _handle_shorthand(cls, update, context):
        app = context.bot_data["flask_app"]
        user_id = update.effective_user.id

        allowed = cls.get_allowed_users(app)
        if user_id not in allowed:
            await update.message.reply_text(
                "Unauthorized. Your Telegram user ID is not whitelisted."
            )
            return

        text = update.message.text

        try:
            customer_code, template_code, quantity = cls.parse_shorthand(text)

            with app.app_context():
                result = cls.process_shorthand(customer_code, template_code, quantity)

            status = "NEW" if result["created_new"] else "EXISTING"
            reply = (
                f"Added to Invoice #{result['invoice_number']} ({status})\n"
                f"Customer: {result['customer_name']}\n"
                f"Item: {result['item_description']}\n"
                f"Qty: {result['quantity']} x ${result['price_per_unit']:.2f}"
                f" = ${result['line_total']:.2f}\n"
                f"Invoice Total: ${result['invoice_total']:.2f}"
            )
            await update.message.reply_text(reply)

        except ValueError as e:
            await update.message.reply_text(f"Error: {e}")
