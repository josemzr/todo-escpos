# Quick Start Guide

Get your Todo Manager with Thermal Printer Integration up and running in minutes!

## Prerequisites

- Docker and Docker Compose installed
- ESC/POS compatible thermal printer (optional, for printing functionality)
- Network access to your thermal printer (if using printer features)

## Installation Methods

### Method 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/jmm-org1/todo-escpos.git
cd todo-escpos

# Start the application (secure non-root mode)
./run-docker.sh -d

# Alternative: Manual startup
export UID=$(id -u) && export GID=$(id -g)
docker-compose up -d

# Access the application
open http://localhost:8000
```

**Security Feature**: The container runs as a non-root user for enhanced security.

### Method 2: Local Python Installation

```bash
# Clone and navigate
git clone https://github.com/jmm-org1/todo-escpos.git
cd todo-escpos

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access the application
open http://localhost:8000
```

### Method 3: Custom Port

```bash
# Using environment variable
PORT=3000 python app.py

# Or with Docker Compose
echo "PORT=3000" > .env
docker-compose up -d
```

## First Steps

1. **Access the Web Interface**: Open `http://localhost:8000` in your browser

2. **Create Your First Task**:
   - Enter a task name (required)
   - Add description (optional)
   - Set due date
   - Choose priority level
   - Print option is checked by default - uncheck if not printing

3. **Configure Printer** (Optional):
   - Edit `task_card_generator/printer.py`
   - Update `printer_ip` to your printer's IP address
   - Update `printer_port` if needed (default: 9100)

## Features Overview

### Task Management
- ✅ Create tasks with name, description, due date, priority
- ✅ View all active tasks in a responsive interface
- ✅ Mark tasks as complete or delete them
- ✅ Bulk operations (complete all tasks)

### Thermal Printing
- 🖨️ Auto-print option (checked by default)
- 🎫 Compact ticket design optimized for thermal printers
- 📅 Creation and due dates in dd-mm-yyyy format
- 🎯 Priority indicators
- 📏 Optimized for standard thermal printer width (58mm/72mm)

### Web Interface
- 📱 Mobile-friendly responsive design
- 🎨 Bootstrap-based modern UI
- ⚡ Real-time feedback with flash messages
- 🔄 AJAX-ready API endpoints

## Printer Setup

### Compatible Printers
- XPrinter XP-80T
- Most ESC/POS compatible thermal printers
- Network-connected printers (Ethernet)

### Network Configuration
1. Connect printer to your network
2. Note the printer's IP address
3. Update `printer_ip` in `task_card_generator/printer.py`
4. Test with the print function

### Testing Printer Connection
```python
# Quick printer test
python -c "
from task_card_generator import create_task_image, print_to_thermal_printer
from datetime import datetime

test_task = {
    'title': 'Test Print',
    'creation_date': datetime.now(),
    'due_date': datetime.now(),
    'priority': 'MEDIUM'
}

image_path = create_task_image(test_task)
if image_path:
    print_to_thermal_printer(image_path)
    print('Test ticket sent!')
"
```

## Common Issues & Solutions

### Port Conflicts (macOS)
**Problem**: Port 5000 is used by AirPlay Receiver on macOS
**Solution**: App now uses port 8000 by default

### Database Permissions
**Problem**: Database creation fails
**Solution**: Ensure write permissions in the project directory

### Printer Not Found
**Problem**: Cannot connect to thermal printer
**Solution**: 
1. Check printer IP address
2. Ensure printer is on same network
3. Test network connectivity: `ping [printer_ip]`

### Font Issues in Docker
**Problem**: Fonts not loading properly
**Solution**: App includes fallback fonts for Linux environments

## Next Steps

1. **Customize**: Modify printer settings, task fields, or UI styling
2. **Integrate**: Use the JSON API (`/api/tasks`) for integration with other systems
3. **Deploy**: Use Docker Compose for production deployment
4. **Extend**: Add features like task categories, due date reminders, etc.

## Support

- 📖 Full documentation: See [README.md](README.md)
- 🐛 Report issues: Use GitHub Issues
- 💡 Feature requests: Use GitHub Discussions
- 📝 Changelog: See [CHANGELOG.md](CHANGELOG.md)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | Application port |
| `SECRET_KEY` | dev-key | Flask secret key |
| `SQLALCHEMY_DATABASE_URI` | sqlite:///instance/todo_manager.db | Database connection |

That's it! You're ready to manage tasks and print thermal tickets! 🎉
