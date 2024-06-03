import scrapy
import json
import re


class ProductsSpider(scrapy.Spider):
    name = "products"

    start_urls = [
        "https://priceoye.pk",
    ]

    avoid_text = ["mobiles accessories", "TV & Home Appliances", "Personal Cares"]

    def parse(self, response):
        """Parse the main category page and follow links to subcategories."""
        for link in response.css(".all-cat-icon a"):
            if link.css("::text").get() not in self.avoid_text:
                href = link.css("::attr(href)").get()
                if href:
                    yield response.follow(href, self.parse_category)

    def parse_category(self, response):
        """Parse subcategory pages and follow links to product pages."""
        for url in response.css(".productBox a::attr(href)").getall():
            yield response.follow(url, self.parse_product)

        next_page = response.css('.pagination a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_category)

    def parse_product(self, response):
        """Parse product details from the product page."""
        json_data = self.extract_ld_json(response)

        if not json_data:
            return

        offers = json_data.get("offers", {})
        aggregate_rating = json_data.get("aggregateRating", {})
        previous_price = self.extract_previous_price(response)

        yield {
            "product_name": json_data.get("name", ""),
            "brand_name": json_data.get("brand", ""),
            "price": int(offers.get("price", 0)),
            "previous_price": previous_price,
            "currency": offers.get("priceCurrency"),
            "images": self.extract_images(response),
            "in_stock": self.is_in_stock(response),
            "rating": float(aggregate_rating.get("ratingValue", 0.0)),
            "rating_count": int(aggregate_rating.get("ratingCount", 0)),
            "colors": response.css(".color-name span::text").getall(),
            "product_url": json_data.get("url", ""),
        }

    def extract_ld_json(self, response):
        """Extract and sanitize JSON data from LD+JSON script tags."""
        ld_json_scripts = response.css('script[type="application/ld+json"]').getall()

        if len(ld_json_scripts) > 2:
            json_string = ld_json_scripts[2].strip()
            sanitized_json_string = json_string.replace("\n", " ").replace("\r", " ")
            sanitized_json_string = re.sub(
                r"[\x00-\x1f\x7f]", "", sanitized_json_string
            )

            sanitized_json_string = re.search(
                r"(?<=>)\s*(.*?)\s*(?=<)", sanitized_json_string, re.DOTALL
            ).group(1)

            try:
                return json.loads(sanitized_json_string)
            except json.JSONDecodeError:
                self.logger.error("Failed to decode JSON")
                return {}
        return {}

    def extract_previous_price(self, response):
        """Extract the previous price from the product page."""
        previous_price = (
            response.css(".stock-info::text").get(default="0").strip().replace(",", "")
        )
        return int(previous_price) if previous_price.isdigit() else None

    def extract_images(self, response):
        """Extract product images from the product page."""
        images = response.css(".product-image-thumbnail img::attr(src)").getall()
        if not images:
            images = response.css("#product-image-main img::attr(src)").getall()
        return images

    def is_in_stock(self, response):
        """Check if the product is in stock."""
        return response.css(".stock-status::text").get() == "In Stock"
