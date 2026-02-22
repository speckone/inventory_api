import os

import click
from flask.cli import FlaskGroup
from inventory_api_app.app import create_app


def create_inventory_api_app():
    return create_app(cli=True)


@click.group(cls=FlaskGroup, create_app=create_inventory_api_app)
def cli():
    """Main entry point"""


@cli.command("init")
@click.option("--username", default=None, help="Admin username")
@click.option("--email", default=None, help="Admin email")
@click.option("--password", default=None, help="Admin password")
def init(username, email, password):
    """Create a new admin user"""
    from inventory_api_app.extensions import db
    from inventory_api_app.models import User

    admin_user = username or os.getenv("ADMIN_USER")
    admin_email = email or os.getenv("ADMIN_EMAIL")
    admin_pass = password or os.getenv("ADMIN_PASS")

    if not all([admin_user, admin_email, admin_pass]):
        raise click.UsageError(
            "Admin credentials required. Provide --username, --email, and --password "
            "options or set ADMIN_USER, ADMIN_EMAIL, and ADMIN_PASS environment variables."
        )

    click.echo("create user")
    user = User(username=admin_user, email=admin_email, password=admin_pass, active=True)
    db.session.add(user)
    db.session.commit()
    click.echo(f"created user {admin_user}")


if __name__ == "__main__":
    cli()
