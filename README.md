# Scrape Priceoye using Scrapy

This python project scrapes website [Priceoye](https://priceoye.pk/)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies.

```bash
pip install -r requirements.txt
```

## Usage

### Command
#### Scrape website
```bash
scrapy crawl products
```
#### Scrape website and write data in file
```bash
scrapy crawl products -O products.json
```

## Description

- After the Usage command is run the website will be scrapped
- A new file (products.json) if not existing will be created
- The data will be stored in the file

## Data Format

```bash
[
   {
    "product_name": "String",
    "brand_name": "String",
    "category": "String",
    "url": "String",
    "trail": ["String"],
    "variants": [
      {
        "color": "String",
        "images": ["String"],
        "size": "String",
        "price": Int,
        "prev_price": Int,
        "store_name": "String",
        "in_stock": Bool
      },
    ]
  }
]
```

## Sample Data

```bash
{
    "product_name": "Nokia 130",
    "brand_name": "Nokia",
    "category": "Mobiles",
    "url": "https://priceoye.pk/mobiles/nokia/nokia-130",
    "trail": ["https://priceoye.pk", "https://priceoye.pk/mobiles"],
    "variants": [
      {
        "color": "Black",
        "images": [
          "https://images.priceoye.pk/nokia-130-pakistan-priceoye-83wpb-500x500.webp",
          "https://images.priceoye.pk/nokia-130-pakistan-priceoye-f9oye-500x500.webp",
          "https://images.priceoye.pk/nokia-130-pakistan-priceoye-9io8w-500x500.webp"
        ],
        "size": "standard",
        "price": 5399,
        "prev_price": 8499,
        "store_name": "Priceoye",
        "in_stock": true
      },
    ]
  }
```

## Packages used

- Python (3.12.2)
- Scrapy (2.11.2)

