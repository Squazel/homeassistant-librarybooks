# Library Books Integration for Home Assistant

Never forget to return a library book again! Track your outstanding library books and due dates directly in Home Assistant.

## ✨ Features

- 📅 **Calendar Integration** - View due dates in Home Assistant calendar
- 📊 **Real-time Sensors** - Book counts, overdue status, and details
- 🚨 **Overdue Detection** - Never miss a return date
- 📖 **Rich Details** - Titles, authors, ISBNs, and cover images

## 🏛️ Supported Libraries

- ✅ **Libero Library System** (fully supported)
- 🔜 More systems coming soon

## 🚀 Installation

Install via HACS or manually. See [complete documentation](https://github.com/Squazel/homeassistant-librarybooks) for setup instructions.

## 📱 Quick Example

```yaml
# Get notified when you have overdue books
automation:
  - alias: "Overdue Library Books Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.library_overdue_books
      above: 0
    action:
      service: notify.mobile_app
      data:
        message: "You have {{ states('sensor.library_overdue_books') }} overdue library books!"
```

---
📖 **[Full Documentation & Setup Guide →](https://github.com/Squazel/homeassistant-librarybooks)**