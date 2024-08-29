import csv
import time
from dataclasses import dataclass
from urllib.parse import urljoin

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

BASE_URL = "https://webscraper.io/"
HOME_URL = "test-sites/e-commerce/more/"

URLS_TO_PARSE = {
    "home": "test-sites/e-commerce/more/",
    "laptops": "test-sites/e-commerce/more/computers/laptops",
    "tablets": "test-sites/e-commerce/more/computers/tablets",
    "phones": "https://webscraper.io/test-sites/e-commerce/more/phones",
    "touch": "test-sites/e-commerce/more/phones/touch",
    "computers": "test-sites/e-commerce/more/computers",
}


@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: int


def parse_product(elem: WebElement) -> Product:
    return Product(
        title=elem.find_element(By.CSS_SELECTOR, ".caption > h4 > a").text,
        description=elem.find_element(
            By.CSS_SELECTOR, ".caption > p.description"
        ).text,
        price=float(elem.find_element(
            By.CSS_SELECTOR, ".caption > h4.float-end"
        ).text.replace("$", "")),
        rating=len(elem.find_elements(
            By.CSS_SELECTOR, ".ratings span.ws-icon-star")
        ),
        num_of_reviews=int(
            elem.find_element(
                By.CSS_SELECTOR, ".ratings > p.review-count"
            ).text.split(" ")[0]),
    )


def accept_cookie_banner(banner: WebElement) -> None:
    accept_button = banner.find_element(
        By.CSS_SELECTOR, ".acceptContainer > button.acceptCookies"
    )
    accept_button.click()


def parse_product_page(driver: WebDriver, url: str) -> [Product]:
    driver.get(urljoin(BASE_URL, url))
    try:
        cookie_banner = driver.find_element(By.ID, "cookieBanner")
        accept_cookie_banner(cookie_banner)
    except NoSuchElementException:
        ...

    while True:
        try:
            more_button = driver.find_element(
                By.CSS_SELECTOR, "a.ecomerce-items-scroll-more"
            )
            if not more_button.is_displayed():
                break
            wait = WebDriverWait(driver, 10)
            more_button = wait.until(ec.element_to_be_clickable(more_button))
        except NoSuchElementException:
            break
        print(more_button)
        more_button.click()
        time.sleep(1)

    products = driver.find_elements(By.CSS_SELECTOR, ".product-wrapper")
    return [parse_product(product) for product in products]


def write_products_to_csv(filename: str, products: [Product]) -> None:
    with open(f"{filename}.csv", "w", encoding="utf-8", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(
            ["title", "description", "price", "rating", "num_of_reviews"]
        )
        csv_writer.writerows(
            [
                [
                    product.title,
                    product.description,
                    product.price,
                    product.rating,
                    product.num_of_reviews,
                ]
                for product in products
            ],

        )


def get_all_products() -> None:
    driver = webdriver.Chrome()
    for filename, url in URLS_TO_PARSE.items():
        products = parse_product_page(
            driver,
            url
        )
        write_products_to_csv(filename, products)


if __name__ == "__main__":
    get_all_products()
