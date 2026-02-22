"""Simple helper to paginate query"""
import math

from flask import request

DEFAULT_PAGE_SIZE = 25
DEFAULT_PAGE_NUMBER = 1


def paginate(query, schema):
    """Paginate a SQLAlchemy query and serialize results with the given schema.

    Reads ``page`` and ``per_page`` from ``request.args`` (defaults: 1 / 25).
    Returns a dict with ``results``, ``total``, ``page`` and ``pages``.
    """
    page = request.args.get("page", DEFAULT_PAGE_NUMBER, type=int)
    per_page = request.args.get("per_page", DEFAULT_PAGE_SIZE, type=int)

    # Clamp to sane boundaries
    page = max(1, page)
    per_page = max(1, min(per_page, 10000))

    page_obj = query.paginate(page=page, per_page=per_page, error_out=False)
    total = page_obj.total
    pages = math.ceil(total / per_page) if per_page else 0

    return {
        "results": schema.dump(page_obj.items),
        "total": total,
        "page": page,
        "pages": pages,
    }
