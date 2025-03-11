#!/usr/bin/env python3
import os
import sys
import argparse
import logging
from file_loader import PDFLoader, DOCXLoader, PPTLoader
from data_extractor import DataExtractor
from storage import FileStorage, SQLStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_file_loader(file_path):
    """Create the appropriate file loader based on file extension."""
    extension = os.path.splitext(file_path)[1].lower()
    
    if extension == ".pdf":
        return PDFLoader(file_path)
    elif extension == ".docx":
        return DOCXLoader(file_path)
    elif extension == ".pptx":
        return PPTLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")


def process_file(file_path, use_sql=False, sql_host="localhost", sql_user="root", sql_password="", sql_db="document_extractor"):
    """Process a single file and extract its content."""
    try:
        # Create file loader
        file_loader = create_file_loader(file_path)
        
        # Create data extractor
        data_extractor = DataExtractor(file_loader)
        
        # Create storage and store all extracted data
        if use_sql:
            try:
                storage = SQLStorage(
                    data_extractor,
                    host=sql_host,
                    user=sql_user,
                    password=sql_password,
                    database=sql_db
                )
            except Exception as sql_error:
                logger.error(f"Error connecting to SQL database, falling back to file storage: {str(sql_error)}")
                logger.info("Using file storage as fallback")
                storage = FileStorage(data_extractor)
        else:
            storage = FileStorage(data_extractor)
        
        # Store all data
        storage.store_all()
        
        logger.info(f"Successfully processed file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        return False


def main():
    """Main function to parse arguments and process files."""
    parser = argparse.ArgumentParser(description="Extract content from PDF, DOCX, and PPTX files.")
    
    parser.add_argument(
        "--files",
        nargs="+",
        default=["sample.pdf", "sample.docx", "sample.pptx"],
        help="List of files to process (default: sample.pdf, sample.docx, sample.pptx)"
    )
    
    parser.add_argument(
        "--sql",
        action="store_true",
        help="Store data in MySQL database instead of files"
    )
    
    parser.add_argument(
        "--sql-host",
        default="localhost",
        help="MySQL server host (default: localhost)"
    )
    
    parser.add_argument(
        "--sql-user",
        default="root",
        help="MySQL user (default: root)"
    )
    
    parser.add_argument(
        "--sql-password",
        default="",
        help="MySQL password"
    )
    
    parser.add_argument(
        "--sql-db",
        default="document_extractor",
        help="MySQL database name (default: document_extractor)"
    )
    
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for extracted data (default: output)"
    )
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "images"), exist_ok=True)
    
    # Process each file
    success_count = 0
    for file_path in args.files:
        success = process_file(
            file_path,
            use_sql=args.sql,
            sql_host=args.sql_host,
            sql_user=args.sql_user,
            sql_password=args.sql_password,
            sql_db=args.sql_db
        )
        if success:
            success_count += 1
    
    logger.info(f"Processing complete. Successfully processed {success_count}/{len(args.files)} files.")


if __name__ == "__main__":
    main()