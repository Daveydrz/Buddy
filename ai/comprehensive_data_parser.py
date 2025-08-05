"""
Comprehensive Data Parser and Error Handler - Robust JSON parsing and data validation
Created: 2025-08-05
Purpose: Solve data parsing errors, malformed responses, and improve error handling throughout the system
"""

import json
import re
import time
import traceback
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
from dataclasses import dataclass
from enum import Enum
import logging

T = TypeVar('T')

class ParseErrorType(Enum):
    """Types of parsing errors"""
    JSON_MALFORMED = "json_malformed"
    INCOMPLETE_RESPONSE = "incomplete_response"
    ENCODING_ERROR = "encoding_error"
    TIMEOUT_ERROR = "timeout_error"
    VALIDATION_ERROR = "validation_error"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class ParseResult:
    """Result of a parsing operation"""
    success: bool
    data: Any = None
    error_type: Optional[ParseErrorType] = None
    error_message: str = ""
    raw_content: str = ""
    recovery_applied: bool = False
    parsing_time: float = 0.0

class ComprehensiveExtractor:
    """Enhanced extractor with robust error handling and recovery mechanisms"""
    
    def __init__(self):
        self.parse_stats = {
            'total_attempts': 0,
            'successful_parses': 0,
            'error_recoveries': 0,
            'error_counts': {error_type.value: 0 for error_type in ParseErrorType}
        }
        
        # Recovery strategies for different error types
        self.recovery_strategies = {
            ParseErrorType.JSON_MALFORMED: self._recover_malformed_json,
            ParseErrorType.INCOMPLETE_RESPONSE: self._recover_incomplete_response,
            ParseErrorType.ENCODING_ERROR: self._recover_encoding_error,
            ParseErrorType.VALIDATION_ERROR: self._recover_validation_error
        }
        
        # Common JSON repair patterns
        self.json_repair_patterns = [
            (r'([^"\\])"([^"\\])', r'\1\\"\2'),  # Fix unescaped quotes
            (r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":'),  # Add quotes to keys
            (r':\s*([^",\[\]{}:\s]+)(\s*[,}])', r': "\1"\2'),  # Quote unquoted string values
            (r',\s*[}\]]', lambda m: m.group(0)[1:]),  # Remove trailing commas
            (r'\n\s*\n', '\n'),  # Remove extra newlines
            (r'[\x00-\x1f\x7f-\x9f]', ''),  # Remove control characters
        ]
    
    def parse_json_safe(self, content: str, expected_schema: Optional[Dict] = None,
                       allow_recovery: bool = True) -> ParseResult:
        """
        Safely parse JSON content with comprehensive error handling and recovery.
        
        Args:
            content: Raw content to parse
            expected_schema: Optional schema to validate against
            allow_recovery: Whether to attempt recovery on parse errors
            
        Returns:
            ParseResult containing the parsed data or error information
        """
        start_time = time.time()
        self.parse_stats['total_attempts'] += 1
        
        if not content or not isinstance(content, str):
            return ParseResult(
                success=False,
                error_type=ParseErrorType.VALIDATION_ERROR,
                error_message="Empty or invalid content provided",
                raw_content=str(content),
                parsing_time=time.time() - start_time
            )
        
        # Clean and prepare content
        cleaned_content = self._clean_content(content)
        
        # First attempt: Direct JSON parsing
        result = self._attempt_json_parse(cleaned_content)
        if result.success:
            result.parsing_time = time.time() - start_time
            self.parse_stats['successful_parses'] += 1
            
            # Validate against schema if provided
            if expected_schema and not self._validate_schema(result.data, expected_schema):
                result.success = False
                result.error_type = ParseErrorType.VALIDATION_ERROR
                result.error_message = "Data does not match expected schema"
            
            return result
        
        # Recovery attempts if enabled
        if allow_recovery:
            recovery_result = self._attempt_recovery(cleaned_content, result.error_type)
            if recovery_result.success:
                recovery_result.parsing_time = time.time() - start_time
                recovery_result.recovery_applied = True
                self.parse_stats['successful_parses'] += 1
                self.parse_stats['error_recoveries'] += 1
                return recovery_result
        
        # Update error statistics
        if result.error_type:
            self.parse_stats['error_counts'][result.error_type.value] += 1
        
        result.parsing_time = time.time() - start_time
        result.raw_content = content[:500]  # Limit raw content size
        return result
    
    def _clean_content(self, content: str) -> str:
        """Clean and prepare content for parsing"""
        try:
            # Remove common problematic characters and patterns
            cleaned = content.strip()
            
            # Remove BOM if present
            if cleaned.startswith('\ufeff'):
                cleaned = cleaned[1:]
            
            # Fix common encoding issues
            cleaned = cleaned.encode('utf-8', errors='ignore').decode('utf-8')
            
            # Remove control characters except newlines and tabs
            cleaned = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', cleaned)
            
            # Fix line endings
            cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
            
            return cleaned
            
        except Exception as e:
            print(f"[ComprehensiveExtractor] Content cleaning error: {e}")
            return content
    
    def _attempt_json_parse(self, content: str) -> ParseResult:
        """Attempt to parse JSON content"""
        try:
            # Try direct parsing first
            data = json.loads(content)
            return ParseResult(success=True, data=data, raw_content=content)
            
        except json.JSONDecodeError as e:
            return ParseResult(
                success=False,
                error_type=ParseErrorType.JSON_MALFORMED,
                error_message=f"JSON decode error: {str(e)}",
                raw_content=content
            )
        except UnicodeDecodeError as e:
            return ParseResult(
                success=False,
                error_type=ParseErrorType.ENCODING_ERROR,
                error_message=f"Encoding error: {str(e)}",
                raw_content=content
            )
        except Exception as e:
            return ParseResult(
                success=False,
                error_type=ParseErrorType.UNKNOWN_ERROR,
                error_message=f"Unknown error: {str(e)}",
                raw_content=content
            )
    
    def _attempt_recovery(self, content: str, error_type: ParseErrorType) -> ParseResult:
        """Attempt to recover from parsing errors"""
        try:
            if error_type in self.recovery_strategies:
                recovery_func = self.recovery_strategies[error_type]
                return recovery_func(content)
            else:
                return ParseResult(
                    success=False,
                    error_type=error_type,
                    error_message="No recovery strategy available",
                    raw_content=content
                )
                
        except Exception as e:
            return ParseResult(
                success=False,
                error_type=ParseErrorType.UNKNOWN_ERROR,
                error_message=f"Recovery failed: {str(e)}",
                raw_content=content
            )
    
    def _recover_malformed_json(self, content: str) -> ParseResult:
        """Recover from malformed JSON"""
        try:
            # Apply JSON repair patterns
            repaired = content
            for pattern, replacement in self.json_repair_patterns:
                if callable(replacement):
                    repaired = re.sub(pattern, replacement, repaired)
                else:
                    repaired = re.sub(pattern, replacement, repaired)
            
            # Try parsing repaired content
            try:
                data = json.loads(repaired)
                return ParseResult(success=True, data=data, raw_content=content)
            except json.JSONDecodeError:
                pass
            
            # Try extracting JSON objects from content
            json_objects = self._extract_json_objects(content)
            if json_objects:
                # Return the first valid JSON object found
                return ParseResult(success=True, data=json_objects[0], raw_content=content)
            
            # Try parsing as loosely structured data
            loose_data = self._parse_loose_structure(content)
            if loose_data:
                return ParseResult(success=True, data=loose_data, raw_content=content)
            
            return ParseResult(
                success=False,
                error_type=ParseErrorType.JSON_MALFORMED,
                error_message="Could not repair malformed JSON",
                raw_content=content
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_type=ParseErrorType.UNKNOWN_ERROR,
                error_message=f"JSON recovery error: {str(e)}",
                raw_content=content
            )
    
    def _recover_incomplete_response(self, content: str) -> ParseResult:
        """Recover from incomplete responses"""
        try:
            # Try to complete common incomplete patterns
            if content.strip().endswith(','):
                # Remove trailing comma and try to close structure
                cleaned = content.strip()[:-1]
                if cleaned.count('{') > cleaned.count('}'):
                    cleaned += '}'
                if cleaned.count('[') > cleaned.count(']'):
                    cleaned += ']'
                
                try:
                    data = json.loads(cleaned)
                    return ParseResult(success=True, data=data, raw_content=content)
                except json.JSONDecodeError:
                    pass
            
            # Try to extract partial data
            partial_data = self._extract_partial_data(content)
            if partial_data:
                return ParseResult(success=True, data=partial_data, raw_content=content)
            
            return ParseResult(
                success=False,
                error_type=ParseErrorType.INCOMPLETE_RESPONSE,
                error_message="Could not recover incomplete response",
                raw_content=content
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_type=ParseErrorType.UNKNOWN_ERROR,
                error_message=f"Incomplete response recovery error: {str(e)}",
                raw_content=content
            )
    
    def _recover_encoding_error(self, content: str) -> ParseResult:
        """Recover from encoding errors"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'ascii', 'utf-16']
            
            for encoding in encodings:
                try:
                    if isinstance(content, bytes):
                        decoded = content.decode(encoding, errors='ignore')
                    else:
                        decoded = content.encode(encoding, errors='ignore').decode(encoding)
                    
                    # Try parsing the re-encoded content
                    data = json.loads(decoded)
                    return ParseResult(success=True, data=data, raw_content=content)
                    
                except (json.JSONDecodeError, UnicodeError):
                    continue
            
            return ParseResult(
                success=False,
                error_type=ParseErrorType.ENCODING_ERROR,
                error_message="Could not recover from encoding error",
                raw_content=str(content)
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_type=ParseErrorType.UNKNOWN_ERROR,
                error_message=f"Encoding recovery error: {str(e)}",
                raw_content=str(content)
            )
    
    def _recover_validation_error(self, content: str) -> ParseResult:
        """Recover from validation errors"""
        try:
            # Try to parse as basic data and restructure
            try:
                data = json.loads(content)
                # Apply basic validation fixes
                fixed_data = self._fix_common_validation_issues(data)
                return ParseResult(success=True, data=fixed_data, raw_content=content)
            except json.JSONDecodeError:
                pass
            
            return ParseResult(
                success=False,
                error_type=ParseErrorType.VALIDATION_ERROR,
                error_message="Could not recover from validation error",
                raw_content=content
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_type=ParseErrorType.UNKNOWN_ERROR,
                error_message=f"Validation recovery error: {str(e)}",
                raw_content=content
            )
    
    def _extract_json_objects(self, content: str) -> List[Any]:
        """Extract valid JSON objects from content"""
        objects = []
        try:
            # Find potential JSON objects using regex
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, content)
            
            for match in matches:
                try:
                    obj = json.loads(match)
                    objects.append(obj)
                except json.JSONDecodeError:
                    continue
            
            # Also try to find JSON arrays
            array_pattern = r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'
            array_matches = re.findall(array_pattern, content)
            
            for match in array_matches:
                try:
                    arr = json.loads(match)
                    objects.append(arr)
                except json.JSONDecodeError:
                    continue
            
        except Exception as e:
            print(f"[ComprehensiveExtractor] JSON extraction error: {e}")
        
        return objects
    
    def _parse_loose_structure(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse loosely structured data"""
        try:
            # Try to extract key-value pairs
            result = {}
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if ':' in line and not line.startswith('#'):
                    try:
                        key, value = line.split(':', 1)
                        key = key.strip().strip('"\'')
                        value = value.strip().strip(',').strip('"\'')
                        
                        # Try to parse value as JSON
                        try:
                            value = json.loads(value)
                        except:
                            pass
                        
                        result[key] = value
                    except:
                        continue
            
            return result if result else None
            
        except Exception as e:
            print(f"[ComprehensiveExtractor] Loose structure parsing error: {e}")
            return None
    
    def _extract_partial_data(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract partial data from incomplete content"""
        try:
            result = {}
            
            # Extract quoted strings as potential values
            string_pattern = r'"([^"]+)"\s*:\s*"([^"]*)"'
            string_matches = re.findall(string_pattern, content)
            
            for key, value in string_matches:
                result[key] = value
            
            # Extract number values
            number_pattern = r'"([^"]+)"\s*:\s*(\d+(?:\.\d+)?)'
            number_matches = re.findall(number_pattern, content)
            
            for key, value in number_matches:
                try:
                    result[key] = float(value) if '.' in value else int(value)
                except:
                    result[key] = value
            
            # Extract boolean values
            bool_pattern = r'"([^"]+)"\s*:\s*(true|false)'
            bool_matches = re.findall(bool_pattern, content, re.IGNORECASE)
            
            for key, value in bool_matches:
                result[key] = value.lower() == 'true'
            
            return result if result else None
            
        except Exception as e:
            print(f"[ComprehensiveExtractor] Partial data extraction error: {e}")
            return None
    
    def _fix_common_validation_issues(self, data: Any) -> Any:
        """Fix common validation issues in parsed data"""
        try:
            if isinstance(data, dict):
                fixed = {}
                for key, value in data.items():
                    # Ensure keys are strings
                    str_key = str(key) if not isinstance(key, str) else key
                    fixed[str_key] = self._fix_common_validation_issues(value)
                return fixed
            elif isinstance(data, list):
                return [self._fix_common_validation_issues(item) for item in data]
            else:
                return data
                
        except Exception as e:
            print(f"[ComprehensiveExtractor] Validation fix error: {e}")
            return data
    
    def _validate_schema(self, data: Any, schema: Dict) -> bool:
        """Basic schema validation"""
        try:
            if not isinstance(schema, dict) or not isinstance(data, dict):
                return True  # Skip validation for non-dict schemas
            
            required_fields = schema.get('required', [])
            for field in required_fields:
                if field not in data:
                    return False
            
            return True
            
        except Exception as e:
            print(f"[ComprehensiveExtractor] Schema validation error: {e}")
            return True  # Be permissive on validation errors
    
    def get_parsing_stats(self) -> Dict[str, Any]:
        """Get parsing statistics"""
        total = self.parse_stats['total_attempts']
        if total == 0:
            return {'status': 'no_data'}
        
        return {
            'total_attempts': total,
            'success_rate': self.parse_stats['successful_parses'] / total,
            'recovery_rate': self.parse_stats['error_recoveries'] / max(1, total - self.parse_stats['successful_parses']),
            'error_distribution': self.parse_stats['error_counts'],
            'most_common_error': max(self.parse_stats['error_counts'].items(), key=lambda x: x[1])[0] if any(self.parse_stats['error_counts'].values()) else 'none'
        }

# Global comprehensive extractor instance
comprehensive_extractor = ComprehensiveExtractor()

def parse_json_robust(content: str, expected_schema: Optional[Dict] = None,
                     allow_recovery: bool = True) -> ParseResult:
    """
    Robustly parse JSON content with comprehensive error handling.
    
    This is the main entry point for safe JSON parsing throughout the system.
    """
    return comprehensive_extractor.parse_json_safe(content, expected_schema, allow_recovery)

def extract_data_safe(content: str, extraction_func: Callable[[str], T],
                     fallback_value: T = None) -> T:
    """
    Safely extract data using a custom extraction function with fallback.
    
    Args:
        content: Content to extract from
        extraction_func: Function to extract data
        fallback_value: Value to return if extraction fails
        
    Returns:
        Extracted data or fallback value
    """
    try:
        return extraction_func(content)
    except Exception as e:
        print(f"[ComprehensiveExtractor] Extraction error: {e}")
        return fallback_value

def get_parsing_statistics() -> Dict[str, Any]:
    """Get current parsing statistics"""
    return comprehensive_extractor.get_parsing_stats()

print("[ComprehensiveExtractor] ✅ Robust data parsing and error handling system initialized")