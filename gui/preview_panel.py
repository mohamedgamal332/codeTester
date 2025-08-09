import tkinter as tk
from tkinter import ttk
from .theme import VSCodeTheme
from fpdf import FPDF
from tkinter import filedialog
import requests
import json
import threading
import subprocess
import sys
import os

class PreviewPanel:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.is_chat_visible = False
        self.chat_history = []  # Store chat conversation
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

        # Chat frame (initially hidden)
        self.setup_chat_frame()
        
        # Initially hide the chat
        self.is_chat_visible = False

    def setup_chat_frame(self):
        self.chat_frame = ttk.Frame(self.paned_window)
        
        # Chat display frame with scrollbar
        chat_display_frame = ttk.Frame(self.chat_frame)
        chat_display_frame.pack(fill=tk.BOTH, expand=True)

        # Enhanced font settings for chat display
        chat_font_family = VSCodeTheme.PREVIEW_FONT_FAMILY
        chat_font_size = VSCodeTheme.CHAT_FONT_SIZE  # Use dedicated chat font size

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
            
            # Create review prompt
            review_prompt = f"""Please review this code and provide feedback on:
1. Code quality and best practices
2. Potential bugs or issues
3. Performance improvements
4. Security concerns
5. Suggestions for better structure or readability

Here's the code to review:

```{current_file.suffix[1:] if current_file.suffix else 'text'}
{code_content}
```

Please provide a comprehensive review with specific suggestions for improvement."""

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
                    # Add the response with proper line breaks
                    self.add_text(response + "\n\n")
                    self.add_text("=" * 50 + "\n")
                    self.add_text("✅ Review completed successfully!\n")
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
            font=('Consolas', 10),
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
        """Apply code changes to the current file"""
        try:
            # Get the current active file from the main editor
            current_file = self._get_current_file()
            
            if not current_file:
                self.add_to_chat("❌ No file is currently open to apply changes to", is_user=False)
                return
            
            # Ask user for confirmation
            if not self._confirm_code_application(code_block, current_file):
                return
            
            # Apply the changes
            self._write_code_to_file(current_file, code_block['code'])
            
            # Refresh the editor
            self._refresh_editor(current_file)
            
            self.add_to_chat(f"✅ Code changes applied to {current_file.name}", is_user=False)
            
        except Exception as e:
            self.add_to_chat(f"❌ Error applying code changes: {str(e)}", is_user=False)

    def _get_current_file(self):
        """Get the currently active file from the main editor"""
        try:
            # Use direct reference to main application if available
            if hasattr(self, 'main_app') and self.main_app:
                return self.main_app.get_current_file()
            
            # Fallback: Get the main application instance by traversing up the widget hierarchy
            current_widget = self.frame
            while current_widget and not hasattr(current_widget, 'get_current_file'):
                current_widget = current_widget.master
            
            if current_widget and hasattr(current_widget, 'get_current_file'):
                return current_widget.get_current_file()
            else:
                # Try alternative approach - look for the main application
                for widget in self.frame.winfo_toplevel().winfo_children():
                    if hasattr(widget, 'get_current_file'):
                        return widget.get_current_file()
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
            font=('Consolas', 10),
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