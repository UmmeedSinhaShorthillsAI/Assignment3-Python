import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock

# Import the modules to test
from file_loader import FileLoader, PDFLoader, DOCXLoader, PPTLoader


class TestFileLoader(unittest.TestCase):
    """Simple unit tests for FileLoader classes"""
    
    def setUp(self):
        """Set up test environment with temporary files"""
        # Create temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create sample test file paths - we won't actually create the files
        # because we'll mock the file loading functions
        self.pdf_path = os.path.join(self.temp_dir.name, "test.pdf")
        self.docx_path = os.path.join(self.temp_dir.name, "test.docx")
        self.pptx_path = os.path.join(self.temp_dir.name, "test.pptx")
        
        # Create only the PDF file (since it's easier to mock)
        open(self.pdf_path, 'w').close()
        
        # Create directories that will make the path validation pass
        # but we won't actually write files as we'll mock the loading
        os.makedirs(os.path.dirname(self.docx_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.pptx_path), exist_ok=True)
    
    def tearDown(self):
        """Clean up temporary files"""
        self.temp_dir.cleanup()
    
    def test_file_loader_validate_file(self):
        """Test file validation in FileLoader"""
        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            PDFLoader(os.path.join(self.temp_dir.name, "nonexistent.pdf"))
        
        # Test with incorrect extension
        with self.assertRaises(ValueError):
            PDFLoader(self.docx_path)
        
        # Test with correct file
        pdf_loader = PDFLoader(self.pdf_path)
        self.assertEqual(pdf_loader.file_path, self.pdf_path)
        self.assertEqual(pdf_loader.file_extension, ".pdf")
    
    @patch('fitz.open')
    @patch('pdfplumber.open')
    def test_pdf_loader(self, mock_plumber_open, mock_fitz_open):
        """Test PDFLoader functionality"""
        # Setup mocks
        mock_fitz_doc = MagicMock()
        mock_plumber_doc = MagicMock()
        mock_fitz_open.return_value = mock_fitz_doc
        mock_plumber_open.return_value = mock_plumber_doc
        
        # Test loader
        loader = PDFLoader(self.pdf_path)
        result = loader.load_file()
        
        # Check that the PDF libraries were called
        mock_fitz_open.assert_called_once_with(self.pdf_path)
        mock_plumber_open.assert_called_once_with(self.pdf_path)
        
        # Check returned data structure
        self.assertEqual(result["fitz_doc"], mock_fitz_doc)
        self.assertEqual(result["plumber_doc"], mock_plumber_doc)
        self.assertEqual(result["file_name"], "test.pdf")
    
    def test_docx_loader(self):
        """Test DOCXLoader functionality"""
        # Instead of creating a real file and loading it, patch the validation
        # and the load_file method directly
        with patch('os.path.exists') as mock_exists, \
             patch('docx.Document') as mock_document:
            
            # Setup mocks
            mock_exists.return_value = True  # Make file validation pass
            mock_doc = MagicMock()
            mock_document.return_value = mock_doc
            
            # Test loader
            loader = DOCXLoader(self.docx_path)
            
            # Set file_exists to True manually to bypass validation
            loader.validate_file = MagicMock()  # Override validation
            
            result = loader.load_file()
            
            # Check that the DOCX library was called
            mock_document.assert_called_once_with(self.docx_path)
            
            # Check returned data structure
            self.assertEqual(result["doc"], mock_doc)
            self.assertEqual(result["file_name"], "test.docx")
    
    def test_ppt_loader(self):
        """Test PPTLoader functionality"""
        # Instead of creating a real file and loading it, patch the validation
        # and the load_file method directly
        with patch('os.path.exists') as mock_exists, \
             patch('pptx.Presentation') as mock_presentation:
            
            # Setup mocks
            mock_exists.return_value = True  # Make file validation pass
            mock_ppt = MagicMock()
            mock_presentation.return_value = mock_ppt
            
            # Test loader
            loader = PPTLoader(self.pptx_path)
            
            # Set file_exists to True manually to bypass validation
            loader.validate_file = MagicMock()  # Override validation
            
            result = loader.load_file()
            
            # Check that the PPTX library was called
            mock_presentation.assert_called_once_with(self.pptx_path)
            
            # Check returned data structure
            self.assertEqual(result["presentation"], mock_ppt)
            self.assertEqual(result["file_name"], "test.pptx")


if __name__ == '__main__':
    unittest.main()