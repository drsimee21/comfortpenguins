# Product Catalog Source

`products.json` is the source of truth for Comfort Penguins shopping feeds.

Only products with `"active": true` are included in `product-feed.xml`.

Before making a product active, make sure it has:

- A real product title and plain-text description.
- A public HTTPS product page URL.
- A public HTTPS image URL.
- A visible price on the product page, formatted like `39.00 USD`.
- A supported availability value: `in stock`, `out of stock`, `preorder`, or `backorder`.
- Shipping details if you want the feed to submit shipping data.

Run this after editing product data:

```sh
python3 scripts/generate-product-feed.py
```

The GitHub workflow also regenerates the feed automatically when this file changes on `main`.
