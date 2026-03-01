"""
Utility functions for the coding agent.
"""

import re
from typing import Dict, List, Optional


def detect_language(code: str) -> str:
    """
    Detect programming language from code snippet
    
    Args:
        code: Code snippet
    
    Returns:
        Detected language (csharp, typescript, sql, or unknown)
    """
    code_lower = code.lower()
    
    # C# indicators
    csharp_patterns = [
        r'\bnamespace\b',
        r'\bpublic\s+class\b',
        r'\busing\s+System',
        r'\basync\s+Task\b',
        r'\bvar\s+\w+\s*=',
        r'\[HttpGet\]',
        r'\[ApiController\]'
    ]
    
    # TypeScript/Angular indicators
    typescript_patterns = [
        r'\bexport\s+(class|interface|function)\b',
        r'\bimport\s+.*from',
        r'@Component\(',
        r'@Injectable\(',
        r':\s*(string|number|boolean|any)\b',
        r'=>'
    ]
    
    # SQL indicators
    sql_patterns = [
        r'\bSELECT\b',
        r'\bFROM\b',
        r'\bWHERE\b',
        r'\bCREATE\s+(TABLE|PROCEDURE|VIEW)\b',
        r'\bINSERT\s+INTO\b',
        r'\bUPDATE\b.*\bSET\b'
    ]
    
    # Count matches
    csharp_score = sum(1 for pattern in csharp_patterns if re.search(pattern, code, re.IGNORECASE))
    typescript_score = sum(1 for pattern in typescript_patterns if re.search(pattern, code, re.IGNORECASE))
    sql_score = sum(1 for pattern in sql_patterns if re.search(pattern, code, re.IGNORECASE))
    
    # Determine language
    scores = {
        'csharp': csharp_score,
        'typescript': typescript_score,
        'sql': sql_score
    }
    
    max_score = max(scores.values())
    if max_score == 0:
        return 'unknown'
    
    return max(scores, key=scores.get)


def format_code(code: str, language: str) -> str:
    """
    Basic code formatting
    
    Args:
        code: Code to format
        language: Programming language
    
    Returns:
        Formatted code
    """
    # Remove extra blank lines
    lines = code.split('\n')
    formatted_lines = []
    prev_blank = False
    
    for line in lines:
        is_blank = line.strip() == ''
        if is_blank and prev_blank:
            continue
        formatted_lines.append(line)
        prev_blank = is_blank
    
    return '\n'.join(formatted_lines)


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from markdown-style text
    
    Args:
        text: Text containing code blocks
    
    Returns:
        List of dictionaries with 'language' and 'code' keys
    """
    # Pattern for markdown code blocks
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    code_blocks = []
    for lang, code in matches:
        code_blocks.append({
            'language': lang if lang else 'unknown',
            'code': code.strip()
        })
    
    return code_blocks


def validate_request(data: Dict, required_fields: List[str]) -> Optional[str]:
    """
    Validate API request data
    
    Args:
        data: Request data dictionary
        required_fields: List of required field names
    
    Returns:
        Error message if validation fails, None otherwise
    """
    if not isinstance(data, dict):
        return "Request body must be a JSON object"
    
    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"
        if not data[field]:
            return f"Field '{field}' cannot be empty"
    
    return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def count_lines(code: str) -> int:
    """
    Count number of lines in code
    
    Args:
        code: Code string
    
    Returns:
        Number of lines
    """
    return len(code.split('\n'))


def estimate_complexity(code: str) -> str:
    """
    Estimate code complexity (simple heuristic)
    
    Args:
        code: Code string
    
    Returns:
        Complexity level (low, medium, high)
    """
    lines = count_lines(code)
    
    # Count control structures
    control_patterns = [
        r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b',
        r'\bswitch\b', r'\btry\b', r'\bcatch\b'
    ]
    
    control_count = sum(
        len(re.findall(pattern, code, re.IGNORECASE))
        for pattern in control_patterns
    )
    
    # Simple heuristic
    if lines < 20 and control_count < 3:
        return 'low'
    elif lines < 50 and control_count < 8:
        return 'medium'
    else:
        return 'high'


def get_code_statistics(code: str) -> Dict[str, any]:
    """
    Get statistics about code
    
    Args:
        code: Code string
    
    Returns:
        Dictionary with statistics
    """
    lines = code.split('\n')
    
    return {
        'total_lines': len(lines),
        'non_empty_lines': len([l for l in lines if l.strip()]),
        'character_count': len(code),
        'estimated_complexity': estimate_complexity(code),
        'detected_language': detect_language(code)
    }


if __name__ == '__main__':
    # Test utilities
    sample_code = """
    using Microsoft.AspNetCore.Mvc;
    
    namespace MyApi.Controllers
    {
        [ApiController]
        [Route("api/[controller]")]
        public class ProductsController : ControllerBase
        {
            [HttpGet]
            public IActionResult GetAll()
            {
                return Ok(new { message = "Products retrieved" });
            }
        }
    }
    """
    
    print("Testing utilities...")
    print(f"\nDetected language: {detect_language(sample_code)}")
    print(f"\nCode statistics:")
    stats = get_code_statistics(sample_code)
    for key, value in stats.items():
        print(f"  {key}: {value}")
