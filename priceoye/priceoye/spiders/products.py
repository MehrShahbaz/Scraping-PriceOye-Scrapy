import scrapy
from json import loads


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
                    yield response.follow(
                        href, self.parse_category, meta={"trail": [response.url]}
                    )

    def parse_category(self, response):
        """Parse subcategory pages and follow links to product pages."""
        trail = response.meta.get("trail", [])
        for url in response.css(".productBox a::attr(href)").getall():
            yield response.follow(
                url, self.parse_product, meta={"trail": trail + [response.url]}
            )

        next_page = response.css('.pagination a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_category, meta={"trail": trail})

    def parse_product(self, response):
        """Parse product details from the product page."""
        script = response.css('script:contains("product_data")').get()
        product_data = None

        if not script:
            return

        formated_script = script.split(" = ")[-1]
        formated_script = formated_script.split("</script>")[0]

        if not formated_script:
            return

        data = loads(formated_script)
        product_data = data.get("dataSet")

        if not product_data:
            return

        product = {
            "product_name": product_data["title"],
            "brand_name": product_data["brand_name"],
            "category": product_data["category_name"],
            "url": response.url,
            "trail": response.meta.get("trail", []),
        }

        product_variants = data.get("product_config").get("dataPrices")
        rating = product.get("ratings_data")
        if product_variants:
            image_urls = self.get_colors_dict(data)
            formated_data = self.get_data(product_variants)

            product["variants"] = self.format_data(
                formated_data, image_urls, self.get_product_images(product_data)
            )

        else:
            product["variants"] = [
                {
                    "color": None,
                    "images": self.get_product_images(product_data),
                    "size": None,
                    "price": product_data["expected_price"],
                    "prev_price": None,
                    "store_name": None,
                    "quantity": None,
                    "in_stock": False,
                }
            ]

        yield product

    def get_colors_dict(self, data):
        image_dict = data.get("product_color_images")

        if not image_dict:
            return None

        for color, images in image_dict.items():
            image_dict[color] = [
                "https://images.priceoye.pk/" + image for image in images
            ]
        return image_dict

    def get_data(self, data):
        data1 = list(data.values())
        formated_data = []

        if isinstance(data1[0], dict):
            for x in data1:
                data2 = list(x.values())
                data3 = [y for y in data2]
                formated_data.extend([d for sublist in data3 for d in sublist])

        elif isinstance(data1[0], list):
            return [
                dictionary
                for sublist1 in data1
                for sublist2 in sublist1
                for dictionary in sublist2
            ]
        else:
            return []

        return formated_data

    def format_data(self, data: list, colors, images):
        return [
            {
                "color": self.format_color(x["product_color"]),
                "images": colors.get(x["product_color"]) if colors else images,
                "size": x["product_size"],
                "price": self.format_price(x["product_price"]),
                "prev_price": self.format_price(x["retail_price"]),
                "store_name": x["store_name"],
                "in_stock": (
                    True if x["product_availability"].lower() == "in stock" else False
                ),
            }
            for x in data
        ]

    def format_price(self, price: str) -> int:
        if price:
            return int(price.replace(",", ""))

    def format_color(self, color: str) -> str:
        return color.replace("_", " ").title()

    def get_product_images(self, data):
        return data.get("api_image", [])
