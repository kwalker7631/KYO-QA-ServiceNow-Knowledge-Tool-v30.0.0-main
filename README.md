# KYO QA ServiceNow Knowledge Tool v30.0.0

A powerful desktop application for automating the extraction of key information from Kyocera QA/service PDFs using OCR and AI-powered pattern matching.

## Features

- **Automated PDF Processing**: Process hundreds of PDFs in batch or individually
- **Advanced OCR**: Automatic detection and processing of scanned documents with Tesseract OCR
- **AI-Powered Extraction**: Intelligent pattern matching to find product models, QA numbers, and metadata
- **Dynamic Pattern Management**: Add and manage custom regex patterns through the built-in Pattern Manager
- **Real-time Progress Tracking**: Color-coded status indicators, progress bars, and detailed logs
- **Excel Integration**: Updates ServiceNow-compatible Excel files with extracted data
- **Smart Caching**: Speeds up reprocessing with intelligent result caching
- **Review System**: Flag and review documents that need manual attention

## Requirements

- Windows 10/11 (64-bit)
- Python 3.9 or higher
- Tesseract OCR 5.0+
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space

## Installation

### 1. Install Python

Download and install Python 3.9+ from [python.org](https://www.python.org/downloads/). During installation, **ensure you check "Add Python to PATH"**.

### 2. Install Tesseract OCR

Download the Windows installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). During installation, select "Add to PATH" option.

### 3. Setup the Application

1. Extract the application files to your desired location
2. Double-click `START.bat` to launch the tool
3. On first run, the launcher will:
   - Create a virtual environment
   - Install all required dependencies
   - Generate necessary icons
   - Launch the main application

## Usage

### Basic Workflow

1. **Select Excel Template**: Click "Browse" to select your ServiceNow kb_knowledge.xlsx template
   - A short progress bar below the fields fills while the template loads
2. **Select PDFs**: Choose either:
   - A folder containing PDFs
   - Individual PDF files
3. **Start Processing**: Click the red START button
4. **Monitor Progress**: Watch real-time status updates and progress
5. **Review Results**: Check the generated Excel file in the `output` folder

### Pattern Management

The Pattern Manager allows you to create custom extraction patterns:

1. Click the "Patterns" button
2. Select pattern type (Model or QA Numbers)
3. For documents that failed extraction:
   - Highlight the missed text
   - Click "Suggest from Highlight"
   - Test and refine the pattern
   - Save to apply in future runs

### Understanding Status Indicators

- **Pass** (Green): Successful extraction
- **Fail** (Red): Processing error
- **Needs Review** (Orange): No patterns matched
- **OCR** (Blue): OCR was required
- **Protected** (Gray): Password-protected PDF
- **Corrupted** (Purple): Corrupted file

## Project Structure

```
KYO_QA_ServiceNow_Knowledge_Tool_v30.0.0/
├── START.bat                 # Windows launcher
├── run.py                    # Python launcher with setup
├── kyo_qa_tool_app.py        # Main GUI application
├── processing_engine.py      # Core processing logic
├── data_harvesters.py        # Pattern matching engine
├── ocr_utils.py             # OCR processing utilities
├── excel_generator.py        # Excel file generation
├── kyo_review_tool.py       # Pattern management UI
├── custom_patterns.py       # User-defined patterns
├── requirements.txt         # Python dependencies
├── logs/                    # Session logs
├── output/                  # Generated Excel files
└── PDF_TXT/                 # Text files for review
```

## Configuration

Edit `config.py` to customize:
- Extraction patterns
- Excel column mappings
- UI colors and branding
- Directory paths

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Ensure Tesseract is installed and in your PATH
2. **Import errors**: Delete the `venv` folder and run `START.bat` again
3. **Pattern matching failures**: Use the Pattern Manager to add custom patterns
4. **Excel file locked**: Close the Excel file before processing

### Logs

Check the `logs` folder for detailed error messages and processing history.

## Advanced Features

### Command Line Interface (Alpha)

```bash
python cli_runner.py --folder <PDF_folder> --excel <template.xlsx>
```

### Custom Pattern Development

Patterns use Python regex syntax. Examples:
- Model numbers: `r'\bTASKalfa\s+\d+[a-z]*\b'`
- QA numbers: `r'\bQA-\d+\b'`

## License

This software is licensed under the MIT License. See the LICENSE file for details.

## Author

**Kenneth Walker**  
*Freelance Programmer & TSC Support Engineer*

## Version History

- v30.0.0 (2025) - Major update with enhanced OCR, pattern management, and UI improvements
- v25.1.0 - Added review system and custom patterns
- v24.0.0 - Initial public release

## Support

For issues, feature requests, or questions, please contact the author.

---

© 2025 Kenneth C. Walker Jr. All rights reserved.