"""
Unit tests for the coding agent model and utilities.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from model import CodingAgentModel
from utils import (
    detect_language,
    format_code,
    extract_code_blocks,
    validate_request,
    count_lines,
    estimate_complexity,
    get_code_statistics
)


class TestLanguageDetection:
    """Tests for language detection"""
    
    def test_detect_csharp(self):
        code = """
        using Microsoft.AspNetCore.Mvc;
        
        [ApiController]
        public class ProductsController : ControllerBase
        {
            [HttpGet]
            public async Task<IActionResult> GetAll()
            {
                return Ok();
            }
        }
        """
        assert detect_language(code) == 'csharp'
    
    def test_detect_typescript(self):
        code = """
        import { Component } from '@angular/core';
        
        @Component({
            selector: 'app-root',
            template: '<h1>Hello</h1>'
        })
        export class AppComponent {
            title: string = 'My App';
        }
        """
        assert detect_language(code) == 'typescript'
    
    def test_detect_sql(self):
        code = """
        CREATE TABLE Products (
            Id INT PRIMARY KEY,
            Name NVARCHAR(100) NOT NULL
        );
        
        SELECT * FROM Products WHERE Price > 100;
        """
        assert detect_language(code) == 'sql'
    
    def test_detect_unknown(self):
        code = "hello world"
        assert detect_language(code) == 'unknown'


class TestCodeFormatting:
    """Tests for code formatting"""
    
    def test_remove_extra_blank_lines(self):
        code = "line1\n\n\nline2\n\n\n\nline3"
        formatted = format_code(code, 'csharp')
        # Should have at most one blank line between content
        assert '\n\n\n' not in formatted
    
    def test_preserve_content(self):
        code = "line1\nline2\nline3"
        formatted = format_code(code, 'csharp')
        assert 'line1' in formatted
        assert 'line2' in formatted
        assert 'line3' in formatted


class TestCodeBlockExtraction:
    """Tests for extracting code blocks"""
    
    def test_extract_single_block(self):
        text = """
        Here is some code:
        ```python
        def hello():
            print("Hello")
        ```
        """
        blocks = extract_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0]['language'] == 'python'
        assert 'def hello()' in blocks[0]['code']
    
    def test_extract_multiple_blocks(self):
        text = """
        ```javascript
        console.log("Hello");
        ```
        
        ```python
        print("Hello")
        ```
        """
        blocks = extract_code_blocks(text)
        assert len(blocks) == 2
        assert blocks[0]['language'] == 'javascript'
        assert blocks[1]['language'] == 'python'
    
    def test_extract_no_language(self):
        text = """
        ```
        some code
        ```
        """
        blocks = extract_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0]['language'] == 'unknown'


class TestRequestValidation:
    """Tests for request validation"""
    
    def test_valid_request(self):
        data = {'language': 'csharp', 'framework': 'dotnet8', 'task': 'Create controller'}
        error = validate_request(data, ['language', 'framework', 'task'])
        assert error is None
    
    def test_missing_field(self):
        data = {'language': 'csharp', 'framework': 'dotnet8'}
        error = validate_request(data, ['language', 'framework', 'task'])
        assert error is not None
        assert 'task' in error
    
    def test_empty_field(self):
        data = {'language': '', 'framework': 'dotnet8', 'task': 'Create controller'}
        error = validate_request(data, ['language', 'framework', 'task'])
        assert error is not None
        assert 'language' in error
    
    def test_invalid_type(self):
        data = "not a dict"
        error = validate_request(data, ['language'])
        assert error is not None
        assert 'JSON object' in error


class TestCodeStatistics:
    """Tests for code statistics"""
    
    def test_count_lines(self):
        code = "line1\nline2\nline3"
        assert count_lines(code) == 3
    
    def test_estimate_complexity_low(self):
        code = "var x = 1;\nvar y = 2;\nreturn x + y;"
        assert estimate_complexity(code) == 'low'
    
    def test_estimate_complexity_high(self):
        code = "\n".join([
            "if (condition) {",
            "  for (var i = 0; i < 10; i++) {",
            "    while (true) {",
            "      try {",
            "        switch (x) {",
            "          case 1: break;",
            "          case 2: break;",
            "        }",
            "      } catch (e) {}",
            "    }",
            "  }",
            "}"
        ] * 5)  # Repeat to increase lines
        assert estimate_complexity(code) == 'high'
    
    def test_get_statistics(self):
        code = "line1\nline2\n\nline3"
        stats = get_code_statistics(code)
        assert stats['total_lines'] == 4
        assert stats['non_empty_lines'] == 3
        assert 'character_count' in stats
        assert 'estimated_complexity' in stats
        assert 'detected_language' in stats


# Note: Model tests would require the trained model to be available
# These are placeholder tests for the model wrapper

class TestModelWrapper:
    """Tests for model wrapper (requires trained model)"""
    
    def test_model_loading_nonexistent(self):
        """Test that loading a non-existent model raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError) as excinfo:
            CodingAgentModel("/non/existent/path")
        assert "Model directory not found" in str(excinfo.value)

    @pytest.mark.skip(reason="Requires trained model")
    def test_model_loading(self):
        from model import CodingAgentModel
        current_dir = Path(__file__).parent
        model_path = (current_dir.parent / 'models' / 'best_model').resolve()
        model = CodingAgentModel(str(model_path))
        assert model is not None
    
    @pytest.mark.skip(reason="Requires trained model")
    def test_code_generation(self):
        from model import CodingAgentModel
        current_dir = Path(__file__).parent
        model_path = (current_dir.parent / 'models' / 'best_model').resolve()
        model = CodingAgentModel(str(model_path))
        code = model.generate(
            language='csharp',
            framework='dotnet8',
            task='Create a simple controller'
        )
        assert code is not None
        assert len(code) > 0


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
