# Document Content Extractor

## Objective
The Document Content Extractor is a Python application designed to extract text, hyperlinks, images, and tables from PDF, DOCX, and PPTX files. The system uses a modular object-oriented approach with abstract classes to provide a flexible and extensible architecture that supports different file types and storage methods. The extracted content includes metadata such as page numbers, font styles, and layout information.

## Main Components

### 1. File Structure
```
Assignment3-Python/
├── file_loader.py      # Handles loading different file types
├── data_extractor.py   # Extracts content from loaded files
├── storage.py          # Stores extracted data in files or database
├── main.py             # Main script to run the application
├── requirements.txt    # Lists required Python packages
├── run_tests.py        # Script to run all unit tests
├── tests/              # Unit tests directory
│   ├── __init__.py
│   ├── test_file_loader.py
│   ├── test_data_extractor.py
│   └── test_storage.py
└── output/             # Output directory (created when run)
    ├── text/           # Extracted text data
    ├── links/          # Extracted hyperlink data
    ├── images/         # Extracted images and their metadata
    └── tables/         # Extracted tables and their metadata
```

### 2. Key Files

1. **file_loader.py**
   - Contains the abstract `FileLoader` class
   - Implements concrete loaders for PDF, DOCX, and PPTX files
   - Each loader validates and loads the appropriate file type

2. **data_extractor.py**
   - Contains the `DataExtractor` class
   - Works with any FileLoader to extract content
   - Provides methods for extracting text, links, images, and tables with metadata

3. **storage.py**
   - Contains the abstract `Storage` class
   - Implements `FileStorage` for saving to files (CSV/JSON)
   - Implements `SQLStorage` for saving to a MySQL database

4. **main.py**
   - Command-line interface to the application
   - Processes files and directs output to chosen storage method

## How to Run

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Assignment3-Python
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### Basic Usage (File Storage)
To process files and store output to the filesystem:

```bash
python main.py --files sample.pdf sample.docx sample.pptx
```

This will extract content from the specified files and save it to the `output` directory.

#### Using MySQL Storage
To store the extracted data in a MySQL database:

```bash
python main.py --files sample.pdf sample.docx sample.pptx --sql --sql-user root --sql-password your_password
```

#### Command-Line Options

- `--files`: List of files to process (default: sample.pdf, sample.docx, sample.pptx)
- `--sql`: Store data in MySQL database instead of files
- `--sql-host`: MySQL server host (default: localhost)
- `--sql-user`: MySQL user (default: root)
- `--sql-password`: MySQL password
- `--sql-db`: MySQL database name (default: document_extractor)
- `--output-dir`: Output directory for extracted data (default: output)

### Setting Up MySQL

1. Install MySQL if not already installed:
   ```bash
   sudo apt-get install mysql-server   # For Ubuntu/Debian
   ```

2. Start the MySQL service:
   ```bash
   sudo service mysql start
   ```

3. Create a database (optional, the application will create one if it doesn't exist):
   ```bash
   mysql -u root -p
   CREATE DATABASE document_extractor;
   EXIT;
   ```

4. Run the application with MySQL storage:
   ```bash
   python main.py --sql --sql-user root --sql-password your_password
   ```

## Running Unit Tests

### Running All Tests
To run all unit tests at once:

```bash
python run_tests.py
```

### Running Individual Test Modules
To run specific test modules:

```bash
python -m unittest tests.test_file_loader
python -m unittest tests.test_data_extractor
python -m unittest tests.test_storage
```

## Summary

This project demonstrates a modular approach to extracting content from different document types. Key features include:

1. **Object-Oriented Design**: Uses abstract classes and inheritance to create a flexible and extensible architecture.

2. **Multiple File Type Support**: Handles PDF, DOCX, and PPTX files with a unified interface.

3. **Comprehensive Extraction**: Extracts text with formatting information, hyperlinks, images, and tables.

4. **Multiple Storage Options**: Allows storing data in files (CSV/JSON) or in a MySQL database.

5. **Robust Error Handling**: Includes defensive programming techniques to handle various edge cases and file formats.

The system is designed to be easily extended to support additional file types or storage methods in the future by implementing new concrete classes that conform to the existing abstract interfaces.
