import re
import difflib
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class CodePatcher:
    """Handles targeted code changes using diff-based patching"""
    
    def __init__(self):
        self.backup_dir = Path(".code_analyzer_backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def apply_targeted_changes(self, file_path: Path, ai_suggestions: str) -> Dict[str, any]:
        """
        Apply targeted changes to a file based on AI suggestions
        
        Args:
            file_path: Path to the file to modify
            ai_suggestions: AI response containing code suggestions
            
        Returns:
            Dict containing:
            - success: bool
            - changes_applied: List of applied changes
            - backup_path: Path to backup file
            - error: Error message if any
        """
        try:
            # Create backup
            backup_path = self._create_backup(file_path)
            
            # Parse AI suggestions for targeted changes
            changes = self._parse_ai_suggestions(ai_suggestions)
            
            if not changes:
                return {
                    'success': False,
                    'changes_applied': [],
                    'backup_path': backup_path,
                    'error': 'No valid changes found in AI suggestions'
                }
            
            # Read original file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
            
            # Apply changes
            modified_lines = original_lines.copy()
            applied_changes = []
            
            for change in changes:
                result = self._apply_single_change(modified_lines, change)
                if result['success']:
                    applied_changes.append(result)
                    modified_lines = result['new_lines']
                else:
                    print(f"Warning: Failed to apply change: {result['error']}")
            
            # Write modified content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(modified_lines)
            
            return {
                'success': True,
                'changes_applied': applied_changes,
                'backup_path': backup_path,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'changes_applied': [],
                'backup_path': None,
                'error': f'Error applying changes: {str(e)}'
            }
    
    def _create_backup(self, file_path: Path) -> Path:
        """Create a backup of the original file"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        with open(file_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        
        return backup_path
    
    def _parse_ai_suggestions(self, ai_suggestions: str) -> List[Dict]:
        """
        Parse AI suggestions to extract targeted changes
        
        Expected formats:
        1. Function replacement: "Replace function X with: ..."
        2. Line changes: "Change line X to: ..."
        3. Block changes: "Replace lines X-Y with: ..."
        4. Insertions: "Add after line X: ..."
        """
        changes = []
        
        # Look for code blocks in the AI response
        code_blocks = self._extract_code_blocks(ai_suggestions)
        
        for block in code_blocks:
            # Try to parse context from surrounding text
            context = self._extract_context(ai_suggestions, block)
            
            if context:
                change = {
                    'type': context['type'],
                    'target': context['target'],
                    'new_code': block['code'],
                    'language': block['language']
                }
                changes.append(change)
        
        return changes
    
    def _extract_code_blocks(self, text: str) -> List[Dict]:
        """Extract code blocks from AI response"""
        blocks = []
        
        # Pattern to match code blocks
        pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            language = match.group(1) or 'text'
            code = match.group(2)
            blocks.append({
                'language': language,
                'code': code
            })
        
        return blocks
    
    def _extract_context(self, text: str, code_block: Dict) -> Optional[Dict]:
        """Extract context about what the code block should replace"""
        # Look for common patterns in AI responses
        patterns = [
            # Function replacement
            r'replace\s+(?:the\s+)?function\s+(\w+)\s+with:?',
            r'update\s+(?:the\s+)?function\s+(\w+)\s+to:?',
            r'function\s+(\w+)\s+should\s+be:?',
            
            # Line changes
            r'change\s+line\s+(\d+)\s+to:?',
            r'update\s+line\s+(\d+)\s+to:?',
            r'line\s+(\d+)\s+should\s+be:?',
            
            # Block changes
            r'replace\s+lines?\s+(\d+)-(\d+)\s+with:?',
            r'update\s+lines?\s+(\d+)-(\d+)\s+to:?',
            
            # Insertions
            r'add\s+(?:after\s+)?line\s+(\d+):?',
            r'insert\s+(?:after\s+)?line\s+(\d+):?',
            
            # Method/class changes
            r'replace\s+(?:the\s+)?method\s+(\w+)\s+with:?',
            r'update\s+(?:the\s+)?class\s+(\w+)\s+to:?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'line' in pattern:
                    if '-' in match.group(0):
                        # Block change
                        return {
                            'type': 'block_replace',
                            'target': (int(match.group(1)), int(match.group(2)))
                        }
                    else:
                        # Single line change
                        return {
                            'type': 'line_replace',
                            'target': int(match.group(1))
                        }
                elif 'function' in pattern or 'method' in pattern:
                    return {
                        'type': 'function_replace',
                        'target': match.group(1)
                    }
                elif 'class' in pattern:
                    return {
                        'type': 'class_replace',
                        'target': match.group(1)
                    }
                elif 'add' in pattern or 'insert' in pattern:
                    return {
                        'type': 'insert_after',
                        'target': int(match.group(1))
                    }
        
        return None
    
    def _apply_single_change(self, lines: List[str], change: Dict) -> Dict:
        """Apply a single change to the lines"""
        try:
            if change['type'] == 'function_replace':
                return self._replace_function(lines, change['target'], change['new_code'])
            elif change['type'] == 'line_replace':
                return self._replace_line(lines, change['target'], change['new_code'])
            elif change['type'] == 'block_replace':
                return self._replace_block(lines, change['target'], change['new_code'])
            elif change['type'] == 'insert_after':
                return self._insert_after_line(lines, change['target'], change['new_code'])
            elif change['type'] == 'class_replace':
                return self._replace_class(lines, change['target'], change['new_code'])
            else:
                return {
                    'success': False,
                    'error': f'Unknown change type: {change["type"]}',
                    'new_lines': lines
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error applying change: {str(e)}',
                'new_lines': lines
            }
    
    def _replace_function(self, lines: List[str], function_name: str, new_code: str) -> Dict:
        """Replace a function with new code"""
        # Find function start and end
        start_line = None
        end_line = None
        indent_level = None
        
        # Look for function definition
        for i, line in enumerate(lines):
            if re.match(rf'\s*def\s+{function_name}\s*\(', line):
                start_line = i
                # Calculate indent level
                indent_level = len(line) - len(line.lstrip())
                break
        
        if start_line is None:
            return {
                'success': False,
                'error': f'Function {function_name} not found',
                'new_lines': lines
            }
        
        # Find function end (next function or end of file)
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':
                continue
            if len(line) - len(line.lstrip()) <= indent_level and line.strip():
                end_line = i
                break
        
        if end_line is None:
            end_line = len(lines)
        
        # Apply the change
        new_lines = lines[:start_line]
        new_lines.extend(new_code.splitlines(True))  # Keep line endings
        new_lines.extend(lines[end_line:])
        
        return {
            'success': True,
            'start_line': start_line,
            'end_line': end_line,
            'new_lines': new_lines
        }
    
    def _replace_line(self, lines: List[str], line_number: int, new_code: str) -> Dict:
        """Replace a single line"""
        if line_number < 1 or line_number > len(lines):
            return {
                'success': False,
                'error': f'Line {line_number} out of range',
                'new_lines': lines
            }
        
        new_lines = lines.copy()
        new_lines[line_number - 1] = new_code.rstrip() + '\n'
        
        return {
            'success': True,
            'start_line': line_number - 1,
            'end_line': line_number,
            'new_lines': new_lines
        }
    
    def _replace_block(self, lines: List[str], line_range: Tuple[int, int], new_code: str) -> Dict:
        """Replace a block of lines"""
        start, end = line_range
        if start < 1 or end > len(lines) or start > end:
            return {
                'success': False,
                'error': f'Invalid line range: {start}-{end}',
                'new_lines': lines
            }
        
        new_lines = lines[:start - 1]
        new_lines.extend(new_code.splitlines(True))
        new_lines.extend(lines[end:])
        
        return {
            'success': True,
            'start_line': start - 1,
            'end_line': end,
            'new_lines': new_lines
        }
    
    def _insert_after_line(self, lines: List[str], line_number: int, new_code: str) -> Dict:
        """Insert code after a specific line"""
        if line_number < 1 or line_number > len(lines):
            return {
                'success': False,
                'error': f'Line {line_number} out of range',
                'new_lines': lines
            }
        
        new_lines = lines[:line_number]
        new_lines.extend(new_code.splitlines(True))
        new_lines.extend(lines[line_number:])
        
        return {
            'success': True,
            'start_line': line_number,
            'end_line': line_number,
            'new_lines': new_lines
        }
    
    def _replace_class(self, lines: List[str], class_name: str, new_code: str) -> Dict:
        """Replace a class with new code"""
        # Find class start and end
        start_line = None
        end_line = None
        indent_level = None
        
        # Look for class definition
        for i, line in enumerate(lines):
            if re.match(rf'\s*class\s+{class_name}\s*[\(:]', line):
                start_line = i
                # Calculate indent level
                indent_level = len(line) - len(line.lstrip())
                break
        
        if start_line is None:
            return {
                'success': False,
                'error': f'Class {class_name} not found',
                'new_lines': lines
            }
        
        # Find class end (next class or end of file)
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':
                continue
            if len(line) - len(line.lstrip()) <= indent_level and line.strip():
                end_line = i
                break
        
        if end_line is None:
            end_line = len(lines)
        
        # Apply the change
        new_lines = lines[:start_line]
        new_lines.extend(new_code.splitlines(True))
        new_lines.extend(lines[end_line:])
        
        return {
            'success': True,
            'start_line': start_line,
            'end_line': end_line,
            'new_lines': new_lines
        }
    
    def create_diff_preview(self, original_lines: List[str], modified_lines: List[str]) -> str:
        """Create a diff preview showing what will be changed"""
        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile='Original',
            tofile='Modified',
            lineterm=''
        )
        return '\n'.join(diff)
    
    def restore_backup(self, backup_path: Path, target_path: Path) -> bool:
        """Restore a file from backup"""
        try:
            with open(backup_path, 'r', encoding='utf-8') as src:
                with open(target_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False 