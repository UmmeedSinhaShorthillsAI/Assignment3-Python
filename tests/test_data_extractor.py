import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock

# Import the module to test
from data_extractor import DataExtractor


class TestDataExtractor(unittest.TestCase):
    """Simple unit tests for DataExtractor class"""
    
    def setUp(self):
        """Set up test environment with mocked file loader"""
        # Create temp directory for image output
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = os.path.join(self.temp_dir.name, "images")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create mock file loader for PDF
        self.mock_pdf_loader = MagicMock()
        self.mock_pdf_loader.get_expected_extension.return_value = ".pdf"
        self.mock_pdf_loader.file_name = "test.pdf"
        
        # Mock PDF documents
        self.mock_fitz_doc = MagicMock()
        self.mock_plumber_doc = MagicMock()
        
        # Set up loader return value
        self.mock_pdf_loader.load_file.return_value = {
            "fitz_doc": self.mock_fitz_doc,
            "plumber_doc": self.mock_plumber_doc,
            "file_name": "test.pdf"
        }
        
        # Create mock file loader for DOCX
        self.mock_docx_loader = MagicMock()
        self.mock_docx_loader.get_expected_extension.return_value = ".docx"
        self.mock_docx_loader.file_name = "test.docx"
        
        # Mock DOCX document
        self.mock_doc = MagicMock()
        
        # Set up loader return value
        self.mock_docx_loader.load_file.return_value = {
            "doc": self.mock_doc,
            "file_name": "test.docx"
        }
        
        # Create mock file loader for PPTX
        self.mock_pptx_loader = MagicMock()
        self.mock_pptx_loader.get_expected_extension.return_value = ".pptx"
        self.mock_pptx_loader.file_name = "test.pptx"
        
        # Mock PPTX presentation
        self.mock_presentation = MagicMock()
        
        # Set up loader return value
        self.mock_pptx_loader.load_file.return_value = {
            "presentation": self.mock_presentation,
            "file_name": "test.pptx"
        }
    
    def tearDown(self):
        """Clean up temporary files"""
        self.temp_dir.cleanup()
    
    def test_extractor_initialization(self):
        """Test DataExtractor initialization"""
        extractor = DataExtractor(self.mock_pdf_loader)
        
        # Check file info was properly set
        self.assertEqual(extractor.file_name, "test.pdf")
        self.assertEqual(extractor.file_type, "pdf")
        self.assertEqual(extractor.file_data, {
            "fitz_doc": self.mock_fitz_doc,
            "plumber_doc": self.mock_plumber_doc,
            "file_name": "test.pdf"
        })
    
    def test_extract_text_pdf(self):
        """Test PDF text extraction"""
        # Setup mock page with text data
        mock_page = MagicMock()
        mock_page.get_text.return_value = {
            "blocks": [
                {
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Sample text",
                                    "font": "Arial",
                                    "size": 12,
                                    "color": "#000000"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Make fitz_doc iterable and return our mock page
        self.mock_fitz_doc.__iter__.return_value = [mock_page]
        
        # Create extractor and call method
        extractor = DataExtractor(self.mock_pdf_loader)
        result = extractor.extract_text()
        
        # Check result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["text"], "Sample text")
        self.assertEqual(result[0]["font"], "Arial")
        self.assertEqual(result[0]["file_type"], "pdf")
    
    def test_extract_text_docx(self):
        """Test DOCX text extraction"""
        # Setup mock paragraph and run
        mock_para = MagicMock()
        mock_run = MagicMock()
        mock_run.text = "Sample DOCX text"
        mock_run.bold = True
        mock_run.italic = False
        
        mock_para.runs = [mock_run]
        mock_para.style.name = "Heading 1"
        mock_para.text = "Sample DOCX text"
        
        # Set paragraphs in mock document
        self.mock_doc.paragraphs = [mock_para]
        
        # Create extractor and call method
        extractor = DataExtractor(self.mock_docx_loader)
        result = extractor.extract_text()
        
        # Check result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["text"], "Sample DOCX text")
        self.assertEqual(result[0]["is_bold"], True)
        self.assertEqual(result[0]["is_heading"], True)
        self.assertEqual(result[0]["file_type"], "docx")
    
    def test_extract_text_pptx(self):
        """Test PPTX text extraction"""
        # Setup mock slide and shape
        mock_slide = MagicMock()
        mock_shape = MagicMock()
        mock_shape.text = "Sample PPTX text"
        mock_shape.name = "Title 1"
        
        # Set shapes in mock slide
        mock_slide.shapes = [mock_shape]
        
        # Set slides in mock presentation
        self.mock_presentation.slides = [mock_slide]
        
        # Create extractor and call method
        extractor = DataExtractor(self.mock_pptx_loader)
        result = extractor.extract_text()
        
        # Check result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["text"], "Sample PPTX text")
        self.assertEqual(result[0]["slide_number"], 1)
        self.assertEqual(result[0]["file_type"], "pptx")
    
    @patch('PIL.Image.open')
    def test_extract_images(self, mock_image_open):
        """Test image extraction functionality"""
        # Setup mock image
        mock_img = MagicMock()
        mock_img.size = (100, 50)
        mock_image_open.return_value = mock_img
        
        # Setup mock PDF page with image
        mock_page = MagicMock()
        mock_page.get_images.return_value = [(1, 0, 0, 0, 0, 0, 0)]  # Sample image info
        
        # Setup mock image extraction
        self.mock_fitz_doc.__iter__.return_value = [mock_page]
        self.mock_fitz_doc.extract_image.return_value = {
            "image": b"fake_image_data",
            "ext": "png"
        }
        
        # Create extractor and call method
        extractor = DataExtractor(self.mock_pdf_loader)
        
        # Use patch to avoid actual file writing
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            result = extractor.extract_images(self.output_dir)
        
        # Check result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["width"], 100)
        self.assertEqual(result[0]["height"], 50)
        self.assertEqual(result[0]["format"], "png")
        self.assertEqual(result[0]["file_type"], "pdf")


if __name__ == '__main__':
    unittest.main()