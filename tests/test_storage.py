import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open

# Import the module to test
from storage import FileStorage, SQLStorage


class TestFileStorage(unittest.TestCase):
    """Simple unit tests for FileStorage class"""
    
    def setUp(self):
        """Set up test environment with mock data extractor"""
        # Create temp directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = os.path.join(self.temp_dir.name, "output")
        
        # Create mock data extractor
        self.mock_extractor = MagicMock()
        self.mock_extractor.file_type = "pdf"
        self.mock_extractor.file_name = "test.pdf"
        
        # Set up sample data for each extraction method
        self.mock_extractor.extract_text.return_value = [
            {
                "page_number": 1,
                "text": "Sample text",
                "font": "Arial",
                "file_type": "pdf",
                "file_name": "test.pdf"
            }
        ]
        
        self.mock_extractor.extract_links.return_value = [
            {
                "page_number": 1,
                "url": "https://example.com",
                "linked_text": "Example",
                "file_type": "pdf",
                "file_name": "test.pdf"
            }
        ]
        
        self.mock_extractor.extract_images.return_value = [
            {
                "page_number": 1,
                "width": 100,
                "height": 50,
                "format": "png",
                "file_path": "/path/to/image.png",
                "file_type": "pdf",
                "file_name": "test.pdf"
            }
        ]
        
        self.mock_extractor.extract_tables.return_value = [
            {
                "page_number": 1,
                "rows": 2,
                "columns": 2,
                "content": [["Header1", "Header2"], ["Data1", "Data2"]],
                "file_type": "pdf",
                "file_name": "test.pdf"
            }
        ]
        
        # Create storage instance
        self.storage = FileStorage(self.mock_extractor, output_dir=self.output_dir)
    
    def tearDown(self):
        """Clean up temporary files"""
        self.temp_dir.cleanup()
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('csv.DictWriter')
    def test_store_text(self, mock_csv_writer, mock_json_dump, mock_open):
        """Test storing text data to files"""
        # Call method
        self.storage.store_text()
        
        # Check that files were opened for writing
        expected_csv_path = os.path.join(self.output_dir, "text", "pdf_test_text.csv")
        expected_json_path = os.path.join(self.output_dir, "text", "pdf_test_text.json")
        
        # Verify open calls (at least 2 for CSV and JSON)
        self.assertTrue(mock_open.call_count >= 2)
        
        # Verify extractor was called
        self.mock_extractor.extract_text.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open)
    def test_store_tables(self, mock_open):
        """Test storing table data to files"""
        # Call method
        self.storage.store_tables()
        
        # Check that the extractor was called
        self.mock_extractor.extract_tables.assert_called_once()
        
        # Verify open was called multiple times (table data + metadata)
        self.assertTrue(mock_open.call_count >= 2)
    
    def test_store_all(self):
        """Test storing all data types at once"""
        # Replace methods with mocks to verify calls
        self.storage.store_text = MagicMock()
        self.storage.store_links = MagicMock()
        self.storage.store_images = MagicMock()
        self.storage.store_tables = MagicMock()
        
        # Call store_all
        self.storage.store_all()
        
        # Verify that all storage methods were called once
        self.storage.store_text.assert_called_once()
        self.storage.store_links.assert_called_once()
        self.storage.store_images.assert_called_once()
        self.storage.store_tables.assert_called_once()


class TestSQLStorage(unittest.TestCase):
    """Simple unit tests for SQLStorage class"""
    
    def setUp(self):
        """Set up test environment with mock data extractor"""
        # Create mock data extractor (same as for FileStorage)
        self.mock_extractor = MagicMock()
        self.mock_extractor.file_type = "pdf"
        self.mock_extractor.file_name = "test.pdf"
        
        # Set up sample data
        self.mock_extractor.extract_text.return_value = [
            {
                "page_number": 1,
                "text": "Sample text",
                "font": "Arial",
                "file_type": "pdf",
                "file_name": "test.pdf"
            }
        ]
        
        self.mock_extractor.extract_links.return_value = [
            {
                "page_number": 1,
                "url": "https://example.com",
                "linked_text": "Example",
                "file_type": "pdf",
                "file_name": "test.pdf"
            }
        ]
        
        self.mock_extractor.extract_images.return_value = [
            {
                "page_number": 1,
                "width": 100,
                "height": 50,
                "format": "png",
                "file_path": "/path/to/image.png",
                "file_type": "pdf",
                "file_name": "test.pdf"
            }
        ]
        
        self.mock_extractor.extract_tables.return_value = [
            {
                "page_number": 1,
                "rows": 2,
                "columns": 2,
                "content": [["Header1", "Header2"], ["Data1", "Data2"]],
                "file_type": "pdf",
                "file_name": "test.pdf"
            }
        ]
    
    @patch('mysql.connector.connect')
    def test_sql_storage_initialization(self, mock_connect):
        """Test SQLStorage initialization and database creation"""
        # Create mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # Create storage instance
        storage = SQLStorage(
            self.mock_extractor,
            host="localhost",
            user="testuser",
            password="testpass",
            database="testdb"
        )
        
        # Verify database connection was attempted
        mock_connect.assert_called()
        
        # Verify database and tables were created
        self.assertTrue(mock_cursor.execute.call_count > 0)
    
    @patch('mysql.connector.connect')
    def test_store_text_sql(self, mock_connect):
        """Test storing text data to SQL database"""
        # Create mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # Create storage instance
        storage = SQLStorage(
            self.mock_extractor,
            host="localhost",
            user="testuser",
            password="testpass",
            database="testdb"
        )
        
        # Call store_text
        storage.store_text()
        
        # Verify that extractor was called
        self.mock_extractor.extract_text.assert_called_once()
        
        # Verify that SQL execution was performed
        self.assertTrue(mock_cursor.execute.call_count > 0)
        mock_connection.commit.assert_called()
    
    @patch('mysql.connector.connect')
    def test_clean_dict_for_sql(self, mock_connect):
        """Test cleaning dictionaries for SQL insertion"""
        # Create mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # Create storage instance
        storage = SQLStorage(
            self.mock_extractor,
            host="localhost",
            user="testuser",
            password="testpass",
            database="testdb"
        )
        
        # Test with sample data containing invalid keys
        test_data = {
            "file_name": "test.pdf",
            "text": "Sample text",
            "invalid_key": "This should be removed"
        }
        
        # Clean for text_data table
        result = storage._clean_dict_for_sql(test_data, "text_data")
        
        # Check that valid keys are kept and invalid ones removed
        self.assertIn("file_name", result)
        self.assertIn("text", result)
        self.assertNotIn("invalid_key", result)


if __name__ == '__main__':
    unittest.main()