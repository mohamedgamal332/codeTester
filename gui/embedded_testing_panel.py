import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from .theme import VSCodeTheme
from .embedded_frameworks import EmbeddedFrameworks

class EmbeddedTestingPanel:
    """GUI panel for embedded microcontroller testing"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.embedded_frameworks = EmbeddedFrameworks()
        self.current_framework = None
        self.test_running = False
        self.setup_panel()
    
    def setup_panel(self):
        """Setup the embedded testing panel"""
        # Main title
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = ttk.Label(
            title_frame,
            text="🔧 Embedded Microcontroller Testing",
            style='Dark.TLabel',
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # Framework selection section
        self.setup_framework_selection()
        
        # Control buttons section
        self.setup_control_buttons()
        
        # Status and output section
        self.setup_status_output()
        
        # Configuration section
        self.setup_configuration()
        
        # Load available frameworks
        self.load_frameworks()
    
    def setup_framework_selection(self):
        """Setup framework selection controls"""
        selection_frame = ttk.LabelFrame(self.frame, text="Framework Selection", padding=10)
        selection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Framework dropdown
        framework_frame = ttk.Frame(selection_frame)
        framework_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(framework_frame, text="Select Framework:", style='Dark.TLabel').pack(side=tk.LEFT)
        
        self.framework_var = tk.StringVar()
        self.framework_combo = ttk.Combobox(
            framework_frame,
            textvariable=self.framework_var,
            state='readonly',
            width=30
        )
        self.framework_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.framework_combo.bind('<<ComboboxSelected>>', self.on_framework_selected)
        
        # Framework info
        self.framework_info = ttk.Label(
            selection_frame,
            text="No framework selected",
            style='Dark.TLabel',
            wraplength=400
        )
        self.framework_info.pack(fill=tk.X, pady=5)
        
        # Validation button
        validate_btn = ttk.Button(
            selection_frame,
            text="🔍 Validate Framework",
            command=self.validate_current_framework
        )
        validate_btn.pack(pady=5)
    
    def setup_control_buttons(self):
        """Setup control buttons"""
        control_frame = ttk.LabelFrame(self.frame, text="Testing Controls", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Compile button
        self.compile_btn = ttk.Button(
            button_frame,
            text="🔨 Compile",
            command=self.compile_framework,
            style='Accent.TButton'
        )
        self.compile_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Flash button
        self.flash_btn = ttk.Button(
            button_frame,
            text="⚡ Flash",
            command=self.flash_framework,
            style='Accent.TButton'
        )
        self.flash_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Flash & Test button
        self.flash_test_btn = ttk.Button(
            button_frame,
            text="🚀 Flash & Test",
            command=self.flash_and_test,
            style='Accent.TButton'
        )
        self.flash_test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹️ Stop",
            command=self.stop_test,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Clear Output",
            command=self.clear_output
        )
        clear_btn.pack(side=tk.RIGHT)
    
    def setup_status_output(self):
        """Setup status and output display"""
        output_frame = ttk.LabelFrame(self.frame, text="Test Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Status indicator
        status_frame = ttk.Frame(output_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            style='Dark.TLabel',
            font=('Segoe UI', 10, 'bold')
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Output text area
        output_container = ttk.Frame(output_frame)
        output_container.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(
            output_container,
            bg=VSCodeTheme.EDITOR_BG,
            fg=VSCodeTheme.FOREGROUND,
            font=('Consolas', 10),
            wrap='word',
            state='disabled'
        )
        
        # Scrollbar for output
        output_scrollbar = ttk.Scrollbar(output_container, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_configuration(self):
        """Setup configuration options"""
        config_frame = ttk.LabelFrame(self.frame, text="Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Serial port configuration
        serial_frame = ttk.Frame(config_frame)
        serial_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(serial_frame, text="Serial Port:", style='Dark.TLabel').pack(side=tk.LEFT)
        
        self.serial_port_var = tk.StringVar(value='/dev/ttyUSB0')
        self.serial_port_combo = ttk.Combobox(
            serial_frame,
            textvariable=self.serial_port_var,
            width=15
        )
        self.serial_port_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Refresh ports button
        refresh_btn = ttk.Button(
            serial_frame,
            text="🔄 Refresh",
            command=self.refresh_serial_ports
        )
        refresh_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Baud rate configuration
        baud_frame = ttk.Frame(config_frame)
        baud_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(baud_frame, text="Baud Rate:", style='Dark.TLabel').pack(side=tk.LEFT)
        
        self.baudrate_var = tk.StringVar(value='115200')
        baudrate_combo = ttk.Combobox(
            baud_frame,
            textvariable=self.baudrate_var,
            values=['9600', '19200', '38400', '57600', '115200', '230400', '460800'],
            width=10
        )
        baudrate_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Timeout configuration
        timeout_frame = ttk.Frame(config_frame)
        timeout_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(timeout_frame, text="Timeout (seconds):", style='Dark.TLabel').pack(side=tk.LEFT)
        
        self.timeout_var = tk.StringVar(value='30')
        timeout_entry = ttk.Entry(timeout_frame, textvariable=self.timeout_var, width=10)
        timeout_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Load available serial ports
        self.refresh_serial_ports()
    
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
        
        if self.current_framework:
            # Update framework info
            info_text = f"Framework: {self.current_framework.display_name}\n"
            info_text += f"Description: {self.current_framework.description}\n"
            info_text += f"Compile Script: {self.current_framework.compile_script}\n"
            info_text += f"Output Path: {self.current_framework.output_path}\n"
            info_text += f"Serial Port: {self.current_framework.serial_port}\n"
            info_text += f"Baud Rate: {self.current_framework.baudrate}"
            
            self.framework_info.config(text=info_text)
            
            # Update configuration
            self.serial_port_var.set(self.current_framework.serial_port)
            self.baudrate_var.set(str(self.current_framework.baudrate))
            self.timeout_var.set(str(self.current_framework.timeout))
    
    def validate_current_framework(self):
        """Validate the current framework configuration"""
        if not self.current_framework:
            messagebox.showwarning("No Framework", "Please select a framework first.")
            return
        
        is_valid, errors = self.embedded_frameworks.validate_framework(self.current_framework.name)
        
        if is_valid:
            messagebox.showinfo("Validation", "Framework configuration is valid!")
        else:
            error_text = "Framework validation failed:\n\n" + "\n".join(errors)
            messagebox.showerror("Validation Failed", error_text)
    
    def refresh_serial_ports(self):
        """Refresh available serial ports"""
        ports = self.embedded_frameworks.get_available_serial_ports()
        self.serial_port_combo['values'] = ports
        if ports and not self.serial_port_var.get() in ports:
            self.serial_port_var.set(ports[0])
    
    def add_output(self, text, color=None):
        """Add text to the output area"""
        self.output_text.configure(state='normal')
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {text}\n")
        
        # Apply color if specified
        if color:
            # Find the line we just added
            lines = self.output_text.get('1.0', tk.END).split('\n')
            line_num = len(lines) - 2  # -2 because we added a newline
            if line_num > 0:
                start = f"{line_num}.0"
                end = f"{line_num}.end"
                self.output_text.tag_add(color, start, end)
        
        self.output_text.configure(state='disabled')
        self.output_text.see(tk.END)
    
    def clear_output(self):
        """Clear the output area"""
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.configure(state='disabled')
    
    def set_status(self, text, color='normal'):
        """Set the status text"""
        self.status_label.config(text=text)
        
        # Apply color
        if color == 'success':
            self.status_label.config(foreground='#28a745')
        elif color == 'error':
            self.status_label.config(foreground='#dc3545')
        elif color == 'warning':
            self.status_label.config(foreground='#ffc107')
        else:
            self.status_label.config(foreground=VSCodeTheme.FOREGROUND)
    
    def start_progress(self):
        """Start the progress bar"""
        self.progress_bar.start()
        self.test_running = True
        self.stop_btn.configure(state='normal')
        self.compile_btn.configure(state='disabled')
        self.flash_btn.configure(state='disabled')
        self.flash_test_btn.configure(state='disabled')
    
    def stop_progress(self):
        """Stop the progress bar"""
        self.progress_bar.stop()
        self.test_running = False
        self.stop_btn.configure(state='disabled')
        self.compile_btn.configure(state='normal')
        self.flash_btn.configure(state='normal')
        self.flash_test_btn.configure(state='normal')
    
    def compile_framework(self):
        """Compile the selected framework"""
        if not self.current_framework:
            messagebox.showwarning("No Framework", "Please select a framework first.")
            return
        
        self.start_progress()
        self.set_status("Compiling...", "warning")
        self.add_output("Starting compilation...", "warning")
        
        def compile_thread():
            success, output = self.embedded_frameworks.compile_framework(
                self.current_framework.name,
                callback=lambda line: self.add_output(f"  {line}")
            )
            
            # Update UI in main thread
            self.frame.after(0, lambda: self.compile_finished(success, output))
        
        threading.Thread(target=compile_thread, daemon=True).start()
    
    def compile_finished(self, success, output):
        """Handle compilation completion"""
        self.stop_progress()
        
        if success:
            self.set_status("Compilation successful", "success")
            self.add_output("✅ Compilation completed successfully", "success")
        else:
            self.set_status("Compilation failed", "error")
            self.add_output("❌ Compilation failed", "error")
            self.add_output(output)
    
    def flash_framework(self):
        """Flash the selected framework"""
        if not self.current_framework:
            messagebox.showwarning("No Framework", "Please select a framework first.")
            return
        
        self.start_progress()
        self.set_status("Flashing...", "warning")
        self.add_output("Starting flashing...", "warning")
        
        def flash_thread():
            success, output = self.embedded_frameworks.flash_framework(
                self.current_framework.name,
                callback=lambda line: self.add_output(f"  {line}")
            )
            
            # Update UI in main thread
            self.frame.after(0, lambda: self.flash_finished(success, output))
        
        threading.Thread(target=flash_thread, daemon=True).start()
    
    def flash_finished(self, success, output):
        """Handle flashing completion"""
        self.stop_progress()
        
        if success:
            self.set_status("Flashing successful", "success")
            self.add_output("✅ Flashing completed successfully", "success")
        else:
            self.set_status("Flashing failed", "error")
            self.add_output("❌ Flashing failed", "error")
            self.add_output(output)
    
    def flash_and_test(self):
        """Flash and test the framework"""
        if not self.current_framework:
            messagebox.showwarning("No Framework", "Please select a framework first.")
            return
        
        self.start_progress()
        self.set_status("Flashing and testing...", "warning")
        self.add_output("Starting flash and test sequence...", "warning")
        
        def flash_test_thread():
            # First flash
            flash_success, flash_output = self.embedded_frameworks.flash_framework(
                self.current_framework.name,
                callback=lambda line: self.add_output(f"[FLASH] {line}")
            )
            
            if not flash_success:
                self.frame.after(0, lambda: self.flash_finished(False, flash_output))
                return
            
            self.frame.after(0, lambda: self.add_output("✅ Flashing successful, starting serial monitoring...", "success"))
            
            # Then monitor serial
            test_success, test_output = self.embedded_frameworks.monitor_serial(
                self.current_framework.name,
                callback=lambda line: self.add_output(f"[SERIAL] {line}"),
                timeout_callback=lambda: self.add_output("⏰ Timeout reached", "warning")
            )
            
            # Update UI in main thread
            self.frame.after(0, lambda: self.test_finished(test_success, test_output))
        
        threading.Thread(target=flash_test_thread, daemon=True).start()
    
    def test_finished(self, success, output):
        """Handle test completion"""
        self.stop_progress()
        
        if success:
            self.set_status("Test PASSED", "success")
            self.add_output("🎉 Test completed successfully!", "success")
        else:
            self.set_status("Test FAILED", "error")
            self.add_output("💥 Test failed", "error")
        
        self.add_output(output)
    
    def stop_test(self):
        """Stop the current test"""
        self.test_running = False
        self.stop_progress()
        self.set_status("Test stopped", "warning")
        self.add_output("⏹️ Test stopped by user", "warning") 