from abc import ABC, abstractmethod
import os
import csv
import json
import mysql.connector
from mysql.connector import Error
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Storage(ABC):
    """Abstract base class for storing extracted data."""
    
    def __init__(self, data_extractor):
        """Initialize with a DataExtractor instance."""
        self.data_extractor = data_extractor
    
    @abstractmethod
    def store_text(self):
        """Store extracted text data."""
        pass
    
    @abstractmethod
    def store_links(self):
        """Store extracted hyperlink data."""
        pass
    
    @abstractmethod
    def store_images(self):
        """Store extracted image data."""
        pass
    
    @abstractmethod
    def store_tables(self):
        """Store extracted table data."""
        pass
    
    def store_all(self):
        """Store all extracted data types."""
        self.store_text()
        self.store_links()
        self.store_images()
        self.store_tables()


class FileStorage(Storage):
    """Concrete class to store extracted data to files."""
    
    def __init__(self, data_extractor, output_dir="output"):
        """Initialize with a DataExtractor instance and output directory."""
        super().__init__(data_extractor)
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create subdirectories for different data types
        self.text_dir = os.path.join(output_dir, "text")
        self.links_dir = os.path.join(output_dir, "links")
        self.images_dir = os.path.join(output_dir, "images")
        self.tables_dir = os.path.join(output_dir, "tables")
        
        for directory in [self.text_dir, self.links_dir, self.images_dir, self.tables_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Get file type from data_extractor
        self.file_type = data_extractor.file_type
        self.file_name = data_extractor.file_name.replace(f".{self.file_type}", "")
    
    def store_text(self):
        """Store extracted text data to CSV file."""
        text_data = self.data_extractor.extract_text()
        
        if not text_data:
            logger.info("No text data to store.")
            return
        
        # Create CSV file
        filename = f"{self.file_type}_{self.file_name}_text.csv"
        filepath = os.path.join(self.text_dir, filename)
        
        # Get all possible keys from the dicts
        all_keys = set()
        for item in text_data:
            all_keys.update(item.keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(text_data)
        
        logger.info(f"Stored {len(text_data)} text items to {filepath}")
        
        # Also save as JSON for easier processing
        json_filepath = os.path.join(self.text_dir, f"{self.file_type}_{self.file_name}_text.json")
        with open(json_filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(text_data, jsonfile, indent=2)
        
        return filepath
    
    def store_links(self):
        """Store extracted hyperlink data to CSV file."""
        links_data = self.data_extractor.extract_links()
        
        if not links_data:
            logger.info("No link data to store.")
            return
        
        # Create CSV file
        filename = f"{self.file_type}_{self.file_name}_links.csv"
        filepath = os.path.join(self.links_dir, filename)
        
        # Get all possible keys from the dicts
        all_keys = set()
        for item in links_data:
            all_keys.update(item.keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(links_data)
        
        logger.info(f"Stored {len(links_data)} links to {filepath}")
        
        # Also save as JSON for easier processing
        json_filepath = os.path.join(self.links_dir, f"{self.file_type}_{self.file_name}_links.json")
        with open(json_filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(links_data, jsonfile, indent=2)
        
        return filepath
    
    def store_images(self):
        """Store extracted image metadata to CSV file."""
        # Images are already saved to disk during extraction
        images_data = self.data_extractor.extract_images(self.images_dir)
        
        if not images_data:
            logger.info("No image data to store.")
            return
        
        # Create CSV file for image metadata
        filename = f"{self.file_type}_{self.file_name}_images.csv"
        filepath = os.path.join(self.images_dir, filename)
        
        # Get all possible keys from the dicts
        all_keys = set()
        for item in images_data:
            all_keys.update(item.keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(images_data)
        
        logger.info(f"Stored {len(images_data)} image metadata to {filepath}")
        
        # Also save as JSON for easier processing
        json_filepath = os.path.join(self.images_dir, f"{self.file_type}_{self.file_name}_images.json")
        with open(json_filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(images_data, jsonfile, indent=2)
        
        return filepath
    
    def store_tables(self):
        """Store extracted table data to CSV files."""
        tables_data = self.data_extractor.extract_tables()
        
        if not tables_data:
            logger.info("No table data to store.")
            return
        
        # Store each table to a separate CSV file
        table_filepaths = []
        
        for table_idx, table in enumerate(tables_data):
            # Create a unique identifier for the table
            if self.file_type == "pdf":
                table_id = f"page{table['page_number']}_table{table['table_index']}"
            elif self.file_type == "docx":
                table_id = f"table{table['table_index']}"
            else:  # pptx
                table_id = f"slide{table['slide_number']}_table{table['table_index']}"
            
            filename = f"{self.file_type}_{self.file_name}_{table_id}.csv"
            filepath = os.path.join(self.tables_dir, filename)
            
            # Write table content to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(table['content'])
            
            table_filepaths.append(filepath)
        
        # Create a metadata CSV for all tables
        metadata_filename = f"{self.file_type}_{self.file_name}_tables_metadata.csv"
        metadata_filepath = os.path.join(self.tables_dir, metadata_filename)
        
        # Clean table data by removing the actual content (saving space)
        metadata = []
        for table in tables_data:
            table_meta = table.copy()
            table_meta.pop("content", None)
            metadata.append(table_meta)
        
        # Get all possible keys from the dicts
        all_keys = set()
        for item in metadata:
            all_keys.update(item.keys())
        
        with open(metadata_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(metadata)
        
        logger.info(f"Stored {len(tables_data)} tables to {self.tables_dir}")
        
        # Also save table metadata as JSON for easier processing
        json_filepath = os.path.join(self.tables_dir, f"{self.file_type}_{self.file_name}_tables_metadata.json")
        with open(json_filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(metadata, jsonfile, indent=2)
        
        return table_filepaths


class SQLStorage(Storage):
    """Concrete class to store extracted data to a MySQL database."""
    
    def __init__(self, data_extractor, host="localhost", user="root", password="", database="document_extractor"):
        """Initialize with a DataExtractor instance and database connection parameters."""
        super().__init__(data_extractor)
        self.connection_params = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }
        
        # Connect to database
        self.connection = None
        try:
            self.connection = mysql.connector.connect(**self.connection_params)
            self.cursor = self.connection.cursor()
            
            # Connect to MySQL server first (without database)
            temp_connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password
            )
            temp_cursor = temp_connection.cursor()
            
            # Create database if it doesn't exist
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            temp_cursor.close()
            temp_connection.close()
            
            # Now connect to the database
            self.connection = mysql.connector.connect(**self.connection_params)
            self.cursor = self.connection.cursor()
            
            # Create tables if they don't exist
            self._create_tables()
            
            logger.info("Successfully connected to MySQL database")
        except Error as e:
            logger.error(f"Error connecting to MySQL database: {e}")
            raise
        
        # Get file details
        self.file_type = data_extractor.file_type
        self.file_name = data_extractor.file_name
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        # Create text table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS text_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_name VARCHAR(255),
                file_type VARCHAR(10),
                page_number INT,
                paragraph_index INT,
                slide_number INT,
                run_index INT,
                shape_index INT,
                text LONGTEXT,
                font VARCHAR(100),
                size FLOAT,
                is_bold BOOLEAN,
                is_italic BOOLEAN,
                is_heading BOOLEAN,
                heading_level INT,
                is_title BOOLEAN,
                shape_type VARCHAR(100),
                color VARCHAR(20)
            )
        """)
        
        # Create links table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS links_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_name VARCHAR(255),
                file_type VARCHAR(10),
                page_number INT,
                paragraph_index INT,
                slide_number INT,
                run_index INT,
                shape_index INT,
                link_index INT,
                url VARCHAR(2083),
                linked_text TEXT,
                rect TEXT
            )
        """)
        
        # Create images table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS images_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_name VARCHAR(255),
                file_type VARCHAR(10),
                page_number INT,
                slide_number INT,
                image_index INT,
                shape_index INT,
                rel_id VARCHAR(50),
                width INT,
                height INT,
                format VARCHAR(10),
                file_path VARCHAR(255)
            )
        """)
        
        # Create tables metadata table (using backticks around reserved words)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tables_metadata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_name VARCHAR(255),
                file_type VARCHAR(10),
                page_number INT,
                slide_number INT,
                table_index INT,
                `rows` INT,
                `columns` INT
            )
        """)
        
        # Create tables content table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tables_content (
                id INT AUTO_INCREMENT PRIMARY KEY,
                table_id INT,
                row_index INT,
                column_index INT,
                cell_content TEXT,
                FOREIGN KEY (table_id) REFERENCES tables_metadata(id) ON DELETE CASCADE
            )
        """)
        
        self.connection.commit()
    
    def _clean_dict_for_sql(self, data, table_name):
        """Remove keys that don't exist in the table schema."""
        if table_name == "text_data":
            allowed_keys = ["file_name", "file_type", "page_number", "paragraph_index", "slide_number", 
                           "run_index", "shape_index", "text", "font", "size", "is_bold", "is_italic", 
                           "is_heading", "heading_level", "is_title", "shape_type", "color"]
        elif table_name == "links_data":
            allowed_keys = ["file_name", "file_type", "page_number", "paragraph_index", "slide_number", 
                           "run_index", "shape_index", "link_index", "url", "linked_text", "rect"]
        elif table_name == "images_data":
            allowed_keys = ["file_name", "file_type", "page_number", "slide_number", "image_index", 
                           "shape_index", "rel_id", "width", "height", "format", "file_path"]
        elif table_name == "tables_metadata":
            allowed_keys = ["file_name", "file_type", "page_number", "slide_number", "table_index", 
                           "`rows`", "`columns`"]
        else:
            return data
        
        # Convert non-string rect to string
        if "rect" in data and isinstance(data["rect"], list):
            data["rect"] = str(data["rect"])
        
        return {k: v for k, v in data.items() if k in allowed_keys}
    
    def store_text(self):
        """Store extracted text data to database."""
        text_data = self.data_extractor.extract_text()
        
        if not text_data:
            logger.info("No text data to store in database.")
            return
        
        try:
            for item in text_data:
                # Clean data
                clean_item = self._clean_dict_for_sql(item, "text_data")
                
                # Generate dynamic SQL
                fields = ", ".join(clean_item.keys())
                placeholders = ", ".join(["%s"] * len(clean_item))
                
                query = f"INSERT INTO text_data ({fields}) VALUES ({placeholders})"
                self.cursor.execute(query, list(clean_item.values()))
            
            self.connection.commit()
            logger.info(f"Stored {len(text_data)} text items to database")
        except Error as e:
            logger.error(f"Error storing text data to database: {e}")
    
    def store_links(self):
        """Store extracted hyperlink data to database."""
        links_data = self.data_extractor.extract_links()
        
        if not links_data:
            logger.info("No link data to store in database.")
            return
        
        try:
            for item in links_data:
                # Clean data
                clean_item = self._clean_dict_for_sql(item, "links_data")
                
                # Generate dynamic SQL
                fields = ", ".join(clean_item.keys())
                placeholders = ", ".join(["%s"] * len(clean_item))
                
                query = f"INSERT INTO links_data ({fields}) VALUES ({placeholders})"
                self.cursor.execute(query, list(clean_item.values()))
            
            self.connection.commit()
            logger.info(f"Stored {len(links_data)} links to database")
        except Error as e:
            logger.error(f"Error storing links data to database: {e}")
    
    def store_images(self):
        """Store extracted image metadata to database."""
        # Images are saved to disk during extraction, store metadata to database
        images_dir = os.path.join("output", "images")
        images_data = self.data_extractor.extract_images(images_dir)
        
        if not images_data:
            logger.info("No image data to store in database.")
            return
        
        try:
            for item in images_data:
                # Clean data
                clean_item = self._clean_dict_for_sql(item, "images_data")
                
                # Generate dynamic SQL
                fields = ", ".join(clean_item.keys())
                placeholders = ", ".join(["%s"] * len(clean_item))
                
                query = f"INSERT INTO images_data ({fields}) VALUES ({placeholders})"
                self.cursor.execute(query, list(clean_item.values()))
            
            self.connection.commit()
            logger.info(f"Stored {len(images_data)} image metadata to database")
        except Error as e:
            logger.error(f"Error storing image data to database: {e}")
    
    def store_tables(self):
        """Store extracted table data to database."""
        tables_data = self.data_extractor.extract_tables()
        
        if not tables_data:
            logger.info("No table data to store in database.")
            return
        
        try:
            for table in tables_data:
                # Store table metadata
                table_meta = table.copy()
                table_content = table_meta.pop("content", [])
                
                # Clean metadata
                clean_meta = self._clean_dict_for_sql(table_meta, "tables_metadata")
                
                # Handle reserved words by renaming keys
                if "rows" in clean_meta:
                    clean_meta["`rows`"] = clean_meta.pop("rows")
                if "columns" in clean_meta:
                    clean_meta["`columns`"] = clean_meta.pop("columns")
                
                # Generate dynamic SQL for metadata
                fields = ", ".join(clean_meta.keys())
                placeholders = ", ".join(["%s"] * len(clean_meta))
                
                query = f"INSERT INTO tables_metadata ({fields}) VALUES ({placeholders})"
                self.cursor.execute(query, list(clean_meta.values()))
                
                # Get the inserted table id
                table_id = self.cursor.lastrowid
                
                # Store table content
                for row_idx, row in enumerate(table_content):
                    for col_idx, cell in enumerate(row):
                        self.cursor.execute("""
                            INSERT INTO tables_content (table_id, row_index, column_index, cell_content)
                            VALUES (%s, %s, %s, %s)
                        """, (table_id, row_idx, col_idx, str(cell)))
            
            self.connection.commit()
            logger.info(f"Stored {len(tables_data)} tables to database")
        except Error as e:
            logger.error(f"Error storing table data to database: {e}")
    
    def __del__(self):
        """Close database connection on object destruction."""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            logger.info("Database connection closed")