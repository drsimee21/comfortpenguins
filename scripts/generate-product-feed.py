#!/usr/bin/env python3
"""Generate the shared Comfort Penguins shopping product feed.

The site is static, so product data lives in data/products.json and this script
turns every active product into a Google/Pinterest-style RSS 2.0 XML feed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_PATH = ROOT / "data" / "products.json"
FEED_PATH = ROOT / "product-feed.xml"

G_NS = "http://base.google.com/ns/1.0"
ET.register_namespace("g", G_NS)

REQUIRED_ACTIVE_FIELDS = [
    "id",
    "title",
    "description",
    "link",
    "image_link",
    "availability",
    "price",
    "brand",
    "condition",
]

GOOGLE_AVAILABILITY = {
    "in stock": "in_stock",
    "in_stock": "in_stock",
    "out of stock": "out_of_stock",
    "out_of_stock": "out_of_stock",
    "preorder": "preorder",
    "backorder": "backorder",
}

PINTEREST_AVAILABILITY = {
    "in stock": "in stock",
    "in_stock": "in stock",
    "out of stock": "out of stock",
    "out_of_stock": "out of stock",
    "preorder": "preorder",
    "backorder": "preorder",
}

PRICE_RE = re.compile(r"^\d+(?:\.\d{2})?\s+[A-Z]{3}$")


def text(value: Any) -> str:
    return str(value or "").strip()


def add(parent: ET.Element, name: str, value: Any, namespace: str | None = None) -> None:
    value_text = text(value)
    if not value_text:
        return

    tag = f"{{{namespace}}}{name}" if namespace else name
    child = ET.SubElement(parent, tag)
    child.text = value_text


def load_catalog() -> dict[str, Any]:
    return json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))


def active_products(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    return [product for product in catalog.get("products", []) if product.get("active") is True]


def validate_product(product: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_ACTIVE_FIELDS if not text(product.get(field))]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"{product.get('id', 'unknown product')}: missing required fields: {joined}")

    availability = text(product.get("availability")).lower()
    if availability not in GOOGLE_AVAILABILITY:
        supported = ", ".join(sorted(GOOGLE_AVAILABILITY))
        raise ValueError(f"{product['id']}: unsupported availability '{availability}'. Use one of: {supported}")

    if not PRICE_RE.match(text(product.get("price"))):
        raise ValueError(f"{product['id']}: price must look like '39.00 USD'")

    sale_price = text(product.get("sale_price"))
    if sale_price and not PRICE_RE.match(sale_price):
        raise ValueError(f"{product['id']}: sale_price must look like '29.00 USD'")

    for url_field in ("link", "image_link"):
        if not text(product.get(url_field)).startswith("https://"):
            raise ValueError(f"{product['id']}: {url_field} must be an absolute HTTPS URL")


def build_item(channel: ET.Element, product: dict[str, Any]) -> None:
    validate_product(product)

    availability_key = text(product.get("availability")).lower()
    item = ET.SubElement(channel, "item")

    # Standard RSS fields help feed readers and non-Google parsers.
    add(item, "title", product.get("title"))
    add(item, "link", product.get("link"))
    add(item, "description", product.get("description"))

    # Google namespace fields are also accepted by many catalog importers.
    add(item, "id", product.get("id"), G_NS)
    add(item, "title", product.get("title"), G_NS)
    add(item, "description", product.get("description"), G_NS)
    add(item, "link", product.get("link"), G_NS)
    add(item, "image_link", product.get("image_link"), G_NS)

    for image_url in product.get("additional_image_link", []):
        add(item, "additional_image_link", image_url, G_NS)

    add(item, "availability", GOOGLE_AVAILABILITY[availability_key], G_NS)
    add(item, "price", product.get("price"), G_NS)
    add(item, "sale_price", product.get("sale_price"), G_NS)
    add(item, "brand", product.get("brand"), G_NS)
    add(item, "condition", product.get("condition"), G_NS)
    add(item, "google_product_category", product.get("google_product_category"), G_NS)
    add(item, "product_type", product.get("product_type"), G_NS)
    add(item, "color", product.get("color"), G_NS)
    add(item, "size", product.get("size"), G_NS)
    add(item, "material", product.get("material"), G_NS)
    add(item, "item_group_id", product.get("item_group_id"), G_NS)
    add(item, "availability_date", product.get("availability_date"), G_NS)

    # Unprefixed mirror fields make the same XML friendlier for Pinterest-style
    # parsers that document plain column names for RSS/CSV/TSV feeds.
    add(item, "id", product.get("id"))
    add(item, "image_link", product.get("image_link"))
    add(item, "availability", PINTEREST_AVAILABILITY[availability_key])
    add(item, "price", product.get("price"))
    add(item, "brand", product.get("brand"))
    add(item, "condition", product.get("condition"))

    for shipping in product.get("shipping", []):
        shipping_price = text(shipping.get("price"))
        if not shipping_price:
            continue
        shipping_value = ":".join(
            [
                text(shipping.get("country")),
                text(shipping.get("region")),
                text(shipping.get("service")),
                shipping_price,
            ]
        )
        add(item, "shipping", shipping_value, G_NS)


def build_feed(catalog: dict[str, Any]) -> ET.ElementTree:
    store = catalog.get("store", {})
    rss = ET.Element("rss", {"version": "2.0"})
    rss.set(f"xmlns:g", G_NS)

    channel = ET.SubElement(rss, "channel")
    add(channel, "title", f"{text(store.get('name'))} Product Feed")
    add(channel, "link", store.get("url"))
    add(channel, "description", "Active Comfort Penguins products for shopping platforms.")
    add(channel, "lastBuildDate", datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"))

    for product in active_products(catalog):
        build_item(channel, product)

    return ET.ElementTree(rss)


def main() -> None:
    catalog = load_catalog()
    tree = build_feed(catalog)
    ET.indent(tree, space="  ")
    tree.write(FEED_PATH, encoding="utf-8", xml_declaration=True)
    active_count = len(active_products(catalog))
    print(f"Wrote {FEED_PATH.relative_to(ROOT)} with {active_count} active product(s).")


if __name__ == "__main__":
    main()
