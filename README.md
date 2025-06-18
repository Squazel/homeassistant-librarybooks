# Library Books Integration for Home Assistant

This Home Assistant integration scrapes your local library's website to determine which books you have outstanding or due. It provides this information through a calendar and sensor entities within Home Assistant.

## Features

- Tracks library books and their due dates
- Displays due dates in a Home Assistant calendar
- Shows book details including title, author, and overdue status
- Supports the Libero library system (with more systems planned)
- Provides sensor entities for real-time updates on outstanding books

## Supported Library Systems

- Libero Library System (fully supported)
- More library systems coming in the future

## Installation

### HACS Installation (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. Go to HACS → Integrations → ⋮ (menu) → Custom repositories
3. Add the URL: `https://github.com/Squazel/homeassistant-librarybooks`
4. Category: Integration
5. Click "Add"
6. Search for "Library Books" in HACS Integrations
7. Click "Download"
8. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/library_books` directory to your Home Assistant configuration directory.
2. Restart Home Assistant.

## Configuration

To configure the integration:

1. Go to the Home Assistant UI
2. Navigate to `Settings` > `Devices & Services`
3. Click `+ Add Integration` and search for `Library Books`
4. Follow the setup wizard:
   - Select your library system type
   - Enter your library URL
   - Provide your library card number/username
   - Enter your PIN/password
   - Configure calendar options

## Usage

Once configured, the integration will automatically fetch your library books and create:

1. A calendar showing all your books with due dates
2. Sensor entities with information about your books

### Calendar Integration

Each library account you configure will create a calendar in Home Assistant:

- Calendar entity IDs follow the format: `calendar.library_books_libraryname_username`
- Calendar display names show the library name you entered during setup
- If you have multiple accounts at the same library, you can adjust the library name to reflect this
- Due dates appear as all-day events
- Book details are included in the event information

You can add these calendars to any Home Assistant calendar card or connect them to external calendar applications.

## Troubleshooting

If you encounter issues:

1. Check that your library credentials are correct
2. Enable debug logging for more information:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.library_books: debug
   ```
3. Check the logs for error messages

## Requirements

- Home Assistant 2023.x or higher
- Library account with a supported system

## Contributing

Contributions are welcome! If you want to add support for additional library systems or improve the integration, please submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the LICENSE file for details.