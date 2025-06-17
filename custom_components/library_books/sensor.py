from homeassistant.helpers.entity import Entity
import requests
from bs4 import BeautifulSoup
from .const import DOMAIN, SENSOR_NAME

class LibraryBooksSensor(Entity):
    def __init__(self):
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return SENSOR_NAME

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        self._scrape_library_website()

    def _scrape_library_website(self):
        url = "http://your-library-website.com/your-endpoint"  # Replace with actual URL
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Example scraping logic (customize based on actual website structure)
        self._state = soup.find("div", class_="outstanding-books").text.strip()
        self._attributes["due_dates"] = self._parse_due_dates(soup)

    def _parse_due_dates(self, soup):
        due_dates = {}
        for book in soup.find_all("div", class_="book"):
            title = book.find("h3").text.strip()
            due_date = book.find("span", class_="due-date").text.strip()
            due_dates[title] = due_date
        return due_dates