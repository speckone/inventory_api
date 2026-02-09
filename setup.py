from setuptools import setup, find_packages

__version__ = "0.1"

setup(
    name="inventory_api_app",
    version=__version__,
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.10",
    install_requires=[
        "flask>=3.0,<4",
        "flask-sqlalchemy>=3.1,<4",
        "flask-restful>=0.3.10,<1",
        "flask-migrate>=4.0,<5",
        "flask-jwt-extended>=4.6,<5",
        "flask-marshmallow>=1.0,<2",
        "flask-cors>=4.0,<5",
        "marshmallow>=3.20,<4",
        "marshmallow-sqlalchemy>=1.0,<2",
        "python-dotenv>=1.0,<2",
        "passlib>=1.7,<2",
        "apispec[yaml]>=6.3,<7",
        "apispec-webframeworks>=1.0,<2",
        "psycopg2-binary>=2.9,<3",
    ],
    entry_points={
        "console_scripts": [
            "inventory_api_app = inventory_api_app.manage:cli"
        ]
    },
)
