# Metadata Editor

> ⚠️ **Work in Progress** - Not ready for production use.

A metadata editor for images with a clean interface.

## Current Status

**Working:**
- Folder selection and image scanning
- Dark/light theme switching
- Basic UI navigation
- Backend API structure

**Not Working:**
- Metadata editing functionality
- EXIF data modification
- File saving
- Learning/suggestions system

## Planned Features

- Edit metadata for multiple images
- View and modify EXIF data
- Save changes to files
- Learning from previous inputs
- Support for IPTC and XMP metadata

## How to Run This Thing

### What You'll Need

- Python 3.8+ (probably works with older versions but haven't tested)
- Node.js 16+ 
- npm (comes with Node usually)

### Getting It Running

1. **Get the code**
   ```bash
   git clone <repository-url>
   cd meta-data
   ```

2. **Install the Python bits**
   ```bash
   pip install -r requirements.txt
   ```
   (If this breaks, you're on your own - I'm still learning this stuff)

3. **Install the frontend bits**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Actually Starting It

**Easy way (usually works):**
```bash
python start.py
```

This should:
- Find ports that aren't already being used
- Make the frontend and backend talk to each other
- Start everything up
- Tell you where to go in your browser

**Hard way (if the easy way doesn't work):**
```bash
# Terminal 1: Backend
python app.py

# Terminal 2: Frontend  
cd frontend
npm start
```

## Current Functionality

1. Select a folder containing images
2. View folder structure in sidebar
3. Switch between light and dark themes
4. Navigate between pages

**Note**: Metadata editing is not yet implemented.

## Architecture

- **Frontend**: React with TypeScript and Tailwind CSS
- **Backend**: Python Flask with Pillow for image processing
- **Database**: SQLite for data storage
- **File Processing**: ExifTool integration

## Troubleshooting

### Port Already in Use
The startup script automatically finds available ports. For manual startup:

1. Check what's using the port: `lsof -i :5000` (or :3000)
2. Stop the process or change the port in `config.json`

### Dependencies Issues
```bash
# Reinstall Python dependencies
pip install -r requirements.txt

# Reinstall frontend dependencies
cd frontend && npm install
```

### Permission Issues
Ensure write permissions to the project directory.

## Contributing

This is a personal project under development. Contributions welcome:
- Report issues
- Suggest improvements
- Submit pull requests

## License

MIT License - see the [LICENSE](LICENSE) file for details.

---

**Status**: Work in progress - expect changes and incomplete features. 