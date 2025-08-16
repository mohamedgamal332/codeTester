import tkinter as tk
from tkinter import ttk
from .theme import VSCodeTheme
from .code_patcher import CodePatcher
# Import the new QEMU-based system instead of the old one
from .qemu_embedded_frameworks import QEMUEmbeddedFrameworks
from fpdf import FPDF
from tkinter import filedialog
import requests
import json
import threading
import subprocess
import sys
import os
from pathlib import Path
from tkinter import messagebox

class PreviewPanel:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.is_chat_visible = False
        self.chat_history = []  # Store chat conversation
        self.code_patcher = CodePatcher()  # Initialize the code patcher
        self.embedded_frameworks = QEMUEmbeddedFrameworks()  # Initialize embedded frameworks
        self.current_framework = None
        self.test_running = False
        self.setup_preview_panel()

    def setup_preview_panel(self):
        # Top toolbar
        self.toolbar = ttk.Frame(self.frame)
        self.toolbar.pack(fill=tk.X)
        
        # Review Code button
        review_code_btn = ttk.Button(
            self.toolbar,
            text="Review Code",
            command=self.review_current_code,
            style='Accent.TButton'
        )
        review_code_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Embedded Testing buttons
        self.embedded_frame = ttk.Frame(self.toolbar)
        self.embedded_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Framework selection
        self.framework_var = tk.StringVar()
        self.framework_combo = ttk.Combobox(
            self.embedded_frame,
            textvariable=self.framework_var,
            state='readonly',
            width=20
        )
        self.framework_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.framework_combo.bind('<<ComboboxSelected>>', self.on_framework_selected)
        
        # Compile button
        self.compile_btn = ttk.Button(
            self.embedded_frame,
            text="🔨 Compile",
            command=self.compile_framework,
            style='Accent.TButton'
        )
        self.compile_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # Flash button
        self.flash_btn = ttk.Button(
            self.embedded_frame,
            text="⚡ Flash",
            command=self.flash_framework,
            style='Accent.TButton'
        )
        self.flash_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # Flash & Test button
        self.flash_test_btn = ttk.Button(
            self.embedded_frame,
            text="🚀 Flash & Test",
            command=self.flash_and_test,
            style='Accent.TButton'
        )
        self.flash_test_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status indicator
        self.status_label = ttk.Label(
            self.embedded_frame,
            text="Ready",
            foreground='#28a745',
            font=('Segoe UI', 9, 'bold')
        )
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Save PDF button
        save_pdf_btn = ttk.Button(
            self.toolbar,
            text="Save as PDF",
            command=self.save_as_pdf,
            style='Accent.TButton'
        )
        save_pdf_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Toggle Chat button
        self.toggle_chat_btn = ttk.Button(
            self.toolbar,
            text="Show AI Chat",
            command=self.toggle_chat,
            style='Accent.TButton'
        )
        self.toggle_chat_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        # Create vertical paned window for preview and chat
        self.paned_window = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Preview content
        self.preview_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.preview_frame, weight=2)  # Give preview more weight

        # Enhanced font settings for preview panel
        preview_font_family = VSCodeTheme.PREVIEW_FONT_FAMILY
        preview_font_size = VSCodeTheme.PREVIEW_FONT_SIZE  # Use dedicated preview font size
        
        # Try to use emoji-friendly fonts
        emoji_fonts = ['Segoe UI Emoji', 'Noto Color Emoji', 'Apple Color Emoji', 'DejaVu Sans', 'Liberation Sans']
        preview_font_family = None
        
        for font in emoji_fonts:
            try:
                # Test if font is available
                test_label = tk.Label(self.frame, font=(font, 12))
                test_label.destroy()
                preview_font_family = font
                break
            except:
                continue
        
        # Fallback to theme font if no emoji fonts available
        if not preview_font_family:
            preview_font_family = VSCodeTheme.PREVIEW_FONT_FAMILY
        
        # Create frame for preview with scrollbar
        preview_container = ttk.Frame(self.preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        self.preview = tk.Text(
            preview_container,
            bg=VSCodeTheme.EDITOR_BG,
            fg=VSCodeTheme.FOREGROUND,
            insertbackground=VSCodeTheme.FOREGROUND,
            relief='flat',
            font=(preview_font_family, preview_font_size),
            pady=8,
            padx=8,
            state='disabled',  # Make preview read-only
            wrap='word',  # Better text wrapping
            spacing1=2,  # Line spacing above
            spacing2=1,  # Line spacing between lines
            spacing3=2   # Line spacing below
        )
        
        # Add scrollbar to preview
        preview_scrollbar = ttk.Scrollbar(preview_container, orient="vertical", command=self.preview.yview)
        self.preview.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Load available frameworks
        self.load_frameworks()

    def load_frameworks(self):
        """Load available frameworks into the dropdown"""
        frameworks = self.embedded_frameworks.get_frameworks()
        framework_names = [f"{config.display_name} ({name})" for name, config in frameworks.items()]
        
        self.framework_combo['values'] = framework_names
        if framework_names:
            self.framework_combo.set(framework_names[0])
            self.on_framework_selected()

    def on_framework_selected(self, event=None):
        """Handle framework selection"""
        selected = self.framework_var.get()
        if not selected:
            return
        
        # Extract framework name from display string
        framework_name = selected.split('(')[-1].rstrip(')')
        self.current_framework = self.embedded_frameworks.get_framework(framework_name)
        
        # Auto-setup framework environment if needed
        if self.current_framework:
            self.auto_setup_framework_if_needed(framework_name)
    
    def auto_setup_framework_if_needed(self, framework_name):
        """Automatically set up framework environment if needed"""
        def auto_setup():
            try:
                # Check if framework is ready
                is_ready, message = self.embedded_frameworks.validate_framework(framework_name)
                
                if is_ready:
                    self.frame.after(0, lambda: self.update_status(f"{framework_name.upper()} Ready", '#28a745'))
                else:
                    # Try to set up the framework automatically
                    if self.embedded_frameworks._ensure_framework_environment(framework_name):
                        self.frame.after(0, lambda: self.update_status(f"{framework_name.upper()} Ready", '#28a745'))
                    else:
                        self.frame.after(0, lambda: self.update_status(f"{framework_name.upper()} Setup Needed", '#ffc107'))
                        self.frame.after(0, lambda: self.add_text(f"⚠️  {framework_name.upper()} framework setup needed. Some features may not work.\n"))
            except Exception as e:
                self.frame.after(0, lambda: self.update_status(f"{framework_name.upper()} Error", '#dc3545'))
        
        threading.Thread(target=auto_setup, daemon=True).start()

    def update_status(self, text, color='#28a745'):
        """Update the status indicator"""
        self.status_label.configure(text=text, foreground=color)
    
    def reset_status(self):
        """Reset status to ready state"""
        self.status_label.configure(text="Ready", foreground='#28a745')
    
    def compile_framework(self):
        """Compile the current framework"""
        if not self.current_framework:
            messagebox.showwarning("Warning", "Please select a framework first!")
            return
        
        current_file = self._get_current_file()
        if not current_file:
            messagebox.showwarning("Warning", "No file selected for compilation!")
            return
        
        # Use the new QEMU-based compilation
        success, output = self.embedded_frameworks.compile_file_for_framework(
            str(current_file), self.current_framework,
            callback=lambda line: self.console_output.insert(tk.END, f"  [BUILD] {line}\n")
        )
        
        if success:
            self.console_output.insert(tk.END, "✅ Compilation successful!\n")
            self.update_status("✅ Compilation successful!")
        else:
            self.console_output.insert(tk.END, f"❌ Compilation failed: {output}\n")
            self.update_status("❌ Compilation failed!")
        
        self.console_output.see(tk.END)

    def compile_finished(self, success, output):
        """Handle compilation completion"""
        if success:
            self.update_status("Compiled", '#28a745')  # Green for success
            self.add_text("\n✅ Compilation completed successfully!\n")
        else:
            self.update_status("Compile Failed", '#dc3545')  # Red for failure
            self.add_text("\n❌ Compilation failed!\n")
            self.add_text(output + "\n")

    def flash_framework(self):
        """Flash the current framework"""
        if not self.current_framework:
            messagebox.showwarning("Warning", "Please select a framework first!")
            return
        
        current_file = self._get_current_file()
        if not current_file:
            messagebox.showwarning("Warning", "No file selected for flashing!")
            return
        
        # Use the new QEMU-based flashing
        success, output = self.embedded_frameworks.flash_file_for_framework(
            str(current_file), self.current_framework,
            callback=lambda line: self.console_output.insert(tk.END, f"  [FLASH] {line}\n")
        )
        
        if success:
            self.console_output.insert(tk.END, "✅ Flashing successful!\n")
            self.update_status("✅ Flashing successful!")
        else:
            self.console_output.insert(tk.END, f"❌ Flashing failed: {output}\n")
            self.update_status("❌ Flashing failed!")
        
        self.console_output.insert(tk.END, "\n")
        self.console_output.see(tk.END)

    def flash_finished(self, success, output):
        """Handle flashing completion"""
        if success:
            self.update_status("Flashed", '#28a745')  # Green for success
            self.add_text("\n✅ Flashing completed successfully!\n")
        else:
            self.update_status("Flash Failed", '#dc3545')  # Red for failure
            self.add_text("\n❌ Flashing failed!\n")
            self.add_text(output + "\n")

    def flash_and_test(self):
        """Flash and test the current framework"""
        if not self.current_framework:
            messagebox.showwarning("Warning", "Please select a framework first!")
            return
        
        current_file = self._get_current_file()
        if not current_file:
            messagebox.showwarning("Warning", "No file selected for testing!")
            return
        
        self.clear()
        self.update_status("Starting Flash & Test...", '#17a2b8')
        
        # Step 1: Compile
        self.add_text(f"🚀 Starting Dynamic Testing for {current_file.name} on {self.current_framework.display_name}...\n")
        self.add_text("=" * 60 + "\n\n")
        self.add_text("📋 Workflow Steps:\n")
        self.add_text("   1. 🔨 Compile your source file\n")
        self.add_text("   2. ⚡ Flash to device\n")
        self.add_text("   3. 📡 Monitor serial output\n")
        self.add_text("   4. ✅ Analyze test results\n\n")
        
        # Step 1: Compile
        self.add_text("🔨 Step 1: Compiling your source file...\n")
        success, output = self.embedded_frameworks.compile_file_for_framework(
            str(current_file), self.current_framework.name,
            callback=lambda line: self.add_text(f"  [BUILD] {line}\n")
        )
        
        if not success:
            self.add_text(f"❌ Compilation failed! Stopping workflow.\n{output}\n")
            self.update_status("❌ Compilation failed!", '#dc3545')
            return
        
        self.add_text("✅ Compilation successful!\n\n")
        
        # Step 2: Flash
        self.add_text("⚡ Step 2: Flashing your code to device...\n")
        flash_success, flash_output = self.embedded_frameworks.flash_file_for_framework(
            str(current_file), self.current_framework.name,
            callback=lambda line: self.add_text(f"  [FLASH] {line}\n")
        )
        
        if not flash_success:
            self.add_text(f"❌ Flashing failed! Stopping workflow.\n{flash_output}\n")
            self.update_status("❌ Flashing failed!", '#dc3545')
            return
        
        self.add_text("✅ Flashing successful!\n\n")
        
        # Step 3: Test with QEMU
        self.add_text("📡 Step 3: Running QEMU test...\n")
        
        # Find the compiled binary
        build_dir = current_file.parent / 'build'
        base_name = current_file.stem
        framework = self.embedded_frameworks.get_framework(self.current_framework.name)
        if framework:
            output_path = build_dir / f"{base_name}{framework.output_format}"
            
            if output_path.exists():
                # Run QEMU test
                test_success, test_output = self.embedded_frameworks.run_qemu_test(
                    self.current_framework.name, str(output_path),
                    callback=lambda line: self.add_text(f"  [QEMU] {line}\n"),
                    timeout_callback=lambda: self.add_text("  [QEMU] Timeout reached\n")
                )
                
                if test_success:
                    self.add_text("✅ QEMU test completed successfully!\n\n")
                    self.update_status("✅ Test completed!", '#28a745')
                else:
                    self.add_text(f"❌ QEMU test failed: {test_output}\n\n")
                    self.update_status("❌ Test failed!", '#dc3545')
            else:
                self.add_text(f"❌ Compiled binary not found: {output_path}\n")
                self.update_status("❌ Binary not found!", '#dc3545')
        else:
            self.add_text("❌ Framework configuration not found\n")
            self.update_status("❌ Framework error!", '#dc3545')
        
        self.add_text("🎯 Dynamic Testing workflow completed!\n")
        self.console_output.see(tk.END)

    def test_finished(self, success, output):
        """Handle test completion with enhanced result visualization"""
        if success:
            self.update_status("Test Passed", '#28a745')  # Green for success
            self.add_text("🎉 DYNAMIC TEST PASSED! 🎉\n")
            self.add_text("=" * 60 + "\n")
            self.add_text("✅ Device is functioning correctly\n")
            self.add_text("✅ Firmware compiled and flashed successfully\n")
            self.add_text("✅ Runtime behavior meets expectations\n")
            self.add_text("✅ Success keywords detected in serial output\n\n")
        else:
            self.update_status("Test Failed", '#dc3545')  # Red for failure
            self.add_text("💥 DYNAMIC TEST FAILED! 💥\n")
            self.add_text("=" * 60 + "\n")
            self.add_text("❌ Test did not complete successfully\n")
            self.add_text("❌ Check device connection and firmware\n")
            self.add_text("❌ Review serial output for errors\n\n")
        
        # Add detailed output analysis
        self.add_text("📊 Detailed Test Output:\n")
        self.add_text("-" * 40 + "\n")
        self.add_text(output + "\n")
        
        # Add summary
        self.add_text("\n" + "=" * 60 + "\n")
        if success:
            self.add_text("🎯 RECOMMENDATION: Device is ready for production deployment\n")
        else:
            self.add_text("🔧 RECOMMENDATION: Investigate and fix issues before deployment\n")
        self.add_text("=" * 60 + "\n")
        
        # Reset status after a delay
        self.frame.after(5000, self.reset_status)

    def setup_chat_frame(self):
        self.chat_frame = ttk.Frame(self.paned_window)
        
        # Chat display frame with scrollbar
        chat_display_frame = ttk.Frame(self.chat_frame)
        chat_display_frame.pack(fill=tk.BOTH, expand=True)

        # Enhanced font settings for chat display
        chat_font_family = VSCodeTheme.PREVIEW_FONT_FAMILY
        chat_font_size = VSCodeTheme.CHAT_FONT_SIZE  # Use dedicated chat font size
        
        # Try to use emoji-friendly fonts for chat too
        emoji_fonts = ['Segoe UI Emoji', 'Noto Color Emoji', 'Apple Color Emoji', 'DejaVu Sans', 'Liberation Sans']
        chat_font_family = None
        
        for font in emoji_fonts:
            try:
                # Test if font is available
                test_label = tk.Label(self.frame, font=(font, 12))
                test_label.destroy()
                chat_font_family = font
                break
            except:
                continue
        
        # Fallback to theme font if no emoji fonts available
        if not chat_font_family:
            chat_font_family = VSCodeTheme.PREVIEW_FONT_FAMILY

        self.chat_display = tk.Text(
            chat_display_frame,
            bg=VSCodeTheme.EDITOR_BG,
            fg=VSCodeTheme.FOREGROUND,
            insertbackground=VSCodeTheme.FOREGROUND,
            relief='flat',
            font=(chat_font_family, chat_font_size),
            pady=6,
            padx=6,
            state='disabled',
            height=12,  # Reduced height to make room for input
            wrap='word',  # Better text wrapping
            spacing1=1,   # Line spacing above
            spacing2=1,   # Line spacing between lines
            spacing3=1    # Line spacing below
        )
        
        scrollbar = ttk.Scrollbar(chat_display_frame, orient="vertical", command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=scrollbar.set)
        
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a beautiful input area at the bottom
        input_area_frame = tk.Frame(self.chat_frame, bg='#1e1e1e', relief='flat', bd=0)
        input_area_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=15, padx=15)
        
        # Add a beautiful gradient-like separator
        separator_frame = tk.Frame(input_area_frame, height=2, bg='#007acc', relief='flat')
        separator_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Beautiful header with icon and text
        header_frame = tk.Frame(input_area_frame, bg='#1e1e1e', relief='flat')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Header label with beautiful styling
        header_label = tk.Label(
            header_frame,
            text="💬 Chat with AI Assistant",
            bg='#1e1e1e',
            fg='#007acc',
            font=('Segoe UI', 12, 'bold'),
            relief='flat'
        )
        header_label.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Ask me anything about your code!",
            bg='#1e1e1e',
            fg='#888888',
            font=('Segoe UI', 9),
            relief='flat'
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))

        # Input field frame with beautiful styling
        input_field_frame = tk.Frame(input_area_frame, bg='#2d2d2d', relief='solid', bd=2, highlightbackground='#007acc', highlightthickness=1)
        input_field_frame.pack(fill=tk.X, pady=5)

        # Enhanced font settings for message input
        input_font_family = 'Segoe UI'
        input_font_size = 11
        
        # Try to use emoji-friendly fonts for input too
        emoji_fonts = ['Segoe UI Emoji', 'Noto Color Emoji', 'Apple Color Emoji', 'DejaVu Sans', 'Liberation Sans']
        input_font_family = None
        
        for font in emoji_fonts:
            try:
                # Test if font is available
                test_label = tk.Label(self.frame, font=(font, 12))
                test_label.destroy()
                input_font_family = font
                break
            except:
                continue
        
        # Fallback to default if no emoji fonts available
        if not input_font_family:
            input_font_family = 'Segoe UI'

        # Create a beautiful, modern input field
        self.message_input = tk.Text(
            input_field_frame,
            height=4,  # Slightly taller for better appearance
            bg='#ffffff',  # Pure white background
            fg='#2d2d2d',  # Dark text for contrast
            insertbackground='#007acc',  # Blue cursor
            relief='flat',
            bd=0,  # No border (handled by parent frame)
            font=(input_font_family, input_font_size),
            wrap='word',
            padx=15,  # Internal padding
            pady=12,  # Internal padding
            selectbackground='#007acc',  # Blue selection
            selectforeground='#ffffff'   # White text when selected
        )
        self.message_input.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Add beautiful placeholder text
        self.message_input.insert('1.0', "Type your message here...")
        self.message_input.configure(fg='#888888')  # Gray color for placeholder
        self.message_input.bind('<FocusIn>', self._on_input_focus_in)
        self.message_input.bind('<FocusOut>', self._on_input_focus_out)
        
        # Bind Enter key to send message (Shift+Enter for new line)
        self.message_input.bind('<Return>', self.handle_enter)
        self.message_input.bind('<Shift-Return>', self.handle_shift_enter)

        # Beautiful button frame on the right
        button_frame = tk.Frame(input_area_frame, bg='#1e1e1e', relief='flat')
        button_frame.pack(side=tk.RIGHT, padx=(15, 0))

        # Send button - beautiful modern design
        self.send_button = tk.Button(
            button_frame,
            text="📤 Send",
            command=self.send_message,
            bg='#007acc',  # Beautiful blue
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            bd=0,
            width=12,
            height=2,
            cursor='hand2',  # Hand cursor on hover
            activebackground='#005a9e',  # Darker blue when clicked
            activeforeground='white'
        )
        self.send_button.pack(side=tk.TOP, pady=2)

        # Retry button - beautiful design
        self.retry_button = tk.Button(
            button_frame,
            text="🔄 Retry",
            command=self.retry_last_message,
            state='disabled',
            bg='#ff6b35',  # Beautiful orange
            fg='white',
            font=('Segoe UI', 9),
            relief='flat',
            bd=0,
            width=12,
            cursor='hand2',
            activebackground='#e55a2b',
            activeforeground='white'
        )
        self.retry_button.pack(side=tk.TOP, pady=2)

        # Clear chat button - beautiful design
        self.clear_chat_button = tk.Button(
            button_frame,
            text="🗑️ Clear",
            command=self.clear_chat_history,
            bg='#dc3545',  # Beautiful red
            fg='white',
            font=('Segoe UI', 9),
            relief='flat',
            bd=0,
            width=12,
            cursor='hand2',
            activebackground='#c82333',
            activeforeground='white'
        )
        self.clear_chat_button.pack(side=tk.TOP, pady=2)

        # Add initial message to chat
        self.add_to_chat("💬 AI Assistant ready! Type your message in the beautiful input box below.", is_user=False)

    def _on_input_focus_in(self, event):
        """Handle focus in event for input field"""
        if self.message_input.get('1.0', 'end-1c') == "Type your message here...":
            self.message_input.delete('1.0', tk.END)
            self.message_input.configure(fg=VSCodeTheme.FOREGROUND)

    def _on_input_focus_out(self, event):
        """Handle focus out event for input field"""
        if not self.message_input.get('1.0', 'end-1c').strip():
            self.message_input.insert('1.0', "Type your message here...")
            self.message_input.configure(fg='#666666')  # Gray color for placeholder

    def clear_chat_history(self):
        """Clear the chat history and display"""
        self.chat_history = []
        self.chat_display.configure(state='normal')
        self.chat_display.delete('1.0', tk.END)
        self.chat_display.configure(state='disabled')
        self.add_to_chat("💬 Chat history cleared. Start a new conversation!", is_user=False)

    def get_conversation_stats(self):
        """Get conversation statistics"""
        user_messages = len([msg for msg in self.chat_history if msg["role"] == "user"])
        ai_messages = len([msg for msg in self.chat_history if msg["role"] == "assistant"])
        return {
            "total_messages": len(self.chat_history),
            "user_messages": user_messages,
            "ai_messages": ai_messages
        }

    def handle_enter(self, event):
        """Handle Enter key press"""
        if not event.state & 0x1:  # Check if Shift is not pressed
            self.send_message()
            return 'break'  # Prevent default Enter behavior

    def handle_shift_enter(self, event):
        """Handle Shift+Enter key press"""
        return None  # Allow default behavior (new line)

    def send_message(self):
        """Send message to AI and display response in chat"""
        message = self.message_input.get("1.0", "end-1c").strip()
        
        # Don't send if message is empty or placeholder
        if not message or message == "Type your message here...":
            return

        # Get preview content
        self.preview.configure(state='normal')
        preview_content = self.preview.get("1.0", "end-1c").strip()
        self.preview.configure(state='disabled')

        # Get current file content as context
        current_file_content = self._get_current_file_content()

        # Display user message
        self.add_to_chat(message, is_user=True)
        
        # Clear input and restore placeholder
        self.message_input.delete("1.0", tk.END)
        self.message_input.insert('1.0', "Type your message here...")
        self.message_input.configure(fg='#666666')  # Gray color for placeholder
        
        # Disable send button and input while processing
        self.send_button.configure(state='disabled')
        self.message_input.configure(state='disabled')
        
        # Store the message in chat history
        self.chat_history.append({"role": "user", "content": message})
        
        # Create the full prompt with context
        full_prompt = self._create_contextual_prompt(message, preview_content, current_file_content)

        # Start API call in separate thread
        threading.Thread(target=self.process_message, args=(full_prompt,)).start()

    def process_message(self, prompt):
        """Process message in separate thread"""
        try:
            # Add "thinking" indicator
            self.add_to_chat("🤔 Thinking...", is_user=False)
            
            # Make API call to DeepSeek
            response = self.call_deepseek_api(prompt)
            
            # Remove "thinking" message
            self.chat_display.configure(state='normal')
            self.chat_display.delete("end-2l", "end")
            self.chat_display.configure(state='disabled')
            
            # Store AI response in chat history
            self.chat_history.append({"role": "assistant", "content": response})
            
            # Display response
            self.add_to_chat(response, is_user=False)
            
        except Exception as e:
            self.add_to_chat(f"❌ Error: {str(e)}", is_user=False)
            self.retry_button.configure(state='normal')
        
        finally:
            # Re-enable input and send button using the root window
            root_window = self.frame.winfo_toplevel()
            root_window.after(0, lambda: [
                self.send_button.configure(state='normal'),
                self.message_input.configure(state='normal'),
                self.message_input.focus_set()
            ])

    def call_deepseek_api(self, prompt):
        """Make API call to DeepSeek via OpenRouter with conversation history"""
        try:
            # OpenRouter API configuration (like in contact_two.py)
            api_key = "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"
            model = "deepseek/deepseek-r1-0528"
            openrouter_api_base = "https://openrouter.ai/api/v1"
            
            print(f"DEBUG: Using OpenRouter API with key ending: {api_key[-4:]}")
            print(f"DEBUG: Using model: {model}")
            print(f"DEBUG: OpenRouter endpoint: {openrouter_api_base}")
            
            # Use OpenAI client with OpenRouter base URL (like in contact_two.py)
            from openai import OpenAI
            client = OpenAI(base_url=openrouter_api_base, api_key=api_key)
            
            # Build messages array with conversation history
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful coding assistant. When suggesting code changes, format them clearly and explain what you're changing. If you provide code blocks, make them easy to understand and implement. Always consider the context of the current file and any previous conversation."
                }
            ]
            
            # Add conversation history (last 10 messages to stay within limits)
            history_messages = self.chat_history[-10:] if len(self.chat_history) > 10 else self.chat_history
            messages.extend(history_messages)
            
            # Add the current prompt
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            print(f"DEBUG: Sending request with {len(messages)} messages via OpenRouter")
            
            # Use the same approach as contact_two.py
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            print(f"DEBUG: OpenRouter API call successful")
            return completion.choices[0].message.content
                
        except Exception as e:
            print(f"DEBUG: OpenRouter API Exception: {str(e)}")
            return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt):
        """Get a fallback response when API is not available"""
        # Simple fallback responses based on the prompt content
        prompt_lower = prompt.lower()
        
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I'm your AI coding assistant. I'm currently running in fallback mode. To get full AI capabilities, please provide a valid API key for OpenAI, DeepSeek, or another AI service."
        
        elif "error" in prompt_lower or "bug" in prompt_lower:
            return "I can help you debug code issues! However, I'm currently running in fallback mode. For detailed code analysis and suggestions, please provide a valid AI API key."
        
        elif "review" in prompt_lower or "improve" in prompt_lower:
            return "I'd be happy to review your code! Currently running in fallback mode. For comprehensive code reviews with specific suggestions, please provide a valid AI API key."
        
        elif "function" in prompt_lower or "method" in prompt_lower:
            return "I can help you with functions and methods! For detailed code suggestions and improvements, please provide a valid AI API key to enable full functionality."
        
        else:
            return "I'm your AI coding assistant! I'm currently running in fallback mode. To get intelligent code suggestions, debugging help, and comprehensive reviews, please provide a valid API key for an AI service like OpenAI or DeepSeek.\n\nYou can get a free API key from:\n- OpenAI: https://platform.openai.com/\n- DeepSeek: https://platform.deepseek.com/"

    def retry_last_message(self):
        """Retry the last failed message"""
        if self.chat_history and self.chat_history[-1]["role"] == "user":
            last_message = self.chat_history[-1]["content"]
            self.send_button.configure(state='disabled')
            self.retry_button.configure(state='disabled')
            threading.Thread(target=self.process_message, args=(last_message,)).start()

    def toggle_chat(self):
        if self.is_chat_visible:
            self.paned_window.remove(self.chat_frame)
            self.is_chat_visible = False
            self.toggle_chat_btn.configure(text="Show AI Chat")
        else:
            self.paned_window.add(self.chat_frame, weight=1)  # Give chat less weight than preview
            self.is_chat_visible = True
            self.toggle_chat_btn.configure(text="Hide AI Chat")
            # Set initial position of the sash (divider)
            self.paned_window.after(100, lambda: self._safe_set_sash_position())
            # Focus on the input field
            self.message_input.focus_set()
            # Add a debug message to confirm chat is working
            self.add_to_chat("✅ Chat interface is now visible and ready!", is_user=False)

    def _safe_set_sash_position(self):
        """Safely set the sash position without causing errors"""
        try:
            if self.paned_window.winfo_exists() and self.paned_window.winfo_height() > 0:
                self.paned_window.sashpos(0, int(self.paned_window.winfo_height() * 0.6))
        except Exception as e:
            # Silently ignore sash positioning errors
            pass

    def review_current_code(self):
        """Send current code to AI for review and display in preview panel"""
        try:
            # Get the current active file
            current_file = self._get_current_file()
            
            if not current_file:
                self.clear()
                self.add_text("❌ No file is currently active to review\n\n")
                self.add_text("💡 To review a file:\n")
                self.add_text("   1. Open a file in the editor (double-click in sidebar)\n")
                self.add_text("   2. Make sure the file tab is active (click on the tab)\n")
                self.add_text("   3. Click 'Review Code' again\n")
                return
            
            # Clear preview panel and show initial message
            self.clear()
            self.add_text(f"🔍 Reviewing code: {current_file.name}\n")
            self.add_text("=" * 50 + "\n\n")
            self.add_text("⏳ Starting AI review...\n\n")
            
            # Read the file content
            with open(current_file, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # Create review prompt that asks for targeted suggestions
            review_prompt = f"""Please review this code and provide specific, targeted suggestions for improvement.

For each suggestion, please specify exactly what should be changed:
1. If suggesting a function change, say "Replace function X with:" followed by the new code
2. If suggesting a line change, say "Change line X to:" followed by the new line
3. If suggesting a block change, say "Replace lines X-Y with:" followed by the new code
4. If suggesting an addition, say "Add after line X:" followed by the new code

Focus on:
- Code quality and best practices
- Potential bugs or issues
- Performance improvements
- Security concerns
- Better structure or readability

Here's the code to review:

```{current_file.suffix[1:] if current_file.suffix else 'text'}
{code_content}
```

Please provide specific, actionable suggestions with clear instructions on what to change."""

            # Update status: Sending to AI
            self.clear()
            self.add_text(f"🔍 Reviewing code: {current_file.name}\n")
            self.add_text("=" * 50 + "\n\n")
            self.add_text("📤 Sending code to AI for analysis...\n\n")
            
            # Make the API call directly (this will block the UI, but it's simpler)
            try:
                response = self.call_deepseek_api(review_prompt)
                
                # Debug: Print response length
                print(f"DEBUG: Review response length: {len(response) if response else 0}")
                print(f"DEBUG: Response preview: {response[:200] if response else 'None'}...")
                
                # Display the final result with proper formatting
                self.clear()
                self.add_text(f"🔍 Code Review: {current_file.name}\n")
                self.add_text("=" * 50 + "\n\n")
                self.add_text("🤖 AI Review Results:\n")
                self.add_text("-" * 30 + "\n\n")
                
                if response:
                    # Store the response for potential application
                    self.last_ai_response = response
                    self.last_reviewed_file = current_file
                    
                    # Add the response with proper line breaks
                    self.add_text(response + "\n\n")
                    self.add_text("=" * 50 + "\n")
                    self.add_text("✅ Review completed successfully!\n\n")
                    
                    # Add apply changes button
                    self.add_apply_changes_button()
                    
                    print(f"DEBUG: Full response displayed, length: {len(response)}")
                else:
                    self.add_text("❌ No response received from AI\n\n")
                    self.add_text("💡 Try using the AI Chat instead, or check your API key configuration.")
                
                # Ensure the preview scrolls to show all content
                self.preview.see(tk.END)
                
            except Exception as e:
                # Display error
                self.clear()
                self.add_text(f"🔍 Code Review: {current_file.name}\n")
                self.add_text("=" * 50 + "\n\n")
                self.add_text("❌ Review Error:\n")
                self.add_text("-" * 30 + "\n\n")
                self.add_text(f"Failed to get AI review: {str(e)}\n\n")
                self.add_text("💡 Try using the AI Chat instead, or check your API key configuration.")
                
                # Ensure the preview scrolls to show all content
                self.preview.see(tk.END)
            
        except Exception as e:
            self.clear()
            self.add_text(f"❌ Error reviewing code: {str(e)}")
            # Ensure the preview scrolls to show all content
            self.preview.see(tk.END)

    def add_apply_changes_button(self):
        """Add a button to apply AI suggestions"""
        # Create a frame for the button
        button_frame = ttk.Frame(self.preview_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Apply Changes button
        apply_btn = ttk.Button(
            button_frame,
            text="🔧 Apply AI Suggestions",
            command=self.apply_ai_suggestions,
            style='Accent.TButton'
        )
        apply_btn.pack(side=tk.RIGHT, padx=5)
        
        # Preview Changes button
        preview_btn = ttk.Button(
            button_frame,
            text="👁️ Preview Changes",
            command=self.preview_ai_changes,
            style='Accent.TButton'
        )
        preview_btn.pack(side=tk.RIGHT, padx=5)

    def apply_ai_suggestions(self):
        """Apply AI suggestions using targeted changes"""
        try:
            if not hasattr(self, 'last_ai_response') or not hasattr(self, 'last_reviewed_file'):
                self.add_text("❌ No AI suggestions available to apply\n")
                return
            
            current_file = self.last_reviewed_file
            
            # Show confirmation dialog
            if not self._confirm_ai_changes(current_file):
                return
            
            # Apply targeted changes
            result = self.code_patcher.apply_targeted_changes(current_file, self.last_ai_response)
            
            if result['success']:
                # Refresh the editor
                self._refresh_editor(current_file)
                
                # Show success message
                self.add_text("\n" + "=" * 50 + "\n")
                self.add_text("✅ AI suggestions applied successfully!\n")
                self.add_text(f"📁 Backup created: {result['backup_path'].name}\n")
                self.add_text(f"🔧 Changes applied: {len(result['changes_applied'])}\n")
                
                # Show details of applied changes
                for i, change in enumerate(result['changes_applied'], 1):
                    self.add_text(f"   {i}. {change.get('type', 'Unknown')} change\n")
                
            else:
                self.add_text("\n" + "=" * 50 + "\n")
                self.add_text("❌ Failed to apply AI suggestions\n")
                self.add_text(f"Error: {result['error']}\n")
                
        except Exception as e:
            self.add_text(f"\n❌ Error applying AI suggestions: {str(e)}\n")

    def preview_ai_changes(self):
        """Preview what changes would be applied"""
        try:
            if not hasattr(self, 'last_ai_response') or not hasattr(self, 'last_reviewed_file'):
                self.add_text("❌ No AI suggestions available to preview\n")
                return
            
            current_file = self.last_reviewed_file
            
            # Read original file
            with open(current_file, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
            
            # Parse AI suggestions
            changes = self.code_patcher._parse_ai_suggestions(self.last_ai_response)
            
            if not changes:
                self.add_text("❌ No valid changes found in AI suggestions\n")
                return
            
            # Apply changes to a copy
            modified_lines = original_lines.copy()
            applied_changes = []
            
            for change in changes:
                result = self.code_patcher._apply_single_change(modified_lines, change)
                if result['success']:
                    applied_changes.append(result)
                    modified_lines = result['new_lines']
            
            if applied_changes:
                # Create diff preview
                diff = self.code_patcher.create_diff_preview(original_lines, modified_lines)
                
                # Show preview dialog
                self._show_diff_preview(diff, current_file)
            else:
                self.add_text("❌ No changes could be applied\n")
                
        except Exception as e:
            self.add_text(f"\n❌ Error previewing changes: {str(e)}\n")

    def _confirm_ai_changes(self, file_path):
        """Show confirmation dialog for applying AI changes"""
        dialog = tk.Toplevel(self.frame.winfo_toplevel())
        dialog.title("Apply AI Suggestions")
        dialog.geometry("400x200")
        dialog.configure(bg=VSCodeTheme.BACKGROUND)
        
        # Make dialog modal
        dialog.transient(self.frame.winfo_toplevel())
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        # Content
        content_frame = ttk.Frame(dialog)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(content_frame, 
                 text=f"Apply AI suggestions to {file_path.name}?", 
                 style='Dark.TLabel').pack(pady=(0, 10))
        
        ttk.Label(content_frame, 
                 text="This will apply targeted changes based on AI suggestions.\nA backup will be created automatically.",
                 style='Dark.TLabel').pack(pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=10)
        
        confirmed = [False]
        
        def on_confirm():
            confirmed[0] = True
            dialog.destroy()
        
        def on_cancel():
            confirmed[0] = False
            dialog.destroy()
        
        ttk.Button(button_frame, text="Apply", command=on_confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        # Wait for dialog to close
        dialog.wait_window()
        return confirmed[0]

    def _show_diff_preview(self, diff, file_path):
        """Show a dialog with diff preview"""
        dialog = tk.Toplevel(self.frame.winfo_toplevel())
        dialog.title(f"Preview Changes - {file_path.name}")
        dialog.geometry("800x600")
        dialog.configure(bg=VSCodeTheme.BACKGROUND)
        
        # Make dialog modal
        dialog.transient(self.frame.winfo_toplevel())
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"800x600+{x}+{y}")
        
        # Content
        content_frame = ttk.Frame(dialog)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(content_frame, 
                 text=f"Preview of changes to {file_path.name}:", 
                 style='Dark.TLabel').pack(pady=(0, 10))
        
        # Diff text widget
        diff_text = tk.Text(
            content_frame,
            bg=VSCodeTheme.EDITOR_BG,
            fg=VSCodeTheme.FOREGROUND,
            font=('Consolas', 10),
            wrap='none'
        )
        diff_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbars
        diff_scrollbar_y = ttk.Scrollbar(content_frame, orient="vertical", command=diff_text.yview)
        diff_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        diff_text.configure(yscrollcommand=diff_scrollbar_y.set)
        
        diff_scrollbar_x = ttk.Scrollbar(content_frame, orient="horizontal", command=diff_text.xview)
        diff_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        diff_text.configure(xscrollcommand=diff_scrollbar_x.set)
        
        # Insert diff content
        diff_text.insert('1.0', diff)
        diff_text.configure(state='disabled')
        
        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def _update_review_status(self, status_message):
        """Update the review status in the preview panel"""
        try:
            # Get current content
            self.preview.configure(state='normal')
            content = self.preview.get('1.0', tk.END)
            lines = content.split('\n')
            
            # Find and update the status line
            for i, line in enumerate(lines):
                if line.startswith('⏳') or line.startswith('📤') or line.startswith('🤖'):
                    lines[i] = status_message
                    break
            
            # Update the preview
            self.preview.delete('1.0', tk.END)
            self.preview.insert('1.0', '\n'.join(lines))
            self.preview.configure(state='disabled')
            
        except Exception as e:
            print(f"Error updating review status: {e}")

    def _display_review_result(self, filename, response):
        """Display the final review result"""
        try:
            print(f"DEBUG: Displaying review result for {filename}")
            print(f"DEBUG: Response length: {len(response) if response else 0}")
            
            self.clear()
            self.add_text(f"🔍 Code Review: {filename}\n")
            self.add_text("=" * 50 + "\n\n")
            self.add_text("🤖 AI Review Results:\n")
            self.add_text("-" * 30 + "\n\n")
            
            if response:
                self.add_text(response)
            else:
                self.add_text("❌ No response received from AI")
            
        except Exception as e:
            print(f"Error displaying review result: {e}")
            self.clear()
            self.add_text(f"❌ Error displaying review result: {str(e)}")

    def _display_review_error(self, filename, error_message):
        """Display review error"""
        try:
            print(f"DEBUG: Displaying review error for {filename}: {error_message}")
            
            self.clear()
            self.add_text(f"🔍 Code Review: {filename}\n")
            self.add_text("=" * 50 + "\n\n")
            self.add_text("❌ Review Error:\n")
            self.add_text("-" * 30 + "\n\n")
            self.add_text(f"Failed to get AI review: {error_message}\n\n")
            self.add_text("💡 Try using the AI Chat instead, or check your API key configuration.")
            
        except Exception as e:
            print(f"Error displaying review error: {e}")
            self.clear()
            self.add_text(f"❌ Error displaying review error: {str(e)}")

    def send_review_request(self, prompt):
        """Send review request to AI - this method is no longer used for Review Code button"""
        # This method is kept for compatibility but Review Code now goes directly to preview
        pass

    def add_to_chat(self, message, is_user=True):
        self.chat_display.configure(state='normal')
        prefix = "👤 You" if is_user else "🤖 AI"
        
        # Add context indicator for user messages (less intrusive)
        if is_user:
            current_file = self._get_current_file()
            if current_file:
                stats = self.get_conversation_stats()
                if stats['total_messages'] == 0:  # Only show context for first message
                    self.chat_display.insert(tk.END, f"📁 Context: {current_file.name} (active file)\n")
            else:
                stats = self.get_conversation_stats()
                if stats['total_messages'] == 0:  # Only show context for first message
                    self.chat_display.insert(tk.END, f"📁 Context: No active file\n")
        
        # Check if message contains code blocks
        if self._contains_code_blocks(message):
            # Add message with code formatting
            self.chat_display.insert(tk.END, f"{prefix}: ")
            
            # Split message into text and code parts
            parts = self._split_message_and_code(message)
            
            for part in parts:
                if part['type'] == 'text':
                    self.chat_display.insert(tk.END, part['content'])
                elif part['type'] == 'code':
                    # Create code box
                    self._insert_code_box(part['content'], part['language'])
            
            self.chat_display.insert(tk.END, "\n")
            
            # Check if AI message contains code suggestions that can be accepted
            if not is_user and self._contains_code_suggestion(message):
                self.chat_display.insert(tk.END, "💡 Accept Code Changes: ")
                
                # Create accept button
                accept_btn = tk.Button(
                    self.chat_display,
                    text="✅ Accept",
                    command=lambda: self._accept_code_changes(message),
                    bg='#28a745',
                    fg='white',
                    relief='flat',
                    font=('Consolas', 9)
                )
                self.chat_display.window_create(tk.END, window=accept_btn)
        else:
            self.chat_display.insert(tk.END, f"{prefix}: {message}\n")
        
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def _get_current_file_content(self):
        """Get the content of the currently active file"""
        try:
            current_file = self._get_current_file()
            if current_file and current_file.exists():
                with open(current_file, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        except Exception as e:
            print(f"Error reading current file: {e}")
            return ""

    def _create_contextual_prompt(self, user_message, preview_content, file_content):
        """Create a contextual prompt for the AI"""
        prompt = f"""You are a helpful coding assistant. Please help with the following request.

User Message: {user_message}

"""
        
        # Add preview content if available
        if preview_content.strip():
            prompt += f"Preview Panel Content:\n{preview_content}\n\n"
        
        # Add current file content if available
        if file_content.strip():
            prompt += f"Current File Content:\n```\n{file_content}\n```\n\n"
        
        prompt += f"Please respond to: {user_message}"
        
        return prompt

    def _contains_code_blocks(self, message):
        """Check if message contains code blocks"""
        return '```' in message

    def _split_message_and_code(self, message):
        """Split message into text and code parts"""
        parts = []
        lines = message.split('\n')
        current_text = []
        in_code_block = False
        current_code = []
        language = 'text'
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    if current_code:
                        parts.append({
                            'type': 'code',
                            'content': '\n'.join(current_code),
                            'language': language
                        })
                    current_code = []
                    in_code_block = False
                else:
                    # Start of code block
                    if current_text:
                        parts.append({
                            'type': 'text',
                            'content': '\n'.join(current_text) + '\n'
                        })
                    current_text = []
                    in_code_block = True
                    language = line.strip()[3:].strip()  # Remove ```
            elif in_code_block:
                current_code.append(line)
            else:
                current_text.append(line)
        
        # Add remaining text
        if current_text:
            parts.append({
                'type': 'text',
                'content': '\n'.join(current_text)
            })
        
        return parts

    def _insert_code_box(self, code, language):
        """Insert a code box into the chat display"""
        # Create a frame for the code box with better styling
        code_frame = tk.Frame(
            self.chat_display,
            bg='#1e1e1e',  # Dark background
            relief='solid',
            bd=2,
            highlightbackground='#404040',  # Border color
            highlightthickness=1
        )
        
        # Language label with better styling
        if language and language != 'text':
            lang_label = tk.Label(
                code_frame,
                text=f" {language.upper()} ",
                bg='#007acc',  # Blue background for language label
                fg='#ffffff',  # White text
                font=('Consolas', 8, 'bold'),
                padx=8,
                pady=3
            )
            lang_label.pack(fill=tk.X, padx=2, pady=2)
        
        # Code text widget with better styling
        code_text = tk.Text(
            code_frame,
            bg='#2d2d2d',  # Slightly lighter background for code
            fg='#ffffff',  # Pure white text for maximum visibility
            insertbackground='#ffffff',
            relief='flat',
            font=('Consolas', 10),  # Keep Consolas for code, but ensure emoji support
            wrap='word',
            height=min(20, len(code.split('\n')) + 2),  # Dynamic height
            padx=10,
            pady=10,
            state='normal',  # Allow text to be visible
            selectbackground='#404040',  # Selection color
            selectforeground='#ffffff',   # Selection text color
            borderwidth=0
        )
        code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        code_text.insert('1.0', code)
        code_text.configure(state='disabled')  # Make read-only after inserting
        
        # Insert the code frame into the chat display
        self.chat_display.window_create(tk.END, window=code_frame)
        self.chat_display.insert(tk.END, "\n")

    def _contains_code_suggestion(self, message):
        """Check if message contains code suggestions"""
        # Look for code blocks or specific patterns that indicate code changes
        code_indicators = [
            '```python', '```cpp', '```java', '```javascript', '```c',
            'here is the updated code', 'here is the corrected code',
            'here is the fixed code', 'here is the improved code',
            'suggested changes', 'recommended changes', 'code changes'
        ]
        
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in code_indicators)

    def _accept_code_changes(self, message):
        """Accept code changes from AI suggestion"""
        try:
            # Extract code blocks from the message
            code_blocks = self._extract_code_blocks(message)
            
            if not code_blocks:
                self.add_to_chat("❌ No code blocks found to accept", is_user=False)
                return
            
            # If multiple code blocks, let user choose
            if len(code_blocks) > 1:
                self._show_code_selection_dialog(code_blocks)
            else:
                self._apply_code_changes(code_blocks[0])
                
        except Exception as e:
            self.add_to_chat(f"❌ Error accepting code changes: {str(e)}", is_user=False)

    def _extract_code_blocks(self, message):
        """Extract code blocks from AI message"""
        code_blocks = []
        lines = message.split('\n')
        in_code_block = False
        current_block = []
        language = None
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    if current_block:
                        code_blocks.append({
                            'language': language,
                            'code': '\n'.join(current_block)
                        })
                    current_block = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                    language = line.strip()[3:].strip()  # Remove ```
            elif in_code_block:
                current_block.append(line)
        
        return code_blocks

    def _show_code_selection_dialog(self, code_blocks):
        """Show dialog to select which code block to apply"""
        dialog = tk.Toplevel(self.frame.winfo_toplevel()) # Use self.frame.winfo_toplevel() for the root window
        dialog.title("Select Code Block to Apply")
        dialog.geometry("600x400")
        dialog.configure(bg=VSCodeTheme.BACKGROUND)
        
        # Make dialog modal
        dialog.transient(self.frame.winfo_toplevel()) # Use self.frame.winfo_toplevel() for the root window
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"600x400+{x}+{y}")
        
        # Create selection frame
        selection_frame = ttk.Frame(dialog)
        selection_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(selection_frame, text="Select which code block to apply:", 
                 style='Dark.TLabel').pack(pady=(0, 10))
        
        # Create notebook for code blocks
        notebook = ttk.Notebook(selection_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        selected_block = [None]  # Use list to store selection
        
        for i, block in enumerate(code_blocks):
            # Create tab for each code block
            tab_frame = ttk.Frame(notebook)
            notebook.add(tab_frame, text=f"Block {i+1} ({block['language']})")
            
            # Code preview
            code_text = tk.Text(
                tab_frame,
                bg=VSCodeTheme.EDITOR_BG,
                fg=VSCodeTheme.FOREGROUND,
                font=('Consolas', 10),
                wrap='word',
                height=15
            )
            code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            code_text.insert('1.0', block['code'])
            code_text.configure(state='disabled')
            
            # Apply button
            apply_btn = ttk.Button(
                tab_frame,
                text="Apply This Code Block",
                command=lambda b=block: self._apply_selected_code_block(b, dialog)
            )
            apply_btn.pack(pady=5)
        
        # Cancel button
        cancel_btn = ttk.Button(
            selection_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_btn.pack(pady=10)

    def _apply_selected_code_block(self, code_block, dialog):
        """Apply the selected code block"""
        dialog.destroy()
        self._apply_code_changes(code_block)

    def _apply_code_changes(self, code_block):
        """Apply code changes to the current file using targeted patching"""
        try:
            # Get the current active file from the main editor
            current_file = self._get_current_file()
            
            if not current_file:
                self.add_to_chat("❌ No file is currently open to apply changes to", is_user=False)
                return
            
            # Ask user for confirmation
            if not self._confirm_code_application(code_block, current_file):
                return
            
            # Create a mock AI response with the code block
            ai_response = f"Replace the current code with:\n\n```{code_block.get('language', 'text')}\n{code_block['code']}\n```"
            
            # Apply targeted changes
            result = self.code_patcher.apply_targeted_changes(current_file, ai_response)
            
            if result['success']:
            # Refresh the editor
            self._refresh_editor(current_file)
            
            self.add_to_chat(f"✅ Code changes applied to {current_file.name}", is_user=False)
                self.add_to_chat(f"📁 Backup created: {result['backup_path'].name}", is_user=False)
            else:
                self.add_to_chat(f"❌ Failed to apply changes: {result['error']}", is_user=False)
            
        except Exception as e:
            self.add_to_chat(f"❌ Error applying code changes: {str(e)}", is_user=False)

    def _get_current_file(self):
        """Get the currently active file from the editor"""
        try:
            # Get the current tab from the editor
            current_tab = self.editor.get_current_tab()
            if current_tab:
                # Get the file path from the tab
                file_path = self.editor.get_tab_file_path(current_tab)
                if file_path and os.path.exists(file_path):
                    return Path(file_path)
                return None
        except Exception as e:
            print(f"Error getting current file: {e}")
            return None

    def _refresh_editor(self, file_path):
        """Refresh the editor to show the updated file"""
        try:
            # Use direct reference to main application if available
            if hasattr(self, 'main_app') and self.main_app:
                self.main_app.refresh_file_content(file_path)
                return
            
            # Fallback: Get the main application instance by traversing up the widget hierarchy
            current_widget = self.frame
            while current_widget and not hasattr(current_widget, 'refresh_file_content'):
                current_widget = current_widget.master
            
            if current_widget and hasattr(current_widget, 'refresh_file_content'):
                current_widget.refresh_file_content(file_path)
            else:
                # Try alternative approach
                for widget in self.frame.winfo_toplevel().winfo_children():
                    if hasattr(widget, 'refresh_file_content'):
                        widget.refresh_file_content(file_path)
                        break
        except Exception as e:
            print(f"Error refreshing editor: {e}")

    def _confirm_code_application(self, code_block, file_path):
        """Show confirmation dialog for code application"""
        dialog = tk.Toplevel(self.frame.winfo_toplevel()) # Use self.frame.winfo_toplevel() for the root window
        dialog.title("Confirm Code Application")
        dialog.geometry("500x300")
        dialog.configure(bg=VSCodeTheme.BACKGROUND)
        
        # Make dialog modal
        dialog.transient(self.frame.winfo_toplevel()) # Use self.frame.winfo_toplevel() for the root window
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"500x300+{x}+{y}")
        
        # Content
        content_frame = ttk.Frame(dialog)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(content_frame, 
                 text=f"Apply code changes to {file_path.name}?", 
                 style='Dark.TLabel').pack(pady=(0, 10))
        
        # Code preview
        preview_text = tk.Text(
            content_frame,
            bg=VSCodeTheme.EDITOR_BG,
            fg=VSCodeTheme.FOREGROUND,
            font=('Consolas', 9),
            wrap='word',
            height=10
        )
        preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        preview_text.insert('1.0', code_block['code'])
        preview_text.configure(state='disabled')
        
        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=10)
        
        confirmed = [False]
        
        def on_confirm():
            confirmed[0] = True
            dialog.destroy()
        
        def on_cancel():
            confirmed[0] = False
            dialog.destroy()
        
        ttk.Button(button_frame, text="Apply", command=on_confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        # Wait for dialog to close
        dialog.wait_window()
        return confirmed[0]

    def _write_code_to_file(self, file_path, code):
        """Write code to the specified file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
        except Exception as e:
            raise Exception(f"Failed to write to file: {str(e)}")

    def clear(self):
        """Clear the preview content"""
        self.preview.configure(state='normal')
        self.preview.delete('1.0', tk.END)
        self.preview.configure(state='disabled')

    def add_text(self, text):
        """Add text to the preview with code box formatting"""
        self.preview.configure(state='normal')
        
        # Check if text contains code blocks
        if '```' in text:
            # Split and format text with code boxes
            parts = self._split_message_and_code(text)
            
            for part in parts:
                if part['type'] == 'text':
                    self.preview.insert(tk.END, part['content'])
                elif part['type'] == 'code':
                    # Create code box in preview
                    self._insert_preview_code_box(part['content'], part['language'])
        else:
            # Insert text with proper line breaks
            self.preview.insert(tk.END, text)
        
        # Ensure text is properly displayed
        self.preview.configure(state='disabled')
        
        # Force update and scroll to end
        self.preview.update_idletasks()
        self.preview.see(tk.END)
        
        # Additional scroll to ensure we see the very end
        self.preview.yview_moveto(1.0)

    def _insert_preview_code_box(self, code, language):
        """Insert a code box into the preview panel"""
        # Create a frame for the code box with better styling
        code_frame = tk.Frame(
            self.preview,
            bg='#1e1e1e',  # Dark background
            relief='solid',
            bd=2,
            highlightbackground='#404040',  # Border color
            highlightthickness=1
        )
        
        # Language label with better styling
        if language and language != 'text':
            lang_label = tk.Label(
                code_frame,
                text=f" {language.upper()} ",
                bg='#007acc',  # Blue background for language label
                fg='#ffffff',  # White text
                font=('Consolas', 8, 'bold'),
                padx=8,
                pady=3
            )
            lang_label.pack(fill=tk.X, padx=2, pady=2)
        
        # Code text widget with better styling
        code_text = tk.Text(
            code_frame,
            bg='#2d2d2d',  # Slightly lighter background for code
            fg='#ffffff',  # Pure white text for maximum visibility
            insertbackground='#ffffff',
            relief='flat',
            font=('Consolas', 10),  # Keep Consolas for code, but ensure emoji support
            wrap='word',
            height=min(15, len(code.split('\n')) + 2),  # Dynamic height
            padx=10,
            pady=10,
            state='normal',  # Allow text to be visible
            selectbackground='#404040',  # Selection color
            selectforeground='#ffffff',   # Selection text color
            borderwidth=0
        )
        code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        code_text.insert('1.0', code)
        code_text.configure(state='disabled')  # Make read-only after inserting
        
        # Insert the code frame into the preview
        self.preview.window_create(tk.END, window=code_frame)
        self.preview.insert(tk.END, "\n")

    def run_command_and_capture_output(self, command, cwd=None):
        """Run a command and capture its output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=30
            )
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': 'Command timed out after 30 seconds',
                'returncode': -1,
                'success': False
            }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': f'Error running command: {str(e)}',
                'returncode': -1,
                'success': False
            }

    def save_as_pdf(self):
        """Save preview content as PDF"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            self.preview.configure(state='normal')
            content = self.preview.get('1.0', tk.END)
            self.preview.configure(state='disabled')
            
            for line in content.split('\n'):
                pdf.cell(0, 10, txt=line, ln=True)
            
            pdf.output(file_path)