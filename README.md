# Todo Manager with Thermal Printer Integration

A web-based task management application with integrated thermal printer support for printing compact task tickets.

## Features

- **Web-based Task Management**: Create, view, complete, and delete tasks through a responsive web interface
- **Task Fields**: Name, description, auto-generated creation date, due date, priority, and WORK/PERSONAL tag
- **REST API**: Create, read, update, filter, complete, delete, and print tasks
- **Thermal Printer Integration**: Print compact task tickets to ESC/POS compatible printers via Ethernet
- **Auto-Print Option**: Print checkbox is checked by default for convenient task printing
- **Compact Ticket Design**: 
  - Creation date at top (dd-mm-yyyy format)
  - Task name with proper text wrapping
  - Due date in dd-mm-yyyy format
  - Priority display
  - Optimized for thermal printer width
- **Database Persistence**: SQLite database for task storage with Flask instance folder
- **Responsive Design**: Mobile-friendly interface using Bootstrap
- **Docker Support**: Containerized deployment with Docker Compose
- **Configurable Port**: Runs on port 8000 by default (configurable via environment variable)

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd todo-escpos
```

2. Start the application (runs as non-root for security):
```bash
# Option A: Using the provided script (recommended)
./run-docker.sh -d

# Option B: Manual startup with user permissions
export UID=$(id -u) && export GID=$(id -g)
docker-compose up -d
```

3. Access the web interface at `http://localhost:8000`

**Security Note**: The Docker container runs as a non-root user for enhanced security. The startup script ensures proper file permissions for volume mounts.

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
# Or with custom port:
PORT=3000 python app.py
```

3. Access the web interface at `http://localhost:8000` (or your custom port)

## Thermal Printer Configuration

The application is designed to work with ESC/POS compatible thermal printers connected via Ethernet.

**Default Configuration:**
- IP Address: `172.31.23.129`
- Port: `9100`

To change the printer settings, set the `PRINTER_IP` and `PRINTER_PORT`
environment variables:

```bash
PRINTER_IP=172.31.23.129 PRINTER_PORT=9100 python app.py
```

**Supported Printers:**
- XPrinter XP-80T
- Most ESC/POS compatible thermal printers with Ethernet connectivity

## Usage

1. **Creating Tasks**: 
   - Fill out the task form with name, description, due date, and priority
   - Print option is checked by default - uncheck if you don't want immediate printing
2. **Task Tickets**: Compact design includes creation date, task name, due date, and priority
3. **Managing Tasks**: Use Complete, Print, or Delete buttons on task cards
4. **Bulk Operations**: Use "Complete All" to mark all tasks as completed

## API Endpoints

- `GET /` - Main task management interface
- `POST /add_task` - Create a new task
- `GET /complete_task/<id>` - Mark task as completed
- `GET /delete_task/<id>` - Delete a task
- `GET /print_task/<id>` - Print a specific task
- `GET /clear_all` - Mark all tasks as completed
- `GET /api/tasks` - List active tasks; filter with `tag=WORK|PERSONAL` and `completed=true|false`
- `POST /api/tasks` - Create a task from JSON
- `GET /api/tasks/<id>` - Get a task
- `PATCH /api/tasks/<id>` - Update one or more task fields
- `DELETE /api/tasks/<id>` - Delete a task
- `POST /api/tasks/<id>/complete` - Complete a task
- `POST /api/tasks/<id>/print` - Print a task
- `POST /api/tasks/complete-all` - Complete active tasks; accepts an optional `tag` filter

Create and update payloads use `YYYY-MM-DD` dates. Valid priorities are `HIGH`,
`MEDIUM`, and `LOW`; valid tags are `WORK` and `PERSONAL`.

The portable Hermes/OpenClaw skill is available at
[`skills/todo-escpos/SKILL.md`](skills/todo-escpos/SKILL.md). Configure
`TODO_ESCPOS_URL` in the agent environment before using it.

## Environment Variables

- `PORT` - Application port (default: 8000)
- `SECRET_KEY` - Flask secret key (default: dev key)
- `SQLALCHEMY_DATABASE_URI` - Database connection string
- `PRINTER_IP` - Thermal printer IP address (default: 172.31.23.129)
- `PRINTER_PORT` - Thermal printer network port (default: 9100)

## Database Schema

Tasks are stored with the following fields:
- `id` - Primary key
- `name` - Task name (required, max 200 chars)
- `description` - Task description (optional, text)
- `creation_date` - Auto-generated timestamp
- `due_date` - Required completion date
- `priority` - HIGH, MEDIUM, or LOW
- `tag` - WORK or PERSONAL
- `print_flag` - Whether task was marked for printing
- `completed` - Task completion status (boolean)

## Development

### Project Structure

```
todo-escpos/
├── app.py                          # Main Flask application
├── templates/
│   └── index.html                  # Web interface template
├── task_card_generator/
│   ├── __init__.py                # Package exports
│   ├── config.py                  # Configuration and imports
│   ├── image_generator.py         # Compact task image creation
│   ├── pdf_generator.py           # PDF generation (optional)
│   └── printer.py                 # ESC/POS printer interface
├── instance/                      # Flask instance folder (auto-created)
│   └── todo_manager.db           # SQLite database (auto-created)
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container build configuration
├── docker-compose.yml            # Multi-container setup
├── .gitignore                     # Git ignore file
├── .dockerignore                  # Docker ignore file
└── README.md                      # This file
```

### Key Components

- **Flask Web App**: Handles web interface and API endpoints
- **SQLAlchemy**: Database ORM for task persistence
- **Task Card Generator**: Creates compact printable images optimized for thermal printers
- **ESC/POS Printer Interface**: Communicates with thermal printer via Ethernet
- **Bootstrap UI**: Responsive, mobile-friendly web interface

### Recent Updates

- ✅ **Compact Ticket Design**: Smaller, more efficient thermal printer output
- ✅ **Date Format**: Creation and due dates now use dd-mm-yyyy format
- ✅ **Auto-Print**: Print checkbox checked by default
- ✅ **Port Configuration**: Configurable port (default 8000) to avoid macOS conflicts
- ✅ **Instance Folder**: Proper Flask instance folder for database and config
- ✅ **Docker Optimization**: Updated Docker Compose for new configuration

### Running in Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default port (8000)
python app.py

# Run with custom port
PORT=3000 python app.py

# Run with Flask CLI
flask run --port 8000
```

### Building Docker Image

```bash
# Build image
docker build -t todo-escpos .

# Run container (non-root for security)
docker run -p 8000:8000 -v ./instance:/app/instance todo-escpos

# Or use Docker Compose
./run-docker.sh --build
```

### GHCR image

Pushes to `main` and semantic version tags publish the image to
`ghcr.io/jmm-org1/todo-escpos`. Authenticate with a GitHub token that can read
packages, then pull `ghcr.io/jmm-org1/todo-escpos:latest`.

## Security Features

### Non-Root Container Execution
- ✅ **Container Security**: Runs as non-root user (appuser) inside container
- ✅ **Host Permission Mapping**: Uses host user ID to avoid permission conflicts
- ✅ **Volume Security**: Proper ownership of mounted volumes
- ✅ **Startup Script**: `run-docker.sh` handles user ID mapping automatically

### File Permissions
- Database and instance files owned by running user
- No root privileges required for operation
- Secure volume mounting with proper permissions

## Troubleshooting

### Common Issues

1. **Port 5000 conflict on macOS**: Use port 8000 (default) or set custom port with `PORT` environment variable
2. **Printer not found**: Check printer IP address and network connectivity
3. **Database issues**: Ensure `instance/` folder has write permissions
4. **Font issues**: Application includes fallback fonts for Linux/Docker environments

### Printer Testing

To test printer connectivity without the web interface:
```bash
python -c "
from task_card_generator import print_to_thermal_printer, create_task_image
from datetime import datetime

# Test data
task_data = {
    'title': 'Test Task',
    'creation_date': datetime.now(),
    'due_date': datetime.now(),
    'priority': 'MEDIUM'
}

# Create and print test image
image_path = create_task_image(task_data)
if image_path:
    print_to_thermal_printer(image_path)
    print('Test ticket sent to printer')
"
```

## License

Open source project for task management and thermal printer integration.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with both web interface and printer functionality
5. Submit a pull request

For issues or feature requests, please use the GitHub issue tracker.
