# Changelog

All notable changes to this project will be documented in this file.

## [1.8.0] - 2025-08-13

### 🎫 Ticket Design Enhancements
- **Compact Design**: Redesigned task tickets for better thermal printer output
- **Date Format**: Added creation date at top in dd-mm-yyyy format
- **Consistent Dates**: Changed due date format to dd-mm-yyyy
- **Clean Layout**: Removed lightning bolt emoji for cleaner appearance
- **Typography**: Optimized font sizes for readability while reducing physical size
- **Spacing**: Improved layout spacing for smaller ticket footprint

### 🖨️ Printing Improvements
- **Default Print**: Print checkbox now checked by default for user convenience
- **Text Wrapping**: Enhanced text wrapping for better thermal printer compatibility
- **Font Support**: Improved font fallback support for Linux/Docker environments

### ⚙️ Configuration Updates
- **Port Change**: Default port changed from 5000 to 8000 (avoids macOS AirPlay conflicts)
- **Environment Variables**: Added PORT environment variable for flexible configuration
- **Docker Compose**: Updated for new port and improved volume mounting
- **Ignore Files**: Added instance/ folder to .gitignore and .dockerignore

### 📚 Documentation
- **README**: Comprehensive update with all new features
- **Troubleshooting**: Added troubleshooting section for common issues
- **Docker**: Updated Docker Compose instructions
- **Development**: Added development and contribution guidelines
- **API**: Documented environment variables and configuration options

### 🐳 Docker Improvements
- **Simplified Setup**: Streamlined Docker Compose configuration
- **Volume Management**: Better handling of instance folder and data persistence
- **Port Mapping**: Updated to use port 8000
- **Container Optimization**: Removed unnecessary database container

### 🔧 Technical Changes
- **Flask Instance**: Proper use of Flask instance folder for database storage
- **Error Handling**: Improved error handling for font loading and image generation
- **Code Quality**: Better code organization and documentation

## Previous Versions

### [1.0.0] - Initial Release
- Basic Flask web application for task management
- Thermal printer integration with ESC/POS protocol
- SQLite database for task persistence
- Bootstrap-based responsive UI
- Docker support with basic configuration
