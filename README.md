# Code Analyzer

A comprehensive desktop application for code analysis, testing, and AI-powered code review with a VSCode-like interface.

![Code Analyzer](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Supported Languages](#supported-languages)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Testing Capabilities](#testing-capabilities)
- [AI Integration](#ai-integration)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Contact](#contact)

## 🎯 Overview

Code Analyzer is a powerful desktop application designed for developers who want comprehensive code analysis and testing capabilities. It combines static analysis, dynamic testing, and white-box testing with AI-powered code review in a modern, VSCode-like interface.

### Key Benefits

- **Multi-language Support**: Analyze Python, C++, C, Java, and JavaScript code
- **Comprehensive Testing**: Static, dynamic, and white-box testing in one tool
- **AI-Powered Review**: Get intelligent code suggestions and improvements
- **Modern Interface**: Familiar VSCode-like experience with dark theme
- **Real-time Analysis**: Instant feedback on code quality and issues
- **Export Capabilities**: Save analysis results as PDF reports

## ✨ Features

### 🔍 Static Analysis
- **Syntax Validation**: Detect syntax errors and code structure issues
- **Style Checking**: Enforce coding standards and best practices
- **Code Smell Detection**: Identify potential problems and anti-patterns
- **Import Analysis**: Validate and optimize import statements
- **Complexity Metrics**: Measure cyclomatic complexity and code maintainability

### ⚡ Dynamic Testing
- **Execution Testing**: Run code and capture output/errors
- **Compilation Testing**: Test compilation for compiled languages
- **Function Validation**: Verify function definitions and calls
- **Error Handling**: Comprehensive error detection and reporting
- **Performance Analysis**: Basic performance metrics

### 🔬 White Box Testing
- **Code Coverage**: Measure test coverage percentage
- **Execution Paths**: Analyze possible code execution flows
- **Function/Class Analysis**: Count and analyze code elements
- **Line of Code Metrics**: Comprehensive code size analysis
- **Complexity Assessment**: Detailed complexity calculations

### 🤖 AI Integration
- **Intelligent Code Review**: AI-powered code quality assessment
- **Smart Suggestions**: Context-aware code improvements
- **Bug Detection**: AI-assisted bug identification
- **Best Practices**: Automated coding standard recommendations
- **Documentation Generation**: AI-generated code documentation

### 🎨 User Interface
- **VSCode-like Experience**: Familiar interface for developers
- **Dark Theme**: Easy on the eyes for extended use
- **Syntax Highlighting**: Language-specific code coloring
- **Tab Management**: Multiple file handling with close functionality
- **File Explorer**: Tree-view project browser
- **Real-time Status**: Live status updates and progress indicators

## 🌐 Supported Languages

| Language | Static Analysis | Dynamic Testing | White Box Testing | AI Review |
|----------|----------------|-----------------|-------------------|-----------|
| **Python** | ✅ Full Support | ✅ Full Support | ✅ Full Support | ✅ Full Support |
| **C++** | ✅ cppcheck | ✅ g++ compilation | ✅ gcov coverage | ✅ Basic Support |
| **C** | ✅ cppcheck | ✅ gcc compilation | ✅ gcov coverage | ✅ Basic Support |
| **Java** | ✅ checkstyle | ✅ javac/java | ✅ jacoco | ✅ Basic Support |
| **JavaScript** | ✅ Basic | ✅ Basic | ✅ Basic | ✅ Basic Support |

## 🚀 Installation

### Prerequisites

- **Python 3.8 or higher**
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Memory**: Minimum 4GB RAM, Recommended 8GB+
- **Storage**: 500MB available disk space

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/code-analyzer.git
cd code-analyzer
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install sv_ttk pygments fpdf requests
```

### Step 3: Install External Tools (Optional but Recommended)

#### For Python Analysis
```bash
pip install flake8 pylint coverage
```

#### For C/C++ Analysis (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install g++ cppcheck
```

#### For Java Analysis (Ubuntu/Debian)
```bash
sudo apt-get install openjdk-11-jdk checkstyle
```

#### For macOS
```bash
# Install Xcode Command Line Tools for C/C++
xcode-select --install

# Install tools via Homebrew
brew install cppcheck
brew install openjdk@11
```

#### For Windows
- Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/) for C/C++
- Install [Java JDK](https://adoptium.net/) for Java
- Install tools via [Chocolatey](https://chocolatey.org/):
  ```cmd
  choco install cppcheck
  choco install openjdk11
  ```

### Step 4: Configure AI Integration (Optional)

To enable AI-powered code review:

1. Get a DeepSeek API key from [DeepSeek](https://platform.deepseek.com/)
2. Set the API key in the application settings
3. The AI features will be automatically enabled

## 🏃 Quick Start

### 1. Launch the Application

```bash
python main.py
```

### 2. Open a Project

1. Click "Open Folder" in the sidebar
2. Select your project directory
3. The file explorer will populate with your project files

### 3. Select Files for Analysis

1. Click on files in the file explorer to select them
2. You can select multiple files by holding Ctrl/Cmd
3. Selected files will be highlighted

### 4. Run Analysis

Choose from three types of analysis:

- **Static Test**: Analyze code without execution
- **Dynamic Test**: Execute code and test functionality
- **White Box Test**: Analyze code structure and coverage

### 5. View Results

Results appear in the preview panel on the right side of the interface.

## 📖 Usage Guide

### File Management

#### Opening Files
- **Double-click** any file in the file explorer
- **Drag and drop** files into the editor
- Use **Ctrl+O** to open files via dialog

#### Tab Management
- **Right-click** tabs for context menu (Close, Close All, Close Others)
- **Middle-click** to close tabs quickly
- **Ctrl+Tab** to switch between tabs

#### Saving Files
- **Ctrl+S** to save current file
- **Ctrl+Shift+S** to save as

### Code Analysis

#### Static Analysis
Static analysis examines your code without executing it:

1. Select files in the file explorer
2. Click "Static Test" button
3. View results in the preview panel

**What it checks:**
- Syntax errors
- Style violations
- Code smells
- Import issues
- Complexity metrics

#### Dynamic Testing
Dynamic testing executes your code to test functionality:

1. Select files in the file explorer
2. Click "Dynamic Test" button
3. View execution results and errors

**What it tests:**
- Code execution
- Compilation (for compiled languages)
- Function calls
- Error handling
- Output validation

#### White Box Testing
White box testing analyzes code structure and coverage:

1. Select files in the file explorer
2. Click "White Box Test" button
3. View detailed analysis results

**What it analyzes:**
- Code coverage
- Execution paths
- Function/class counts
- Complexity metrics
- Line of code analysis

### AI-Powered Features

#### Code Review
1. Open a file in the editor
2. Click "Review Code" in the preview panel
3. Get AI-powered code quality assessment

#### AI Chat
1. Click "Show AI Chat" to open the chat interface
2. Ask questions about your code
3. Get intelligent suggestions and explanations

#### Code Suggestions
- AI can suggest code improvements
- Click "Accept" to apply suggested changes
- Review changes before applying

### Export and Reporting

#### Save as PDF
1. Run any analysis
2. Click "Save as PDF" in the preview panel
3. Choose location and save the report

#### Copy Results
- Right-click in preview panel
- Select "Copy" to copy analysis results
- Paste into other applications

## 🧪 Testing Capabilities

### Static Analysis Tools

#### Python
- **flake8**: Style guide enforcement, error detection
- **pylint**: Code quality analysis, error detection
- **Built-in**: Syntax validation, import analysis

#### C/C++
- **cppcheck**: Static analysis, bug detection
- **Built-in**: Syntax checking, structure analysis

#### Java
- **checkstyle**: Code style enforcement
- **Built-in**: Class structure validation

### Dynamic Testing Tools

#### Python
- **python**: Direct execution and testing
- **Built-in**: Import validation, function testing

#### C/C++
- **g++/gcc**: Compilation and execution
- **Built-in**: Header analysis, function detection

#### Java
- **javac/java**: Compilation and execution
- **Built-in**: Class validation, method testing

### White Box Testing Tools

#### Python
- **coverage**: Code coverage measurement
- **Built-in**: Complexity analysis, path analysis

#### C/C++
- **gcov**: Coverage analysis
- **Built-in**: Function counting, complexity metrics

#### Java
- **jacoco**: Coverage analysis
- **Built-in**: Class analysis, method counting

## 🤖 AI Integration

### DeepSeek API Integration

The application integrates with DeepSeek's AI API for intelligent code analysis:

#### Features
- **Code Review**: Automated quality assessment
- **Bug Detection**: AI-powered bug identification
- **Code Suggestions**: Intelligent improvement suggestions
- **Best Practices**: Automated coding standard recommendations
- **Documentation**: AI-generated code documentation

#### Configuration
1. Obtain API key from [DeepSeek Platform](https://platform.deepseek.com/)
2. Set API key in application settings
3. AI features will be automatically enabled

#### Fallback Mode
- When API is unavailable, the application provides offline responses
- Basic code analysis continues without AI features
- No data is sent without user consent

### AI Chat Interface

The built-in chat interface allows you to:

- **Ask Questions**: Get explanations about your code
- **Request Improvements**: Ask for code optimization suggestions
- **Debug Help**: Get assistance with debugging issues
- **Learning**: Understand coding concepts and best practices

## ⚙️ Configuration

### Application Settings

#### Theme Configuration
The application uses a VSCode-like dark theme by default. Theme settings are in `gui/theme.py`.

#### Font Configuration
Font settings are automatically configured based on your operating system:
- **Windows**: Consolas
- **macOS**: SF Mono
- **Linux**: DejaVu Sans Mono

#### Performance Settings
- **File Size Limits**: Maximum 10MB per file
- **Line Limits**: Maximum 50,000 lines per file
- **Memory Limits**: Maximum 2GB RAM usage

### External Tools Configuration

#### Python Tools
```bash
# Configure flake8
flake8 --max-line-length=88 --extend-ignore=E203

# Configure pylint
pylint --max-line-length=88 --disable=C0114
```

#### C/C++ Tools
```bash
# Configure cppcheck
cppcheck --enable=all --std=c++17

# Configure gcc/g++
g++ -std=c++17 -Wall -Wextra -O2
```

#### Java Tools
```bash
# Configure checkstyle
checkstyle -c google_checks.xml

# Configure javac
javac -Xlint:all
```

## 🔧 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check Python version
python --version

# Verify dependencies
pip list | grep -E "(sv_ttk|pygments|fpdf|requests)"

# Check for missing modules
python -c "import tkinter; print('tkinter available')"
```

#### External Tools Not Found
```bash
# Check if tools are in PATH
which flake8
which cppcheck
which javac

# Install missing tools
pip install flake8 pylint coverage  # Python
sudo apt-get install cppcheck       # C/C++ (Ubuntu)
sudo apt-get install openjdk-11-jdk # Java (Ubuntu)
```

#### AI Features Not Working
1. Verify API key is set correctly
2. Check internet connection
3. Verify API key has sufficient credits
4. Check API rate limits

#### Performance Issues
1. Close unnecessary files
2. Reduce file size (split large files)
3. Restart application
4. Check available system memory

### Error Messages

#### "Tool not found" Error
- Install the required external tool
- Ensure tool is in system PATH
- Restart application after installation

#### "Permission denied" Error
- Check file permissions
- Run as administrator (Windows)
- Use sudo (Linux/macOS) for system-wide installations

#### "API Error" Messages
- Verify API key is correct
- Check internet connection
- Verify API service status
- Check rate limits

### Getting Help

1. **Check the logs**: Look for error messages in the console
2. **Verify installation**: Ensure all dependencies are installed
3. **Test with sample files**: Try with simple test files first
4. **Contact support**: Email mohamednafel006@gmail.com

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Development Setup

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/code-analyzer.git
   cd code-analyzer
   ```
3. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8
   ```

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Write docstrings for all functions

### Testing

- Write tests for new features
- Ensure all tests pass before submitting
- Test on multiple operating systems if possible

### Submitting Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes**
3. **Run tests**
   ```bash
   pytest
   ```
4. **Commit your changes**
   ```bash
   git commit -m "Add feature: description"
   ```
5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a pull request**

### Areas for Contribution

- **New Language Support**: Add support for additional programming languages
- **UI Improvements**: Enhance the user interface
- **Performance Optimization**: Improve application performance
- **Documentation**: Improve documentation and examples
- **Testing**: Add more comprehensive tests
- **Bug Fixes**: Fix reported issues

## 📞 Contact

For support, questions, or contributions:

- **Email**: mohamednafel006@gmail.com
- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for general questions

## 🙏 Acknowledgments

- **VSCode**: Inspiration for the user interface design
- **Pygments**: Syntax highlighting capabilities
- **DeepSeek**: AI-powered code analysis
- **Open Source Community**: All the tools and libraries that make this possible

---

**Made with ❤️ for developers**

*Code Analyzer - Your comprehensive code analysis companion* 