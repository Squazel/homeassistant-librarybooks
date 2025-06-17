# Constants for the library books integration

DOMAIN = "library_books"
CONF_LIBRARY_URL = "library_url"
CONF_LIBRARY_TYPE = "library_type"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_CALENDAR_NAME = "calendar_name"
CONF_USE_SEPARATE_CALENDARS = "use_separate_calendars"

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