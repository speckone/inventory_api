import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app, render_template
from inventory_api_app.extensions import db
from inventory_api_app.models.settings import AppSetting


class EmailService:
    @staticmethod
    def send_async(app, recipient, subject, html, cc=None, bcc=None, attachments=None):
        """Send email in background thread with app context."""
        with app.app_context():
            try:
                server = db.session.get(AppSetting, 'mail_server')
                port = db.session.get(AppSetting, 'mail_port')
                use_ssl = db.session.get(AppSetting, 'mail_use_ssl')
                username = db.session.get(AppSetting, 'mail_username')
                password = db.session.get(AppSetting, 'mail_password')
                sender = db.session.get(AppSetting, 'mail_default_sender')

                server_val = server.value if server else None
                port_val = int(port.value) if port and port.value else 465
                use_ssl_val = use_ssl.value != '0' if use_ssl and use_ssl.value else True
                username_val = username.value if username else None
                password_val = password.value if password else None
                sender_val = sender.value if sender else username_val

                if not server_val or not username_val or not password_val:
                    app.logger.warning("Email settings incomplete, skipping send")
                    return

                if attachments:
                    msg = MIMEMultipart('mixed')
                    html_part = MIMEMultipart('alternative')
                    html_part.attach(MIMEText(html, 'html'))
                    msg.attach(html_part)
                    for att in attachments:
                        part = MIMEBase(*att['content_type'].split('/'))
                        part.set_payload(att['content'])
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'attachment', filename=att['filename'])
                        msg.attach(part)
                else:
                    msg = MIMEMultipart('alternative')
                    msg.attach(MIMEText(html, 'html'))

                msg['Subject'] = subject
                msg['From'] = sender_val
                msg['To'] = recipient

                if cc:
                    msg['Cc'] = ', '.join(cc)

                if bcc:
                    msg['Bcc'] = bcc if isinstance(bcc, str) else ', '.join(bcc)

                bcc_list = []
                if bcc:
                    bcc_list = [bcc] if isinstance(bcc, str) else list(bcc)

                all_recipients = [recipient] + (cc or []) + bcc_list

                if use_ssl_val:
                    with smtplib.SMTP_SSL(server_val, port_val) as smtp:
                        smtp.login(username_val, password_val)
                        smtp.sendmail(sender_val, all_recipients, msg.as_string())
                else:
                    with smtplib.SMTP(server_val, port_val) as smtp:
                        smtp.starttls()
                        smtp.login(username_val, password_val)
                        smtp.sendmail(sender_val, all_recipients, msg.as_string())
            except Exception:
                app.logger.exception("Failed to send email: subject=%s", subject)

    @classmethod
    def send_order_email(cls, order):
        """Compose and send order submission email."""
        recipient_setting = db.session.get(AppSetting, 'mail_order_recipient')
        to_email = recipient_setting.value if recipient_setting else None
        if not to_email:
            current_app.logger.warning("mail_order_recipient not configured, skipping email")
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

        app = current_app._get_current_object()
        thread = threading.Thread(target=cls.send_async, args=(app, to_email, "New Inventory Order", html))
        thread.start()

    @classmethod
    def send_invoice_email(cls, invoice, customer, pdf_bytes):
        """Send invoice email with PDF attachment to customer contacts."""
        from inventory_api_app.models.invoice import CustomerContact

        contacts = CustomerContact.query.filter_by(customer_id=customer.id).all()
        primary = next((c for c in contacts if c.primary), None)
        if not primary:
            current_app.logger.warning("No primary contact for customer %s", customer.id)
            return {"error": "No primary contact found for this customer"}, 400

        to_email = primary.email
        cc_emails = [c.email for c in contacts if not c.primary and c.email]

        html = render_template(
            "emails/invoice_sent.html",
            contact_name=primary.name,
            invoice_number=invoice.invoice_number,
            subtotal=f"{invoice.subtotal:.2f}" if invoice.subtotal else "0.00",
            date=str(invoice.date) if invoice.date else "",
            customer_name=customer.name,
        )

        attachments = [{
            "filename": f"invoice_{invoice.invoice_number}.pdf",
            "content": pdf_bytes,
            "content_type": "application/pdf",
        }]

        app = current_app._get_current_object()
        subject = f"Invoice #{invoice.invoice_number} from Esso Coffeehouse"
        thread = threading.Thread(
            target=cls.send_async,
            args=(app, to_email, subject, html),
            kwargs={"cc": cc_emails, "bcc": "sharon@essocoffeeshop.com", "attachments": attachments},
        )
        thread.start()
        return None
