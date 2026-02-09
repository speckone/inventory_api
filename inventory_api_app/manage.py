import click
from flask import url_for, current_app
from flask.cli import FlaskGroup, with_appcontext
from inventory_api_app.app import create_app


def create_inventory_api_app():
    return create_app(cli=True)


@click.group(cls=FlaskGroup, create_app=create_inventory_api_app)
def cli():
    """Main entry point"""


@cli.command("init")
def init():
    """Create a new admin user
    """
    from inventory_api_app.extensions import db
    from inventory_api_app.models import User

    click.echo("create user")
    user = User(username="admin", email="tyson.koger@gmail.com", password="b1ueJay", active=True)
    db.session.add(user)
    db.session.commit()
    click.echo("created user admin")


if __name__ == "__main__":
    cli()
