import os
import csv
import json
from storage import Storage

class FileStorage(Storage):
    """
    Concrete implementation of Storage for file-based storage.
    """
    
    def __init__(self, data_extractor, output_dir="output"):
        """
        Initialize the file storage with a data extractor and output directory.
        
        Args:
            data_extractor: An instance of DataExtractor class.
            output_dir (str): Directory path for storing extracted data.
        """
        super().__init__(data_extractor)
        self.output_dir = output_dir
        self.images_dir = os.path.join(output_dir, "images")
        self._create_output_dirs()
    
    def _create_output_dirs(self):
        """Create the necessary output directories if they don't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
    
    def store_text(self, text_data):
        """
        Store extracted text data to a JSON file.
        
        Args:
            text_data (list): A list of dictionaries containing text and metadata.
        """
        if not text_data:
            print("No text data to store.")
            return
        
        # Get file type from the first item
        file_type = text_data[0]['file_type']
        file_name = text_data[0]['file_name'].split('.')[0]
        
        # Create a serializable version of the data (no bytes objects)
        serializable_data = []
        for item in text_data:
            serializable_item = item.copy()
            serializable_data.append(serializable_item)
        
        # Save to JSON file
        output_file = os.path.join(self.output_dir, f"{file_name}_{file_type}_text.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=4)
        
        print(f"Text data saved to {output_file}")
    
    def store_links(self, links_data):
        """
        Store extracted hyperlinks data to a CSV file.
        
        Args:
            links_data (list): A list of dictionaries containing hyperlinks and metadata.
        """
        if not links_data:
            print("No links data to store.")
            return
        
        # Get file type from the first item
        if links_data:
            file_type = links_data[0]['file_type']
            file_name = links_data[0]['file_name'].split('.')[0]
            
            # Define output file
            output_file = os.path.join(self.output_dir, f"{file_name}_{file_type}_links.csv")
            
            # Determine fieldnames
            if 'slide_number' in links_data[0]:
                fieldnames = ['slide_number', 'text', 'url', 'file_type', 'file_name']
            else:
                fieldnames = ['page_number', 'text', 'url', 'file_type', 'file_name']
                if 'in_table' in links_data[0]:
                    fieldnames.insert(3, 'in_table')
            
            # Write to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for link in links_data:
                    # Create a new dict with only the fields we want
                    row = {field: link.get(field, '') for field in fieldnames}
                    writer.writerow(row)
            
            print(f"Links data saved to {output_file}")
    
    def store_images(self, images_data):
        """
        Store extracted images to files and metadata to a CSV file.
        
        Args:
            images_data (list): A list of dictionaries containing images and metadata.
        """
        if not images_data:
            print("No images data to store.")
            return
        
        # Get file type from the first item
        file_type = images_data[0]['file_type']
        file_name = images_data[0]['file_name'].split('.')[0]
        
        # Define output CSV file for metadata
        metadata_file = os.path.join(self.output_dir, f"{file_name}_{file_type}_images.csv")
        
        # Determine fieldnames for metadata CSV
        if 'slide_number' in images_data[0]:
            fieldnames = ['slide_number', 'image_index', 'image_path', 'format', 'width', 'height', 'file_type', 'file_name']
        else:
            fieldnames = ['page_number', 'image_index', 'image_path', 'format', 'width', 'height', 'file_type', 'file_name']
        
        # Create a list to store rows for the CSV (with image paths)
        metadata_rows = []
        
        # Save each image and prepare metadata
        for img in images_data:
            # Create image filename
            if 'slide_number' in img:
                image_filename = f"{file_name}_{file_type}_slide{img['slide_number']}_img{img['image_index']}"
            else:
                image_filename = f"{file_name}_{file_type}_page{img.get('page_number', 0)}_img{img['image_index']}"
            
            # Add format if available
            if 'format' in img and img['format']:
                image_filename += f".{img['format']}"
            else:
                image_filename += ".png"  # Default format
            
            # Save image
            image_path = os.path.join(self.images_dir, image_filename)
            with open(image_path, 'wb') as f:
                f.write(img['image_data'])
            
            # Create metadata row
            metadata_row = {field: img.get(field, '') for field in fieldnames if field != 'image_path'}
            metadata_row['image_path'] = os.path.join("images", image_filename)
            metadata_rows.append(metadata_row)
        
        # Write metadata to CSV
        with open(metadata_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(metadata_rows)
        
        print(f"Images saved to {self.images_dir}")
        print(f"Image metadata saved to {metadata_file}")
    
    def store_tables(self, tables_data):
        """
        Store extracted tables to CSV files and metadata to a JSON file.
        
        Args:
            tables_data (list): A list of dictionaries containing tables and metadata.
        """
        if not tables_data:
            print("No tables data to store.")
            return
        
        # Get file type from the first item
        file_type = tables_data[0]['file_type']
        file_name = tables_data[0]['file_name'].split('.')[0]
        
        # Create a tables directory
        tables_dir = os.path.join(self.output_dir, "tables")
        os.makedirs(tables_dir, exist_ok=True)
        
        # Define output JSON file for metadata
        metadata_file = os.path.join(self.output_dir, f"{file_name}_{file_type}_tables.json")
        
        # Create a list to store metadata (with table paths)
        metadata_list = []
        
        # Save each table to a CSV and prepare metadata
        for i, table in enumerate(tables_data):
            # Create table filename
            if 'slide_number' in table:
                table_filename = f"{file_name}_{file_type}_slide{table['slide_number']}_table{table['table_index']}.csv"
            else:
                table_filename = f"{file_name}_{file_type}_page{table.get('page_number', 0)}_table{table['table_index']}.csv"
            
            # Save table data to CSV
            table_path = os.path.join(tables_dir, table_filename)
            with open(table_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in table['data']:
                    writer.writerow(row)
            
            # Create metadata
            metadata = {
                'table_index': table['table_index'],
                'file_type': table['file_type'],
                'file_name': table['file_name'],
                'rows': table['rows'],
                'columns': table['columns'],
                'table_path': os.path.join("tables", table_filename)
            }
            
            # Add page or slide number
            if 'page_number' in table:
                metadata['page_number'] = table['page_number']
            elif 'slide_number' in table:
                metadata['slide_number'] = table['slide_number']
            
            metadata_list.append(metadata)
        
        # Save metadata to JSON
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, ensure_ascii=False, indent=4)
        
        print(f"Tables saved to {tables_dir}")
        print(f"Table metadata saved to {metadata_file}")