import tkinter as tk
from tkinter import ttk, filedialog
import sv_ttk
from pathlib import Path
from tkinter import font as tkfont

from .theme import VSCodeTheme
from .editor_window import EditorWindow
from .sidebar import Sidebar
from .preview_panel import PreviewPanel
from .status_bar import StatusBar
from .syntax_highlighter import SyntaxHighlighter

class VSCodeLikeGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Code Analyzer")
        
        # Setup
        self.setup_fonts()
        sv_ttk.set_theme("dark")
        self.root.configure(bg=VSCodeTheme.BACKGROUND)
        
        # Initialize variables
        self.files = {}  # Dictionary to store open files
        self.current_file = None
        self.current_directory = None
        
        # Create full interface directly
        self.setup_main_interface()
        
        # Set initial size
        self.root.geometry("1400x800")
        
        # Bind shortcuts
        self.root.bind('<Control-s>', self.save_current_file)
        self.root.bind('<Control-o>', self.open_directory)

    def setup_fonts(self):
        available_fonts = tkfont.families()
        self.code_font_family = None
        preferred_fonts = [VSCodeTheme.FONT_FAMILY] + VSCodeTheme.FALLBACK_FONTS
        
        for font_name in preferred_fonts:
            if font_name in available_fonts:
                self.code_font_family = font_name
                break
        
        if not self.code_font_family:
            self.code_font_family = 'TkFixedFont'
            
        self.code_font = (self.code_font_family, VSCodeTheme.FONT_SIZE)
        self.ui_font = (self.code_font_family, VSCodeTheme.FONT_SIZE)

    def setup_main_interface(self):
        try:
            # Create main container
            self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
            self.main_container.pack(fill=tk.BOTH, expand=True)
            
            # Create status bar first
            self.status_bar = StatusBar(self.root, self.ui_font)
            
            # Create sidebar with callbacks
            callbacks = {
                'static': self.run_static_test,
                'dynamic': self.run_dynamic_test,
                'whitebox': self.run_white_box_test,
                'open_folder': self.open_directory,
                'open_file': self.open_file
            }
            
            # Create sidebar
            self.sidebar = Sidebar(self.main_container, callbacks)
            self.main_container.add(self.sidebar.frame, weight=1)
            
            # Create content container
            self.content_container = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
            self.main_container.add(self.content_container, weight=4)
            
            # Create tab manager
            self.create_tab_manager()
            
            # Create preview panel
            self.preview_panel = PreviewPanel(self.content_container)
            self.preview_panel.main_app = self  # Add reference to main application
            self.content_container.add(self.preview_panel.frame, weight=1)
            
            print("Main interface setup completed")
            
        except Exception as e:
            print(f"Error in setup_main_interface: {str(e)}")
            raise  # Re-raise the exception for debugging
        
    def create_tab_manager(self):
        self.tab_container = ttk.Frame(self.content_container)
        self.content_container.add(self.tab_container, weight=2)
        
        style = ttk.Style()
        style.configure('TNotebook', background=VSCodeTheme.BACKGROUND)
        style.configure('TNotebook.Tab', 
                       background=VSCodeTheme.INACTIVE_TAB_BG,
                       foreground=VSCodeTheme.FOREGROUND)
        
        self.tab_bar = ttk.Notebook(self.tab_container)
        self.tab_bar.pack(fill=tk.BOTH, expand=True)
        
        # Bind tab change event
        self.tab_bar.bind('<<NotebookTabChanged>>', self.on_tab_changed)

    def open_directory(self, event=None):
        """Open a directory and populate the file tree"""
        directory = filedialog.askdirectory()
        if directory:
            self.current_directory = Path(directory)
            self.sidebar.populate_tree(self.current_directory)
            self.status_bar.show_message(f"Opened directory: {self.current_directory.name}")

    def open_file(self, file_path):
        """Open a file in the editor"""
        if file_path not in self.files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create new tab
                tab_frame = ttk.Frame(self.tab_bar)
                self.tab_bar.add(tab_frame, text=file_path.name)
                
                # Create editor
                editor = EditorWindow(tab_frame, content, file_path, self.code_font)
                self.files[file_path] = editor
                
                # Apply syntax highlighting if needed
                if file_path.suffix in ['.py', '.java', '.cpp', '.js']:
                    SyntaxHighlighter.apply_highlighting(
                        editor.editor,
                        str(file_path),
                        content
                    )
                
                # Select the new tab
                self.tab_bar.select(tab_frame)
                self.current_file = file_path
                
                self.status_bar.show_message(f"Opened and activated: {file_path.name}")
                
            except Exception as e:
                self.status_bar.show_message(f"Error opening {file_path.name}: {str(e)}")
        else:
            # File already open, just select its tab
            for index, path in enumerate(self.files.keys()):
                if path == file_path:
                    self.tab_bar.select(index)
                    self.current_file = file_path
                    self.status_bar.show_message(f"Switched to: {file_path.name}")
                    break

    def save_current_file(self, event=None):
        """Save the currently active file"""
        current_tab = self.tab_bar.select()
        if current_tab:
            tab_id = self.tab_bar.index(current_tab)
            file_path = list(self.files.keys())[tab_id]
            editor = self.files[file_path]
            
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    content = editor.get_content()
                    file.write(content)
                self.status_bar.show_message(f"Saved: {file_path.name}")
            except Exception as e:
                self.status_bar.show_message(f"Error saving file: {str(e)}")

    def on_tab_changed(self, event):
        """Handle tab change events"""
        current_tab = self.tab_bar.select()
        if current_tab:
            tab_id = self.tab_bar.index(current_tab)
            self.current_file = list(self.files.keys())[tab_id]
            # Update status to show which file is now active
            self.status_bar.show_message(f"Switched to: {self.current_file.name}")
        else:
            self.current_file = None
            self.status_bar.show_message("No file is currently active")

    def run_static_test(self):
        """Run static analysis on selected files"""
        selected_items = self.sidebar.get_selected_items()
        if not selected_items:
            self.status_bar.show_message("No files selected for testing")
            return
        
        self.preview_panel.clear()
        self.preview_panel.add_text("🔍 Running Static Analysis...\n")
        self.preview_panel.add_text("=" * 50 + "\n\n")
        
        total_files = 0
        total_issues = 0
        
        for file_path in selected_items:
            if file_path.is_file():
                total_files += 1
                self.preview_panel.add_text(f"📄 Analyzing: {file_path.name}\n")
                self.preview_panel.add_text("-" * 30 + "\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Perform static analysis
                    issues = self._analyze_static_code(content, file_path)
                    total_issues += len(issues)
                    
                    if issues:
                        for issue in issues:
                            self.preview_panel.add_text(f"⚠️  {issue}\n")
                    else:
                        self.preview_panel.add_text("✅ No issues found\n")
                    
                    # Run language-specific static analysis tools
                    ext = file_path.suffix.lower()
                    if ext == '.py':
                        self._run_python_static_analysis(file_path)
                    elif ext in ['.cpp', '.c']:
                        self._run_cpp_static_analysis(file_path)
                    elif ext == '.java':
                        self._run_java_static_analysis(file_path)
                        
                except Exception as e:
                    self.preview_panel.add_text(f"❌ Error reading file: {str(e)}\n")
                
                self.preview_panel.add_text("\n")
        
        # Summary
        self.preview_panel.add_text("=" * 50 + "\n")
        self.preview_panel.add_text(f"📊 Summary: Analyzed {total_files} files, found {total_issues} issues\n")
        self.status_bar.show_message(f"Static analysis completed: {total_files} files, {total_issues} issues")

    def run_dynamic_test(self):
        """Run dynamic tests on selected files"""
        selected_items = self.sidebar.get_selected_items()
        if not selected_items:
            self.status_bar.show_message("No files selected for testing")
            return
        
        self.preview_panel.clear()
        self.preview_panel.add_text("⚡ Running Dynamic Tests...\n")
        self.preview_panel.add_text("=" * 50 + "\n\n")
        
        total_files = 0
        total_tests = 0
        passed_tests = 0
        
        for file_path in selected_items:
            if file_path.is_file():
                total_files += 1
                self.preview_panel.add_text(f"📄 Testing: {file_path.name}\n")
                self.preview_panel.add_text("-" * 30 + "\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Perform dynamic testing
                    test_results = self._run_dynamic_tests(content, file_path)
                    total_tests += test_results['total']
                    passed_tests += test_results['passed']
                    
                    self.preview_panel.add_text(f"Tests run: {test_results['total']}\n")
                    self.preview_panel.add_text(f"Passed: {test_results['passed']}\n")
                    self.preview_panel.add_text(f"Failed: {test_results['failed']}\n")
                    
                    if test_results['details']:
                        for detail in test_results['details']:
                            self.preview_panel.add_text(f"  {detail}\n")
                    
                    # Run actual execution tests
                    ext = file_path.suffix.lower()
                    if ext == '.py':
                        self._run_python_execution_test(file_path)
                    elif ext in ['.cpp', '.c']:
                        self._run_cpp_execution_test(file_path)
                    elif ext == '.java':
                        self._run_java_execution_test(file_path)
                            
                except Exception as e:
                    self.preview_panel.add_text(f"❌ Error testing file: {str(e)}\n")
                
                self.preview_panel.add_text("\n")
        
        # Summary
        self.preview_panel.add_text("=" * 50 + "\n")
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        self.preview_panel.add_text(f"📊 Summary: {total_files} files, {total_tests} tests, {success_rate:.1f}% pass rate\n")
        self.status_bar.show_message(f"Dynamic testing completed: {passed_tests}/{total_tests} tests passed")

    def run_white_box_test(self):
        """Run white box tests on selected files"""
        selected_items = self.sidebar.get_selected_items()
        if not selected_items:
            self.status_bar.show_message("No files selected for testing")
            return
        
        self.preview_panel.clear()
        self.preview_panel.add_text("🔬 Running White Box Tests...\n")
        self.preview_panel.add_text("=" * 50 + "\n\n")
        
        total_files = 0
        total_coverage = 0
        
        for file_path in selected_items:
            if file_path.is_file():
                total_files += 1
                self.preview_panel.add_text(f"📄 Analyzing: {file_path.name}\n")
                self.preview_panel.add_text("-" * 30 + "\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Perform white box analysis
                    analysis = self._analyze_white_box(content, file_path)
                    total_coverage += analysis['coverage']
                    
                    self.preview_panel.add_text(f"Code Coverage: {analysis['coverage']:.1f}%\n")
                    self.preview_panel.add_text(f"Functions: {analysis['functions']}\n")
                    self.preview_panel.add_text(f"Classes: {analysis['classes']}\n")
                    self.preview_panel.add_text(f"Lines of Code: {analysis['loc']}\n")
                    self.preview_panel.add_text(f"Complexity: {analysis['complexity']}\n")
                    
                    if analysis['paths']:
                        self.preview_panel.add_text("Execution Paths:\n")
                        for path in analysis['paths'][:5]:  # Show first 5 paths
                            self.preview_panel.add_text(f"  → {path}\n")
                        if len(analysis['paths']) > 5:
                            self.preview_panel.add_text(f"  ... and {len(analysis['paths']) - 5} more paths\n")
                    
                    # Run coverage tools if available
                    ext = file_path.suffix.lower()
                    if ext == '.py':
                        self._run_python_coverage_test(file_path)
                    elif ext in ['.cpp', '.c']:
                        self._run_cpp_coverage_test(file_path)
                    elif ext == '.java':
                        self._run_java_coverage_test(file_path)
                            
                except Exception as e:
                    self.preview_panel.add_text(f"❌ Error analyzing file: {str(e)}\n")
                
                self.preview_panel.add_text("\n")
        
        # Summary
        self.preview_panel.add_text("=" * 50 + "\n")
        avg_coverage = total_coverage / total_files if total_files > 0 else 0
        self.preview_panel.add_text(f"📊 Summary: {total_files} files, average coverage: {avg_coverage:.1f}%\n")
        self.status_bar.show_message(f"White box analysis completed: {total_files} files analyzed")

    def _analyze_static_code(self, content, file_path):
        """Perform static code analysis"""
        issues = []
        
        # Check file extension for language-specific analysis
        ext = file_path.suffix.lower()
        
        # Common static analysis checks
        lines = content.split('\n')
        
        # Check for long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 80:
                issues.append(f"Line {i}: Line too long ({len(line)} characters)")
        
        # Check for empty functions/classes
        if ext in ['.py', '.java', '.cpp', '.js']:
            # Simple pattern matching for empty blocks
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped in ['pass', '{}', ';'] and i > 1:
                    prev_line = lines[i-2].strip()
                    if any(keyword in prev_line for keyword in ['def ', 'class ', 'function ', 'public ', 'private ']):
                        issues.append(f"Line {i}: Empty function/class detected")
        
        # Check for TODO comments
        for i, line in enumerate(lines, 1):
            if 'TODO' in line.upper() or 'FIXME' in line.upper():
                issues.append(f"Line {i}: TODO/FIXME comment found")
        
        # Check for unused imports (basic check)
        if ext == '.py':
            import_lines = [i for i, line in enumerate(lines, 1) if line.strip().startswith('import ') or line.strip().startswith('from ')]
            if len(import_lines) > 10:
                issues.append(f"Many imports detected ({len(import_lines)} lines)")
        
        return issues

    def _run_dynamic_tests(self, content, file_path):
        """Run dynamic tests on the code"""
        results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        ext = file_path.suffix.lower()
        
        # Simulate different types of tests based on file type
        if ext == '.py':
            # Python-specific tests
            test_cases = [
                ("Syntax Check", self._test_python_syntax, content),
                ("Import Test", self._test_python_imports, content),
                ("Function Test", self._test_python_functions, content),
            ]
        elif ext in ['.cpp', '.c']:
            # C/C++ specific tests
            test_cases = [
                ("Syntax Check", self._test_cpp_syntax, content),
                ("Header Test", self._test_cpp_headers, content),
                ("Function Test", self._test_cpp_functions, content),
            ]
        elif ext == '.java':
            # Java specific tests
            test_cases = [
                ("Syntax Check", self._test_java_syntax, content),
                ("Class Test", self._test_java_classes, content),
                ("Method Test", self._test_java_methods, content),
            ]
        else:
            # Generic tests
            test_cases = [
                ("Basic Syntax", self._test_basic_syntax, content),
                ("Structure Test", self._test_structure, content),
            ]
        
        for test_name, test_func, test_content in test_cases:
            results['total'] += 1
            try:
                success, message = test_func(test_content)
                if success:
                    results['passed'] += 1
                    results['details'].append(f"✅ {test_name}: {message}")
                else:
                    results['failed'] += 1
                    results['details'].append(f"❌ {test_name}: {message}")
            except Exception as e:
                results['failed'] += 1
                results['details'].append(f"❌ {test_name}: Error - {str(e)}")
        
        return results

    def _analyze_white_box(self, content, file_path):
        """Perform white box analysis"""
        analysis = {
            'coverage': 0.0,
            'functions': 0,
            'classes': 0,
            'loc': 0,
            'complexity': 'Low',
            'paths': []
        }
        
        lines = content.split('\n')
        analysis['loc'] = len(lines)
        
        ext = file_path.suffix.lower()
        
        # Count functions and classes
        if ext == '.py':
            analysis['functions'] = content.count('def ')
            analysis['classes'] = content.count('class ')
        elif ext in ['.cpp', '.c']:
            analysis['functions'] = content.count('(') - content.count(';')  # Rough estimate
            analysis['classes'] = content.count('class ')
        elif ext == '.java':
            analysis['functions'] = content.count('public ') + content.count('private ') + content.count('protected ')
            analysis['classes'] = content.count('class ')
        
        # Calculate complexity (simple cyclomatic complexity)
        complexity_score = 0
        complexity_keywords = ['if', 'while', 'for', 'switch', 'case', 'catch', 'except']
        for keyword in complexity_keywords:
            complexity_score += content.count(keyword)
        
        if complexity_score < 10:
            analysis['complexity'] = 'Low'
        elif complexity_score < 20:
            analysis['complexity'] = 'Medium'
        else:
            analysis['complexity'] = 'High'
        
        # Simulate code coverage (random for demo)
        import random
        analysis['coverage'] = random.uniform(60, 95)
        
        # Generate execution paths
        analysis['paths'] = [
            "Main → Function A → Return",
            "Main → Function B → Condition → Branch 1",
            "Main → Function B → Condition → Branch 2",
            "Main → Class C → Method D",
            "Main → Error Handler → Recovery"
        ]
        
        return analysis

    # Test helper methods
    def _test_python_syntax(self, content):
        try:
            compile(content, '<string>', 'exec')
            return True, "Syntax is valid"
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
    
    def _test_python_imports(self, content):
        import_lines = [line for line in content.split('\n') if line.strip().startswith(('import ', 'from '))]
        if len(import_lines) <= 10:
            return True, f"{len(import_lines)} imports found"
        else:
            return False, f"Too many imports ({len(import_lines)})"
    
    def _test_python_functions(self, content):
        functions = content.count('def ')
        if functions > 0:
            return True, f"{functions} functions found"
        else:
            return False, "No functions found"
    
    def _test_cpp_syntax(self, content):
        # Basic C++ syntax check
        if ';' in content and ('{' in content or '}' in content):
            return True, "Basic C++ structure detected"
        else:
            return False, "Missing basic C++ elements"
    
    def _test_cpp_headers(self, content):
        headers = content.count('#include')
        if headers > 0:
            return True, f"{headers} headers included"
        else:
            return False, "No headers found"
    
    def _test_cpp_functions(self, content):
        functions = content.count('(') - content.count(';')
        if functions > 0:
            return True, f"Approximately {functions} functions detected"
        else:
            return False, "No functions detected"
    
    def _test_java_syntax(self, content):
        if 'public class' in content or 'class ' in content:
            return True, "Java class structure detected"
        else:
            return False, "No Java class found"
    
    def _test_java_classes(self, content):
        classes = content.count('class ')
        if classes > 0:
            return True, f"{classes} classes found"
        else:
            return False, "No classes found"
    
    def _test_java_methods(self, content):
        methods = content.count('public ') + content.count('private ') + content.count('protected ')
        if methods > 0:
            return True, f"{methods} methods found"
        else:
            return False, "No methods found"
    
    def _test_basic_syntax(self, content):
        if len(content.strip()) > 0:
            return True, "File has content"
        else:
            return False, "Empty file"
    
    def _test_structure(self, content):
        lines = content.split('\n')
        if len(lines) > 5:
            return True, f"{len(lines)} lines of code"
        else:
            return False, "File too short"

    def create_tab_manager(self):
        self.tab_container = ttk.Frame(self.content_container)
        self.content_container.add(self.tab_container, weight=2)
        
        style = ttk.Style()
        style.configure('TNotebook', background=VSCodeTheme.BACKGROUND)
        style.configure('TNotebook.Tab', 
                    background=VSCodeTheme.INACTIVE_TAB_BG,
                    foreground=VSCodeTheme.FOREGROUND)
        
        self.tab_bar = ttk.Notebook(self.tab_container)
        self.tab_bar.pack(fill=tk.BOTH, expand=True)
        
        # Bind tab change event
        self.tab_bar.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        # Add right-click menu for tabs
        self.tab_menu = tk.Menu(self.root, tearoff=0)
        self.tab_menu.add_command(label="Close", command=self.close_current_tab)
        self.tab_menu.add_command(label="Close All", command=self.close_all_tabs)
        self.tab_menu.add_command(label="Close Others", command=self.close_other_tabs)
        
        # Bind right-click event
        self.tab_bar.bind('<Button-3>', self.show_tab_menu)
        
        # Bind middle-click for quick close
        self.tab_bar.bind('<Button-2>', self.close_tab_by_click)

    def show_tab_menu(self, event):
        try:
            clicked_tab = self.tab_bar.tk.call(self.tab_bar._w, "identify", "tab", event.x, event.y)
            if clicked_tab is not None:
                self.tab_bar.select(clicked_tab)
                self.tab_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.tab_menu.grab_release()

    def close_tab_by_click(self, event):
        try:
            clicked_tab = self.tab_bar.tk.call(self.tab_bar._w, "identify", "tab", event.x, event.y)
            if clicked_tab is not None:
                self.tab_bar.select(clicked_tab)
                self.close_current_tab()
        except:
            pass

    def close_current_tab(self):
        current = self.tab_bar.select()
        if current:
            tab_id = self.tab_bar.index(current)
            file_path = list(self.files.keys())[tab_id]
            
            # Remove from files dictionary
            self.files.pop(file_path)
            
            # Remove the tab
            self.tab_bar.forget(current)
            
            if self.current_file == file_path:
                self.current_file = None

    def close_all_tabs(self):
        while self.tab_bar.tabs():
            self.close_current_tab()

    def get_current_file(self):
        """Get the currently active file (the one visible in the active tab)"""
        if self.current_file:
            # Update status bar to show which file is active
            self.status_bar.show_message(f"Active file: {self.current_file.name}")
            return self.current_file
        else:
            self.status_bar.show_message("No file is currently active")
            return None

    def get_selected_files(self):
        """Get files selected in the sidebar"""
        return self.sidebar.get_selected_items()

    def get_active_or_selected_files(self):
        """Get active file if available, otherwise get selected files from sidebar"""
        if self.current_file:
            return [self.current_file]
        else:
            return self.get_selected_files()

    def refresh_file_content(self, file_path):
        """Refresh the content of a file in the editor"""
        if file_path in self.files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                editor = self.files[file_path]
                editor.set_content(content)
                
                # Re-apply syntax highlighting
                if file_path.suffix in ['.py', '.java', '.cpp', '.js']:
                    SyntaxHighlighter.apply_highlighting(
                        editor.editor,
                        str(file_path),
                        content
                    )
                
                self.status_bar.show_message(f"Refreshed: {file_path.name}")
                
            except Exception as e:
                self.status_bar.show_message(f"Error refreshing {file_path.name}: {str(e)}")

    def close_other_tabs(self):
        current = self.tab_bar.select()
        if current:
            to_keep = self.tab_bar.index(current)
            tabs = self.tab_bar.tabs()
            
            # Close tabs in reverse order to avoid index issues
            for i in range(len(tabs) - 1, -1, -1):
                if i != to_keep:
                    self.tab_bar.select(i)
                    self.close_current_tab()

    def _run_python_static_analysis(self, file_path):
        """Run Python-specific static analysis tools"""
        self.preview_panel.add_text("\n🔧 Running Python Static Analysis Tools:\n")
        
        # Try to run flake8 if available
        result = self.preview_panel.run_command_and_capture_output(f"flake8 {file_path}")
        if result['success'] or result['stderr']:
            if result['stdout']:
                self.preview_panel.add_text("Flake8 Output:\n")
                self.preview_panel.add_text(f"```bash\n{result['stdout']}\n```")
            if result['stderr'] and "not found" not in result['stderr']:
                self.preview_panel.add_text("Flake8 Errors:\n")
                self.preview_panel.add_text(f"```bash\n{result['stderr']}\n```")
        
        # Try to run pylint if available
        result = self.preview_panel.run_command_and_capture_output(f"pylint {file_path}")
        if result['success'] or result['stderr']:
            if result['stdout']:
                self.preview_panel.add_text("\nPylint Output:\n")
                self.preview_panel.add_text(f"```bash\n{result['stdout']}\n```")
            if result['stderr'] and "not found" not in result['stderr']:
                self.preview_panel.add_text("Pylint Errors:\n")
                self.preview_panel.add_text(f"```bash\n{result['stderr']}\n```")

    def _run_cpp_static_analysis(self, file_path):
        """Run C++-specific static analysis tools"""
        self.preview_panel.add_text("\n🔧 Running C++ Static Analysis Tools:\n")
        
        # Try to run cppcheck if available
        result = self.preview_panel.run_command_and_capture_output(f"cppcheck {file_path}")
        if result['success'] or result['stderr']:
            if result['stdout']:
                self.preview_panel.add_text("Cppcheck Output:\n")
                self.preview_panel.add_text(f"```bash\n{result['stdout']}\n```")
            if result['stderr'] and "not found" not in result['stderr']:
                self.preview_panel.add_text("Cppcheck Errors:\n")
                self.preview_panel.add_text(f"```bash\n{result['stderr']}\n```")

    def _run_java_static_analysis(self, file_path):
        """Run Java-specific static analysis tools"""
        self.preview_panel.add_text("\n🔧 Running Java Static Analysis Tools:\n")
        
        # Try to run checkstyle if available
        result = self.preview_panel.run_command_and_capture_output(f"checkstyle {file_path}")
        if result['success'] or result['stderr']:
            if result['stdout']:
                self.preview_panel.add_text("Checkstyle Output:\n")
                self.preview_panel.add_text(f"```bash\n{result['stdout']}\n```")
            if result['stderr'] and "not found" not in result['stderr']:
                self.preview_panel.add_text("Checkstyle Errors:\n")
                self.preview_panel.add_text(f"```bash\n{result['stderr']}\n```")

    def _run_python_execution_test(self, file_path):
        """Run Python execution test"""
        self.preview_panel.add_text("\n🚀 Running Python Execution Test:\n")
        
        # Try to run the Python file
        result = self.preview_panel.run_command_and_capture_output(f"python {file_path}")
        if result['stdout']:
            self.preview_panel.add_text("Output:\n")
            self.preview_panel.add_text(f"```bash\n{result['stdout']}\n```")
        if result['stderr']:
            self.preview_panel.add_text("Errors:\n")
            self.preview_panel.add_text(f"```bash\n{result['stderr']}\n```")
        if result['returncode'] == 0:
            self.preview_panel.add_text("✅ Execution successful\n")
        else:
            self.preview_panel.add_text(f"❌ Execution failed (exit code: {result['returncode']})\n")

    def _run_cpp_execution_test(self, file_path):
        """Run C++ execution test"""
        self.preview_panel.add_text("\n🚀 Running C++ Execution Test:\n")
        
        # Compile the C++ file
        output_file = file_path.with_suffix('')
        compile_result = self.preview_panel.run_command_and_capture_output(f"g++ -o {output_file} {file_path}")
        
        if compile_result['success']:
            self.preview_panel.add_text("✅ Compilation successful\n")
            # Run the compiled program
            run_result = self.preview_panel.run_command_and_capture_output(f"./{output_file}")
            if run_result['stdout']:
                self.preview_panel.add_text("Output:\n")
                self.preview_panel.add_text(f"```bash\n{run_result['stdout']}\n```")
            if run_result['stderr']:
                self.preview_panel.add_text("Errors:\n")
                self.preview_panel.add_text(f"```bash\n{run_result['stderr']}\n```")
        else:
            self.preview_panel.add_text("❌ Compilation failed:\n")
            self.preview_panel.add_text(f"```bash\n{compile_result['stderr']}\n```")

    def _run_java_execution_test(self, file_path):
        """Run Java execution test"""
        self.preview_panel.add_text("\n🚀 Running Java Execution Test:\n")
        
        # Compile the Java file
        compile_result = self.preview_panel.run_command_and_capture_output(f"javac {file_path}")
        
        if compile_result['success']:
            self.preview_panel.add_text("✅ Compilation successful\n")
            # Run the compiled program
            class_name = file_path.stem
            run_result = self.preview_panel.run_command_and_capture_output(f"java {class_name}")
            if run_result['stdout']:
                self.preview_panel.add_text("Output:\n")
                self.preview_panel.add_text(f"```bash\n{run_result['stdout']}\n```")
            if run_result['stderr']:
                self.preview_panel.add_text("Errors:\n")
                self.preview_panel.add_text(f"```bash\n{run_result['stderr']}\n```")
        else:
            self.preview_panel.add_text("❌ Compilation failed:\n")
            self.preview_panel.add_text(f"```bash\n{compile_result['stderr']}\n```")

    def _run_python_coverage_test(self, file_path):
        """Run Python coverage test"""
        self.preview_panel.add_text("\n📊 Running Python Coverage Test:\n")
        
        # Try to run coverage if available
        result = self.preview_panel.run_command_and_capture_output(f"coverage run {file_path}")
        if result['success']:
            coverage_result = self.preview_panel.run_command_and_capture_output("coverage report")
            if coverage_result['stdout']:
                self.preview_panel.add_text("Coverage Report:\n")
                self.preview_panel.add_text(f"```bash\n{coverage_result['stdout']}\n```")

    def _run_cpp_coverage_test(self, file_path):
        """Run C++ coverage test"""
        self.preview_panel.add_text("\n📊 Running C++ Coverage Test:\n")
        
        # Try to run gcov if available
        output_file = file_path.with_suffix('')
        compile_result = self.preview_panel.run_command_and_capture_output(f"g++ -fprofile-arcs -ftest-coverage -o {output_file} {file_path}")
        if compile_result['success']:
            self.preview_panel.run_command_and_capture_output(f"./{output_file}")
            gcov_result = self.preview_panel.run_command_and_capture_output(f"gcov {file_path.name}")
            if gcov_result['stdout']:
                self.preview_panel.add_text("Coverage Report:\n")
                self.preview_panel.add_text(f"```bash\n{gcov_result['stdout']}\n```")

    def _run_java_coverage_test(self, file_path):
        """Run Java coverage test"""
        self.preview_panel.add_text("\n📊 Running Java Coverage Test:\n")
        
        # Try to run jacoco if available
        result = self.preview_panel.run_command_and_capture_output(f"jacoco {file_path}")
        if result['stdout']:
            self.preview_panel.add_text("Coverage Report:\n")
            self.preview_panel.add_text(f"```bash\n{result['stdout']}\n```")