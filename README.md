# Library Books Integration

This project is a Home Assistant integration that scrapes your local library's website to determine which books you have outstanding or due. It provides this information in a user-friendly format through a calendar and sensor entities within Home Assistant.

## Features

- Scrapes library website for outstanding books
- Displays due dates in a Home Assistant calendar
- Provides sensor entities for real-time updates on outstanding books

## Installation

1. Clone this repository to your local machine:
   ```
   git clone https://github.com/yourusername/library-books-integration.git
   ```

2. Navigate to the project directory:
   ```
   cd library-books-integration
   ```

3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

4. Add the `library_books` custom component to your Home Assistant configuration.

## Configuration

To configure the integration, follow these steps:

1. Go to the Home Assistant UI.
2. Navigate to `Configuration` > `Integrations`.
3. Search for `Library Books` and follow the prompts to set it up.

## Usage

Once configured, the integration will automatically scrape your library's website and update the calendar and sensor entities with the relevant information about your outstanding books.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.