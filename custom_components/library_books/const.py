"""Constants for the Library Books integration."""

DOMAIN = "library_books"

# Configuration constants
CONF_LIBRARY_TYPE = "library_type"
CONF_LIBRARY_URL = "library_base_url"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_NAME = "name"
CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_UPDATE_INTERVAL = 60  # in minutes
DEFAULT_CALENDAR_NAME = "Library Books"

# Supported library types
LIBRARY_TYPES = {
    "libero": "Libero Library System",
    # add others here, such as...
    #"koha": "Koha Library System",
    #"sirsi": "SirsiDynix", 
    #"polaris": "Polaris ILS",
    #"evergreen": "Evergreen ILS",
}

# Sensor names
SENSOR_NAME = "Library Books Outstanding"