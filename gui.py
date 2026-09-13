"""
GUI Application for Instagram DM Bot
Responsive menu for managing all bot commands
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import threading
import random
import time
import math
from datetime import datetime
from bot import InstagramBot
from config import Config
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class InstagramBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram DM Automation Bot")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        
        self.config = Config()
        self.bot = None
        self.is_running = False
        self.current_thread = None
        
        # Animation variables for 3D background
        self.animation_running = True
        self.particles = []
        self.grid_lines = []
        self.time_offset = 0
        
        # Futuristic dark theme styling
        self.setup_futuristic_theme()
        
        self.create_widgets()
        self.load_config()
        
        # Auto-connect to browser if configured
        self.auto_connect_browser()
        
        # Start 3D background animation
        self.start_3d_animation()
    
    def setup_futuristic_theme(self):
        """Setup futuristic dark theme with neon/pixel aesthetic"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Dark color scheme
        bg_color = "#0a0a0a"  # Almost black
        fg_color = "#00ff41"  # Neon green
        accent_color = "#00d9ff"  # Neon cyan
        border_color = "#1a1a1a"  # Dark gray
        hover_color = "#00ff88"  # Bright green
        text_color = "#e0e0e0"  # Light gray
        
        # Configure root background
        self.root.configure(bg=bg_color)
        
        # Configure styles - consistent throughout
        style.configure('TFrame', background=bg_color, borderwidth=0)
        style.configure('TLabel', background=bg_color, foreground=fg_color, 
                       font=('Consolas', 10))
        style.configure('TLabelFrame', background=bg_color, foreground=accent_color,
                       borderwidth=2, relief='solid', bordercolor=border_color)
        style.configure('TLabelFrame.Label', background=bg_color, foreground=accent_color,
                       font=('Consolas', 10, 'bold'))
        
        # Store colors for consistent use
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.accent_color = accent_color
        self.border_color = border_color
        self.hover_color = hover_color
        self.text_color = text_color
        
        # Buttons - futuristic style
        style.configure('TButton', background=bg_color, foreground=fg_color,
                       borderwidth=2, relief='solid', bordercolor=border_color,
                       font=('Consolas', 9), padding=8)
        style.map('TButton',
                 background=[('active', border_color), ('pressed', '#2a2a2a')],
                 foreground=[('active', hover_color)],
                 bordercolor=[('active', accent_color)])
        
        # Entry fields
        style.configure('TEntry', fieldbackground=bg_color, foreground=fg_color,
                       borderwidth=2, relief='solid', bordercolor=border_color,
                       insertcolor=accent_color, font=('Consolas', 10))
        style.map('TEntry',
                 bordercolor=[('focus', accent_color), ('!focus', border_color)])
        
        # Combobox
        style.configure('TCombobox', fieldbackground=bg_color, foreground=fg_color,
                       borderwidth=2, relief='solid', bordercolor=border_color,
                       arrowcolor=accent_color, font=('Consolas', 10))
        style.map('TCombobox',
                 fieldbackground=[('readonly', bg_color)],
                 bordercolor=[('focus', accent_color), ('!focus', border_color)])
        
        # Checkbutton
        style.configure('TCheckbutton', background=bg_color, foreground=fg_color,
                       font=('Consolas', 9))
        style.map('TCheckbutton',
                 background=[('active', bg_color)],
                 foreground=[('active', hover_color)])
        
        # Radiobutton
        style.configure('TRadiobutton', background=bg_color, foreground=fg_color,
                       font=('Consolas', 9))
        style.map('TRadiobutton',
                 background=[('active', bg_color)],
                 foreground=[('active', hover_color)])
        
        # Scrollbar
        style.configure('TScrollbar', background=bg_color, troughcolor=border_color,
                       borderwidth=0, arrowcolor=accent_color, darkcolor=border_color,
                       lightcolor=border_color)
        style.map('TScrollbar',
                 background=[('active', border_color)],
                 arrowcolor=[('active', hover_color)])
        
        # Notebook (if used)
        style.configure('TNotebook', background=bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', background=border_color, foreground=fg_color,
                       padding=[12, 8], font=('Consolas', 9))
        style.map('TNotebook.Tab',
                 background=[('selected', bg_color), ('active', border_color)],
                 foreground=[('selected', accent_color), ('active', hover_color)])
    
    def create_widgets(self):
        """Create all GUI widgets with 3D background"""
        # Create 3D background canvas (place first so it's behind everything)
        self.bg_canvas = tk.Canvas(self.root, bg="#0a0a0a", highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        # Canvas is already behind since it's created first
        
        # Initialize particles for 3D effect
        self.init_3d_particles()
        
        # Main container with dark background (transparent over canvas)
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Left sidebar with 3D neon border effect
        sidebar = tk.Frame(main_frame, width=220, bg="#0a0a0a", highlightbackground="#00d9ff", 
                          highlightthickness=2, highlightcolor="#00ff41")
        sidebar.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        sidebar.grid_propagate(False)
        main_frame.rowconfigure(0, weight=1)
        
        # Add inner glow effect to sidebar
        inner_frame = tk.Frame(sidebar, bg="#0a0a0a")
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Title in sidebar with 3D effect
        title_label = tk.Label(inner_frame, text="INSTABOT", font=('Consolas', 16, 'bold'),
                              bg="#0a0a0a", fg="#00ff41", 
                              relief='flat')
        title_label.pack(pady=(10, 20))
        
        # Add glow effect to title
        self.add_glow_effect(title_label)
        
        # Navigation buttons with 3D interactive styling
        nav_buttons = [
            ("🔐 LOGIN", self.show_login),
            ("💬 SINGLE DM", self.show_single_dm),
            ("📢 BULK MESSAGES", self.show_bulk_dm),
            ("💬 ALL DMs", self.show_send_all_dms),
            ("👥 FOLLOWERS", self.show_get_followers),
            ("📝 TEMPLATES", self.show_templates),
            ("📋 CONTACTS", self.show_contact_lists),
            ("⚙️ SETTINGS", self.show_settings),
            ("📊 STATS", self.show_statistics),
        ]
        
        self.nav_buttons = []
        for text, command in nav_buttons:
            btn = self.create_3d_button(inner_frame, text, command)
            btn.pack(fill=tk.X, pady=4, padx=5)
            self.nav_buttons.append(btn)
        
        # Main content area with split: Browser widget (left) and Content (right)
        content_container = tk.Frame(main_frame, bg="#0a0a0a", highlightbackground="#00d9ff",
                                    highlightthickness=2, highlightcolor="#00ff41")
        content_container.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_container.columnconfigure(0, weight=0)  # Browser widget (fixed width)
        content_container.columnconfigure(1, weight=1)  # Content area (flexible)
        content_container.rowconfigure(0, weight=1)
        
        # Browser Widget Panel (left side) - fixed width with futuristic border
        self.browser_widget = self.create_browser_widget(content_container)
        self.browser_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 8))
        self.browser_widget.config(width=300)  # Slightly wider for better visibility
        self.browser_widget.grid_propagate(False)
        
        # Content area (right side) with inner glow effect
        content_inner = tk.Frame(content_container, bg="#0a0a0a", highlightbackground="#1a1a1a",
                                 highlightthickness=1)
        content_inner.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(8, 0))
        content_inner.columnconfigure(0, weight=1)
        content_inner.rowconfigure(0, weight=1)
        
        self.content_frame = ttk.Frame(content_inner)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Status bar with neon effect
        self.status_var = tk.StringVar(value="[READY]")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                               font=('Consolas', 9, 'bold'))
        status_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Log area with dark theme
        log_frame = ttk.LabelFrame(main_frame, text="[ACTIVITY LOG]", padding="5")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD,
                                                 bg="#0a0a0a", fg="#00ff41", 
                                                 insertbackground="#00d9ff",
                                                 selectbackground="#1a1a1a",
                                                 selectforeground="#00ff41",
                                                 font=('Consolas', 9),
                                                 borderwidth=2, relief='solid')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Show login screen by default
        self.show_login()
    
    def create_browser_widget(self, parent):
        """Create embedded browser widget panel with service tabs"""
        browser_frame = tk.Frame(parent, bg="#0a0a0a", highlightbackground="#00d9ff",
                                highlightthickness=2, width=280)
        
        # Title
        title = tk.Label(browser_frame, text="🌐 BROWSER", font=('Consolas', 12, 'bold'),
                         bg="#0a0a0a", fg="#00ff41")
        title.pack(pady=(10, 5))
        
        # Browser status
        self.browser_status_label = tk.Label(browser_frame, text="Status: Not Connected",
                                            font=('Consolas', 9), bg="#0a0a0a", fg="#ff0040")
        self.browser_status_label.pack(pady=5)
        
        # Current page info
        self.browser_page_label = tk.Label(browser_frame, text="Page: None",
                                          font=('Consolas', 8), bg="#0a0a0a", fg="#00d9ff",
                                          wraplength=260, justify=tk.LEFT)
        self.browser_page_label.pack(pady=5, padx=10)
        
        # Service tabs/buttons
        services_frame = tk.LabelFrame(browser_frame, text="SERVICES", bg="#0a0a0a",
                                       fg="#00ff41", font=('Consolas', 9),
                                       highlightbackground="#1a1a1a", highlightthickness=1)
        services_frame.pack(fill=tk.X, padx=10, pady=10)
        
        service_buttons = [
            ("🏠 Home", "https://www.instagram.com/"),
            ("💬 DMs", "https://www.instagram.com/direct/inbox/"),
            ("👤 Profile", lambda: self.navigate_to_profile()),
            ("👥 Followers", lambda: self.navigate_to_followers()),
            ("📊 Activity", "https://www.instagram.com/accounts/activity/"),
        ]
        
        for text, action in service_buttons:
            btn = tk.Button(services_frame, text=text, font=('Consolas', 8),
                           bg="#1a1a1a", fg="#00ff41", activebackground="#2a2a2a",
                           activeforeground="#00d9ff", relief='flat', bd=1,
                           command=lambda a=action: self.browser_navigate(a) if isinstance(a, str) else a())
            btn.pack(fill=tk.X, pady=2, padx=5)
        
        # Browser controls
        controls_frame = tk.Frame(browser_frame, bg="#0a0a0a")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        connect_btn = tk.Button(controls_frame, text="🔌 Connect Browser",
                                font=('Consolas', 9), bg="#1a1a1a", fg="#00ff41",
                                activebackground="#2a2a2a", activeforeground="#00d9ff",
                                relief='flat', bd=1, command=self.init_persistent_browser)
        connect_btn.pack(fill=tk.X, pady=2)
        
        refresh_btn = tk.Button(controls_frame, text="🔄 Refresh",
                               font=('Consolas', 9), bg="#1a1a1a", fg="#00ff41",
                               activebackground="#2a2a2a", activeforeground="#00d9ff",
                               relief='flat', bd=1, command=self.refresh_browser_status)
        refresh_btn.pack(fill=tk.X, pady=2)
        
        # Browser info display
        info_frame = tk.LabelFrame(browser_frame, text="INFO", bg="#0a0a0a",
                                   fg="#00d9ff", font=('Consolas', 8),
                                   highlightbackground="#1a1a1a", highlightthickness=1)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.browser_info_text = scrolledtext.ScrolledText(info_frame, height=6, wrap=tk.WORD,
                                                           bg="#0a0a0a", fg="#00d9ff",
                                                           insertbackground="#00d9ff",
                                                           selectbackground="#1a1a1a",
                                                           selectforeground="#00ff41",
                                                           font=('Consolas', 7),
                                                           borderwidth=1, relief='solid')
        self.browser_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.browser_info_text.insert('1.0', "Browser widget ready.\nClick 'Connect Browser' to start.")
        self.browser_info_text.config(state=tk.DISABLED)
        
        return browser_frame
    
    def init_persistent_browser(self):
        """Initialize persistent browser window (one window, reused)"""
        if self.bot and self.bot.driver:
            self.log("Browser already connected")
            self.update_browser_status("Connected", self.bot.driver.current_url)
            return
        
        self.log("Initializing persistent browser...")
        self.update_browser_status("Connecting...", "")
        
        def init_thread():
            try:
                # Create bot instance
                self.bot = InstagramBot(headless=False)
                
                # Setup driver with persistent window
                self.bot.setup_driver(connect_existing=False)
                
                if self.bot.driver:
                    # Navigate to Instagram
                    self.bot.driver.get("https://www.instagram.com")
                    time.sleep(2)
                    
                    # Update status
                    current_url = self.bot.driver.current_url
                    self.root.after(0, lambda: self.update_browser_status("Connected", current_url))
                    self.root.after(0, lambda: self.log("✓ Browser connected! Please log in."))
                    self.root.after(0, lambda: self.browser_info_text.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.browser_info_text.delete('1.0', tk.END))
                    self.root.after(0, lambda: self.browser_info_text.insert('1.0', 
                        f"Browser connected!\nURL: {current_url}\n\nPlease log in to Instagram in the browser window."))
                    self.root.after(0, lambda: self.browser_info_text.config(state=tk.DISABLED))
                else:
                    self.root.after(0, lambda: self.update_browser_status("Failed", ""))
                    self.root.after(0, lambda: self.log("✗ Failed to initialize browser"))
            except Exception as e:
                self.root.after(0, lambda: self.update_browser_status("Error", ""))
                self.root.after(0, lambda: self.log(f"✗ Error: {str(e)}"))
        
        threading.Thread(target=init_thread, daemon=True).start()
    
    def browser_navigate(self, url):
        """Navigate browser to URL"""
        if not self.bot or not self.bot.driver:
            self.log("Browser not connected. Please connect first.")
            return
        
        def nav_thread():
            try:
                self.bot.driver.get(url)
                time.sleep(1)
                current_url = self.bot.driver.current_url
                self.root.after(0, lambda: self.update_browser_status("Connected", current_url))
                self.root.after(0, lambda: self.log(f"✓ Navigated to: {url}"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"✗ Navigation error: {str(e)}"))
        
        threading.Thread(target=nav_thread, daemon=True).start()
    
    def navigate_to_profile(self):
        """Navigate to current user's profile"""
        if not self.bot or not self.bot.driver:
            self.log("Browser not connected")
            return
        
        username = self.bot.get_current_username()
        if username:
            self.browser_navigate(f"https://www.instagram.com/{username}/")
        else:
            self.log("Could not determine username. Please log in first.")
    
    def navigate_to_followers(self):
        """Navigate to followers page"""
        if not self.bot or not self.bot.driver:
            self.log("Browser not connected")
            return
        
        username = self.bot.get_current_username()
        if username:
            self.browser_navigate(f"https://www.instagram.com/{username}/followers/")
        else:
            self.log("Could not determine username. Please log in first.")
    
    def refresh_browser_status(self):
        """Refresh browser status display"""
        if not self.bot or not self.bot.driver:
            self.update_browser_status("Not Connected", "")
            return
        
        try:
            current_url = self.bot.driver.current_url
            is_logged_in = self.bot.check_login_status()
            status = "Connected & Logged In" if is_logged_in else "Connected (Not Logged In)"
            self.update_browser_status(status, current_url)
            
            # Update info
            self.browser_info_text.config(state=tk.NORMAL)
            self.browser_info_text.delete('1.0', tk.END)
            info = f"Status: {status}\n"
            info += f"URL: {current_url}\n"
            if is_logged_in:
                username = self.bot.get_current_username()
                if username:
                    info += f"Account: {username}\n"
            self.browser_info_text.insert('1.0', info)
            self.browser_info_text.config(state=tk.DISABLED)
        except Exception as e:
            self.update_browser_status("Error", "")
            self.log(f"Error refreshing status: {str(e)}")
    
    def update_browser_status(self, status, url=""):
        """Update browser status display"""
        if "Connected" in status or "Logged In" in status:
            color = "#00ff41"  # Green
        elif "Error" in status or "Failed" in status:
            color = "#ff0040"  # Red
        else:
            color = "#00d9ff"  # Cyan
        
        self.browser_status_label.config(text=f"Status: {status}", fg=color)
        
        if url:
            # Truncate long URLs
            display_url = url if len(url) < 50 else url[:47] + "..."
            self.browser_page_label.config(text=f"Page: {display_url}")
        else:
            self.browser_page_label.config(text="Page: None")
    
    def init_3d_particles(self):
        """Initialize particles for 3D background effect"""
        self.particles = []
        for _ in range(50):
            self.particles.append({
                'x': random.randint(0, 1000),
                'y': random.randint(0, 750),
                'z': random.randint(100, 500),  # Depth
                'speed': random.uniform(0.5, 2.0),
                'size': random.randint(1, 3),
                'color': random.choice(['#00ff41', '#00d9ff', '#00ff88', '#00aaff'])
            })
    
    def start_3d_animation(self):
        """Start the 3D background animation"""
        if not self.animation_running:
            return
        
        self.animate_3d_background()
        self.root.after(50, self.start_3d_animation)  # ~20 FPS
    
    def animate_3d_background(self):
        """Animate 3D background with particles and grid"""
        if not hasattr(self, 'bg_canvas'):
            return
        
        canvas = self.bg_canvas
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Clear canvas
        canvas.delete("particle")
        canvas.delete("grid")
        
        # Update time offset
        self.time_offset += 0.02
        
        # Draw 3D grid
        self.draw_3d_grid(canvas, width, height)
        
        # Update and draw particles
        for particle in self.particles:
            # Move particle
            particle['y'] += particle['speed']
            if particle['y'] > height:
                particle['y'] = 0
                particle['x'] = random.randint(0, width)
            
            # Calculate 3D position (perspective)
            scale = 200 / (particle['z'] + 200)
            x = particle['x'] * scale + (width / 2) * (1 - scale)
            y = particle['y'] * scale + (height / 2) * (1 - scale)
            size = particle['size'] * scale
            
            # Draw particle with glow
            canvas.create_oval(x - size, y - size, x + size, y + size,
                             fill=particle['color'], outline=particle['color'],
                             tags="particle", width=0)
    
    def draw_3d_grid(self, canvas, width, height):
        """Draw 3D perspective grid"""
        center_x, center_y = width / 2, height / 2
        grid_spacing = 50
        depth = 300
        
        # Draw grid lines with perspective
        for i in range(-10, 11):
            # Horizontal lines
            z1 = -depth
            z2 = depth
            x1 = i * grid_spacing + center_x
            x2 = i * grid_spacing + center_x
            
            # Apply perspective
            scale1 = 200 / (z1 + 200)
            scale2 = 200 / (z2 + 200)
            
            y1 = center_y * scale1 + center_y * (1 - scale1)
            y2 = center_y * scale2 + center_y * (1 - scale2)
            
            x1_scaled = x1 * scale1 + center_x * (1 - scale1)
            x2_scaled = x2 * scale2 + center_x * (1 - scale2)
            
            if 0 <= y1 <= height and 0 <= y2 <= height:
                canvas.create_line(x1_scaled, y1, x2_scaled, y2,
                                 fill="#00d9ff", width=1, tags="grid", 
                                 stipple="gray25")
            
            # Vertical lines
            y1 = i * grid_spacing + center_y
            y2 = i * grid_spacing + center_y
            
            x1_scaled = center_x * scale1 + center_x * (1 - scale1)
            x2_scaled = center_x * scale2 + center_x * (1 - scale2)
            
            y1_scaled = y1 * scale1 + center_y * (1 - scale1)
            y2_scaled = y2 * scale2 + center_y * (1 - scale2)
            
            if 0 <= x1_scaled <= width and 0 <= x2_scaled <= width:
                canvas.create_line(x1_scaled, y1_scaled, x2_scaled, y2_scaled,
                                 fill="#00d9ff", width=1, tags="grid",
                                 stipple="gray25")
    
    def create_3d_button(self, parent, text, command):
        """Create a 3D interactive button"""
        btn_frame = tk.Frame(parent, bg="#0a0a0a", relief='flat')
        
        # Button with 3D effect
        btn = tk.Button(btn_frame, text=text, command=command,
                       bg="#1a1a1a", fg="#00ff41", 
                       font=('Consolas', 9, 'bold'),
                       relief='flat', borderwidth=0,
                       padx=15, pady=8,
                       cursor='hand2',
                       activebackground="#2a2a2a",
                       activeforeground="#00ff88")
        
        btn.pack(fill=tk.BOTH, expand=True)
        
        # Add hover effects
        def on_enter(e):
            btn.config(bg="#2a2a2a", fg="#00ff88")
            btn_frame.config(bg="#2a2a2a")
        
        def on_leave(e):
            btn.config(bg="#1a1a1a", fg="#00ff41")
            btn_frame.config(bg="#0a0a0a")
        
        def on_press(e):
            btn.config(bg="#3a3a3a")
        
        def on_release(e):
            btn.config(bg="#2a2a2a")
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)
        
        return btn_frame
    
    def add_glow_effect(self, widget):
        """Add glow effect to widget"""
        def update_glow():
            if not self.animation_running:
                return
            # Animate glow intensity
            intensity = int(128 + 127 * math.sin(self.time_offset * 2))
            color = f"#{intensity:02x}ff41"
            widget.config(fg=color)
            self.root.after(50, update_glow)
        
        update_glow()
    
    def log(self, message):
        """Add message to log with futuristic styling"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        # Color code messages
        if "✓" in message or "success" in message.lower():
            color = "#00ff41"  # Green
        elif "✗" in message or "error" in message.lower() or "failed" in message.lower():
            color = "#ff0040"  # Red
        elif "info" in message.lower():
            color = "#00d9ff"  # Cyan
        else:
            color = "#00ff41"  # Default green
        
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        # Apply color to the last line
        start = self.log_text.index("end-2l")
        end = self.log_text.index("end-1l")
        self.log_text.tag_add("colored", start, end)
        self.log_text.tag_config("colored", foreground=color)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """Update status bar with futuristic styling"""
        self.status_var.set(f"[{message.upper()}]")
        self.root.update_idletasks()
    
    def clear_content(self):
        """Clear main content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_login(self):
        """Show login screen"""
        self.clear_content()
        
        frame = ttk.Frame(self.content_frame, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="[LOGIN]", font=('Consolas', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Login method selection
        login_method_frame = ttk.LabelFrame(frame, text="[LOGIN METHOD]", padding="10")
        login_method_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.login_method_var = tk.StringVar(value="existing")
        ttk.Radiobutton(login_method_frame, text="🔗 Connect to Existing Browser (Recommended)", 
                       variable=self.login_method_var, value="existing",
                       command=self.toggle_login_method).pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(login_method_frame, text="🔓 Open New Browser & Login", 
                       variable=self.login_method_var, value="manual",
                       command=self.toggle_login_method).pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(login_method_frame, text="🤖 Auto Login (New Browser)", 
                       variable=self.login_method_var, value="auto",
                       command=self.toggle_login_method).pack(anchor=tk.W, pady=5)
        
        # Connect to existing browser section
        self.existing_frame = ttk.Frame(frame)
        self.existing_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        self.existing_frame.columnconfigure(1, weight=1)
        
        info_text_existing = "Connect to your existing Chrome browser with Instagram open.\n\nINSTRUCTIONS:\n1. Close all Chrome windows\n2. Open Chrome with remote debugging:\n   Windows: chrome.exe --remote-debugging-port=9222\n   Or use the 'Start Chrome for Bot' button below\n3. Log into Instagram in that browser\n4. Click 'Connect to Existing Browser'"
        ttk.Label(self.existing_frame, text=info_text_existing, foreground="#00d9ff", justify=tk.LEFT, 
                 font=('Consolas', 9)).grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        ttk.Label(self.existing_frame, text="Debug Port:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.debug_port_entry = ttk.Entry(self.existing_frame, width=10)
        self.debug_port_entry.insert(0, "9222")
        self.debug_port_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        button_frame_existing = ttk.Frame(self.existing_frame)
        button_frame_existing.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame_existing, text="Start Chrome for Bot", 
                  command=self.start_chrome_for_bot).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame_existing, text="Connect to Existing Browser", 
                  command=self.connect_existing_browser).pack(side=tk.LEFT, padx=5)
        
        # Manual login section
        self.manual_frame = ttk.Frame(frame)
        self.manual_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        self.manual_frame.columnconfigure(1, weight=1)
        
        info_text_manual = "Click 'Open Browser & Login Manually' to open Instagram.\nLog in manually in the browser, and the bot will detect when you're ready.\nThis method is safer and handles CAPTCHA/2FA smoothly."
        ttk.Label(self.manual_frame, text=info_text_manual, foreground=self.text_color, 
                 justify=tk.LEFT, font=('Consolas', 9)).grid(row=0, column=0, columnspan=2, pady=5)
        ttk.Button(self.manual_frame, text="Open Browser & Login Manually", 
                  command=self.manual_login).grid(row=1, column=0, columnspan=2, pady=10)
        
        # Check login status button (shown when bot exists)
        self.check_status_btn = ttk.Button(self.manual_frame, text="Check Login Status", 
                                          command=self.check_login_status)
        self.check_status_btn.grid(row=2, column=0, columnspan=2, pady=5)
        self.check_status_btn.grid_remove()  # Hidden initially
        
        # Auto login section
        self.auto_frame = ttk.Frame(frame)
        self.auto_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        self.auto_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.auto_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(self.auto_frame, width=30)
        self.username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(self.auto_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(self.auto_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Button(self.auto_frame, text="Auto Login & Open Browser", 
                  command=self.auto_login).grid(row=2, column=0, columnspan=2, pady=10)
        
        info_text_auto = "Enter credentials for automatic login.\nYou may still need to complete CAPTCHA or 2FA manually."
        ttk.Label(self.auto_frame, text=info_text_auto, foreground=self.text_color, 
                 justify=tk.LEFT, font=('Consolas', 9)).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Initially show existing browser connection
        self.toggle_login_method()
    
    def toggle_login_method(self):
        """Toggle between login methods"""
        method = self.login_method_var.get()
        if method == "existing":
            self.existing_frame.grid()
            self.manual_frame.grid_remove()
            self.auto_frame.grid_remove()
        elif method == "manual":
            self.existing_frame.grid_remove()
            self.manual_frame.grid()
            self.auto_frame.grid_remove()
        else:  # auto
            self.existing_frame.grid_remove()
            self.manual_frame.grid_remove()
            self.auto_frame.grid()
    
    def start_chrome_for_bot(self):
        """Start Chrome with remote debugging enabled"""
        import subprocess
        import os
        
        port = self.debug_port_entry.get().strip() or "9222"
        
        # Find Chrome executable
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
        
        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break
        
        if not chrome_path:
            messagebox.showerror("Error", "Chrome not found. Please start Chrome manually with:\nchrome.exe --remote-debugging-port=" + port)
            return
        
        try:
            # Start Chrome with remote debugging
            subprocess.Popen([chrome_path, f"--remote-debugging-port={port}", "--user-data-dir=" + os.path.join(os.getenv('TEMP'), 'chrome_debug')])
            self.log(f"✓ Started Chrome with remote debugging on port {port}")
            self.log("Please log into Instagram in the Chrome window that opened")
            messagebox.showinfo("Chrome Started", 
                             f"Chrome started with remote debugging on port {port}.\n\n"
                             "Please log into Instagram in the Chrome window.\n"
                             "Then click 'Connect to Existing Browser'")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start Chrome: {str(e)}")
            self.log(f"✗ Error starting Chrome: {str(e)}")
    
    def connect_existing_browser(self):
        """Connect to existing browser session"""
        port = self.debug_port_entry.get().strip() or "9222"
        
        try:
            port_num = int(port)
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return
        
        self.update_status("Connecting to existing browser...")
        self.log(f"Connecting to Chrome on port {port_num}...")
        
        def connect_thread():
            try:
                self.bot = InstagramBot(headless=False)
                success = self.bot.connect_to_existing_browser(debug_port=port_num)
                
                if success:
                    # Check login status
                    if self.bot.check_login_status():
                        # Get account username using bot method
                        account_username = self.bot.get_current_username()
                        
                        # Save connection settings
                        self.config.save_browser_connection(port_num, account_username, auto_connect=True)
                        
                        self.root.after(0, lambda: self.log("✓ Connected and logged in! Ready to use."))
                        self.root.after(0, lambda: self.update_status("Connected & Logged In"))
                        
                        # Auto-fetch followers if account detected
                        if account_username:
                            self.root.after(0, lambda: self.auto_fetch_followers(account_username))
                        
                        try:
                            if hasattr(self, 'check_status_btn'):
                                self.root.after(0, lambda: self.check_status_btn.grid())
                        except:
                            pass
                        self.root.after(0, lambda: messagebox.showinfo("Success", 
                            "Successfully connected to existing browser!\nYou're logged in and ready to use all features."))
                    else:
                        self.root.after(0, lambda: self.log("✓ Connected but not logged in. Please log in manually."))
                        self.root.after(0, lambda: self.update_status("Connected - Please Login"))
                        try:
                            if hasattr(self, 'check_status_btn'):
                                self.root.after(0, lambda: self.check_status_btn.grid())
                        except:
                            pass
                        self.root.after(0, lambda: messagebox.showwarning("Not Logged In", 
                            "Connected to browser but not logged in.\nPlease log into Instagram, then click 'Check Login Status'."))
                else:
                    self.root.after(0, lambda: self.log("✗ Failed to connect. Make sure Chrome is running with remote debugging."))
                    self.root.after(0, lambda: self.update_status("Connection Failed"))
                    self.root.after(0, lambda: messagebox.showerror("Connection Failed", 
                        f"Could not connect to Chrome on port {port_num}.\n\n"
                        "Make sure:\n"
                        "1. Chrome is running with: chrome.exe --remote-debugging-port=" + port + "\n"
                        "2. Or use 'Start Chrome for Bot' button"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Connection error: {str(e)}"))
                self.root.after(0, lambda: self.update_status("Error"))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def manual_login(self):
        """Handle manual login - open browser and wait for user to log in"""
        self.update_status("Opening browser...")
        self.log("Opening browser. Please log in manually in the browser window.")
        
        def login_thread():
            try:
                self.bot = InstagramBot(headless=False)
                success = self.bot.open_and_wait_for_login(timeout=300)  # 5 minutes timeout
                
                if success:
                    self.root.after(0, lambda: self.log("✓ Login detected! You're ready to use the bot."))
                    self.root.after(0, lambda: self.update_status("Logged in - Ready to use"))
                    try:
                        self.root.after(0, lambda: self.check_status_btn.grid() if hasattr(self, 'check_status_btn') else None)
                    except:
                        pass
                    self.root.after(0, lambda: messagebox.showinfo("Success", "Login detected! You can now use all bot features."))
                else:
                    self.root.after(0, lambda: self.log("✗ Login timeout. You can click 'Check Login Status' if you've logged in."))
                    self.root.after(0, lambda: self.update_status("Login timeout - Click 'Check Login Status' if logged in"))
                    try:
                        self.root.after(0, lambda: self.check_status_btn.grid() if hasattr(self, 'check_status_btn') else None)
                    except:
                        pass
                    self.root.after(0, lambda: messagebox.showwarning("Timeout", "Login timeout. If you've logged in, click 'Check Login Status'."))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {str(e)}"))
                self.root.after(0, lambda: self.update_status("Error"))
        
        threading.Thread(target=login_thread, daemon=True).start()
    
    def check_login_status(self):
        """Check current login status"""
        if not self.bot or not self.bot.driver:
            messagebox.showwarning("No Browser", "Please open browser first using 'Open Browser & Login Manually'")
            return
        
        self.update_status("Checking login status...")
        self.log("Checking if you're logged in...")
        
        def check_thread():
            try:
                is_logged_in = self.bot.check_login_status()
                if is_logged_in:
                    self.root.after(0, lambda: self.log("✓ You are logged in! Ready to use bot features."))
                    self.root.after(0, lambda: self.update_status("Logged in - Ready to use"))
                    self.root.after(0, lambda: messagebox.showinfo("Logged In", "You are logged in! You can now use all bot features."))
                else:
                    self.root.after(0, lambda: self.log("✗ Not logged in. Please log in manually in the browser."))
                    self.root.after(0, lambda: self.update_status("Not logged in"))
                    self.root.after(0, lambda: messagebox.showwarning("Not Logged In", "Please log in manually in the browser window, then check again."))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error checking status: {str(e)}"))
                self.root.after(0, lambda: self.update_status("Error"))
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def auto_login(self):
        """Handle automatic login with credentials"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        self.update_status("Logging in...")
        self.log(f"Attempting to login as {username}...")
        
        def login_thread():
            try:
                self.bot = InstagramBot(headless=False)
                success = self.bot.login(username, password)
                
                if success:
                    self.root.after(0, lambda: self.log("✓ Login successful! Browser is open."))
                    self.root.after(0, lambda: self.update_status("Logged in"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Login Failed", "Failed to login. Please check credentials and try again."))
                    self.root.after(0, lambda: self.update_status("Login failed"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Login error: {str(e)}"))
                self.root.after(0, lambda: self.update_status("Error"))
        
        threading.Thread(target=login_thread, daemon=True).start()
    
    def show_single_dm(self):
        """Show single DM screen"""
        self.clear_content()
        
        frame = ttk.Frame(self.content_frame, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="[SEND SINGLE DM]", font=('Consolas', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Option to use existing DM
        use_existing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Use existing DM conversation if available", 
                       variable=use_existing_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="Username:").grid(row=2, column=0, sticky=tk.W, pady=5)
        username_entry = ttk.Entry(frame, width=30)
        username_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="Message:").grid(row=3, column=0, sticky=tk.W, pady=5)
        message_text = scrolledtext.ScrolledText(frame, height=8, width=40,
                                                bg="#0a0a0a", fg="#00ff41",
                                                insertbackground="#00d9ff",
                                                selectbackground="#1a1a1a",
                                                selectforeground="#00ff41",
                                                font=('Consolas', 10),
                                                borderwidth=2, relief='solid')
        message_text.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        frame.rowconfigure(3, weight=1)
        
        # Template selector
        ttk.Label(frame, text="Template:").grid(row=4, column=0, sticky=tk.W, pady=5)
        template_var = tk.StringVar()
        template_combo = ttk.Combobox(frame, textvariable=template_var, state="readonly")
        templates = [t['name'] for t in self.config.get_templates()]
        template_combo['values'] = templates if templates else ['No templates']
        template_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        def load_template():
            template_name = template_var.get()
            if template_name and template_name != 'No templates':
                message_text.delete('1.0', tk.END)
                message_text.insert('1.0', self.config.get_template(template_name))
        
        ttk.Button(frame, text="Load Template", command=load_template).grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        def send_dm():
            if not self.bot or not self.bot.driver:
                messagebox.showerror("Error", "Please open browser and login first")
                return
            
            # Check login status
            if not self.bot.is_logged_in:
                if not self.bot.check_login_status():
                    messagebox.showerror("Error", "Please login first. Use the Login section to login.")
                    return
            
            username = username_entry.get().strip()
            message = message_text.get('1.0', tk.END).strip()
            
            if not username or not message:
                messagebox.showerror("Error", "Please enter username and message")
                return
            
            self.update_status(f"Sending DM to {username}...")
            self.log(f"Sending DM to {username}...")
            self.log("Opening DM in browser...")
            
            def send_thread():
                try:
                    use_existing = use_existing_var.get()
                    success = self.bot.send_dm_to_user(username, message, use_existing_dm=use_existing)
                    if success:
                        self.root.after(0, lambda: self.log(f"✓ Message sent to {username}"))
                        self.root.after(0, lambda: self.update_status("Message sent"))
                        self.config.log_message(username, message, "success")
                    else:
                        self.root.after(0, lambda: self.log(f"✗ Failed to send message to {username}"))
                        self.root.after(0, lambda: self.update_status("Failed"))
                        self.config.log_message(username, message, "failed")
                        self.root.after(0, lambda: messagebox.showwarning("Failed", f"Could not send message to {username}. Check:\n- Username is correct\n- You're logged in\n- Browser is open"))
                except Exception as e:
                    self.root.after(0, lambda: self.log(f"✗ Error: {str(e)}"))
                    self.root.after(0, lambda: self.update_status("Error"))
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to send DM: {str(e)}"))
            
            threading.Thread(target=send_thread, daemon=True).start()
        
        ttk.Button(frame, text="Send DM", command=send_dm).grid(row=6, column=0, columnspan=2, pady=20)
    
    def show_bulk_dm(self):
        """Show bulk DM screen"""
        self.clear_content()
        
        frame = ttk.Frame(self.content_frame, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(3, weight=1)
        
        ttk.Label(frame, text="[BULK MESSAGES]", font=('Consolas', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Source selection
        ttk.Label(frame, text="Message Source:").grid(row=1, column=0, sticky=tk.W, pady=5)
        source_var = tk.StringVar(value="manual")
        ttk.Radiobutton(frame, text="Manual List", variable=source_var, value="manual").grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Radiobutton(frame, text="Contact List", variable=source_var, value="contact_list").grid(row=1, column=1, sticky=tk.W, padx=(150, 0))
        ttk.Radiobutton(frame, text="Followers of User", variable=source_var, value="followers").grid(row=1, column=1, sticky=tk.W, padx=(300, 0))
        
        # Contact list selector
        ttk.Label(frame, text="Contact List:").grid(row=2, column=0, sticky=tk.W, pady=5)
        contact_list_var = tk.StringVar()
        contact_list_combo = ttk.Combobox(frame, textvariable=contact_list_var, state="readonly")
        contact_lists = list(self.config.get_contact_lists().keys())
        contact_list_combo['values'] = contact_lists if contact_lists else ['No contact lists']
        contact_list_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Followers input
        ttk.Label(frame, text="Target Username:").grid(row=3, column=0, sticky=tk.W, pady=5)
        followers_user_entry = ttk.Entry(frame, width=30)
        followers_user_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Manual list input
        ttk.Label(frame, text="Usernames (one per line):").grid(row=4, column=0, sticky=tk.W, pady=5)
        usernames_text = scrolledtext.ScrolledText(frame, height=8, width=40,
                                                   bg="#0a0a0a", fg="#00ff41",
                                                   insertbackground="#00d9ff",
                                                   selectbackground="#1a1a1a",
                                                   selectforeground="#00ff41",
                                                   font=('Consolas', 10),
                                                   borderwidth=2, relief='solid')
        usernames_text.grid(row=4, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        frame.rowconfigure(4, weight=1)
        
        # Message
        ttk.Label(frame, text="Message:").grid(row=5, column=0, sticky=tk.W, pady=5)
        message_text = scrolledtext.ScrolledText(frame, height=6, width=40,
                                                 bg="#0a0a0a", fg="#00ff41",
                                                 insertbackground="#00d9ff",
                                                 selectbackground="#1a1a1a",
                                                 selectforeground="#00ff41",
                                                 font=('Consolas', 10),
                                                 borderwidth=2, relief='solid')
        message_text.grid(row=5, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        
        # Template selector
        ttk.Label(frame, text="Template:").grid(row=6, column=0, sticky=tk.W, pady=5)
        template_var = tk.StringVar()
        template_combo = ttk.Combobox(frame, textvariable=template_var, state="readonly")
        templates = [t['name'] for t in self.config.get_templates()]
        template_combo['values'] = templates if templates else ['No templates']
        template_combo.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        def load_template():
            template_name = template_var.get()
            if template_name and template_name != 'No templates':
                message_text.delete('1.0', tk.END)
                message_text.insert('1.0', self.config.get_template(template_name))
        
        ttk.Button(frame, text="Load Template", command=load_template).grid(row=7, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Limits
        ttk.Label(frame, text="Max Messages:").grid(row=8, column=0, sticky=tk.W, pady=5)
        max_messages_entry = ttk.Entry(frame, width=10)
        max_messages_entry.insert(0, "50")
        max_messages_entry.grid(row=8, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        def send_bulk():
            if not self.bot or not self.bot.driver:
                messagebox.showerror("Error", "Please open browser and login first")
                return
            
            # Check login status
            if not self.bot.is_logged_in:
                if not self.bot.check_login_status():
                    messagebox.showerror("Error", "Please login first. Use the Login section to login.")
                    return
            
            message = message_text.get('1.0', tk.END).strip()
            if not message:
                messagebox.showerror("Error", "Please enter a message")
                return
            
            source = source_var.get()
            usernames = []
            
            if source == "manual":
                usernames_text_content = usernames_text.get('1.0', tk.END).strip()
                usernames = [u.strip() for u in usernames_text_content.split('\n') if u.strip()]
            elif source == "contact_list":
                list_name = contact_list_var.get()
                if list_name and list_name != 'No contact lists':
                    usernames = self.config.get_contact_list(list_name)
                else:
                    messagebox.showerror("Error", "Please select a contact list")
                    return
            elif source == "followers":
                target_user = followers_user_entry.get().strip()
                if not target_user:
                    messagebox.showerror("Error", "Please enter target username")
                    return
                self.log(f"Getting followers of {target_user} first...")
                self.update_status(f"Fetching followers of {target_user}...")
                
                # Get followers in thread
                def get_followers_thread():
                    try:
                        fetched = self.bot.get_followers_list(target_user, max_followers=100)
                        if fetched:
                            usernames.extend(fetched)
                            self.root.after(0, lambda: self.log(f"✓ Retrieved {len(fetched)} followers, starting bulk send..."))
                            # Continue with bulk send
                            self.root.after(0, lambda: start_bulk_send(usernames))
                        else:
                            self.root.after(0, lambda: messagebox.showerror("Error", "Could not retrieve followers"))
                            self.root.after(0, lambda: self.update_status("Failed to get followers"))
                    except Exception as e:
                        self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to get followers: {str(e)}"))
                        self.root.after(0, lambda: self.update_status("Error"))
                
                threading.Thread(target=get_followers_thread, daemon=True).start()
                return  # Exit early, bulk send will continue in thread
            
            if not usernames:
                messagebox.showerror("Error", "No usernames to send messages to")
                return
            
            start_bulk_send(usernames)
        
        def start_bulk_send(usernames):
            """Start the bulk sending process"""
            message = message_text.get('1.0', tk.END).strip()
            
            max_msgs = max_messages_entry.get().strip()
            try:
                max_msgs = int(max_msgs) if max_msgs.isdigit() else None
            except ValueError:
                max_msgs = None
            
            safety = self.config.get_safety_settings()
            delay_range = (safety.get('min_delay_seconds', 5), safety.get('max_delay_seconds', 10))
            
            if max_msgs:
                usernames = usernames[:max_msgs]
            
            self.update_status(f"Sending bulk messages to {len(usernames)} users...")
            self.log(f"Starting bulk send to {len(usernames)} users...")
            self.log("The browser will open DMs automatically. Please don't close the browser window.")
            
            def bulk_thread():
                try:
                    results = self.bot.send_bulk_messages(usernames, message, max_messages=None, delay_between=delay_range)
                    self.root.after(0, lambda: self.log(f"✓ Bulk send complete. Success: {len(results['success'])}, Failed: {len(results['failed'])}"))
                    self.root.after(0, lambda: self.update_status(f"Sent: {len(results['success'])}, Failed: {len(results['failed'])}"))
                    
                    # Log all messages
                    for username in results['success']:
                        self.config.log_message(username, message, "success")
                    for username in results['failed']:
                        self.config.log_message(username, message, "failed")
                    
                    # Show summary
                    if results['failed']:
                        self.root.after(0, lambda: self.log(f"Failed usernames: {', '.join(results['failed'][:10])}{'...' if len(results['failed']) > 10 else ''}"))
                    
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Bulk Send Complete", 
                        f"Successfully sent: {len(results['success'])}\nFailed: {len(results['failed'])}"
                    ))
                except Exception as e:
                    self.root.after(0, lambda: self.log(f"✗ Error during bulk send: {str(e)}"))
                    self.root.after(0, lambda: self.update_status("Error occurred"))
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Bulk send error: {str(e)}"))
            
            threading.Thread(target=bulk_thread, daemon=True).start()
        
        ttk.Button(frame, text="Send Bulk Messages", command=send_bulk).grid(row=9, column=0, columnspan=2, pady=20)
    
    def show_send_all_dms(self):
        """Show send to all existing DMs screen"""
        self.clear_content()
        
        frame = ttk.Frame(self.content_frame, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        
        ttk.Label(frame, text="[SEND TO ALL DMs]", font=('Consolas', 16, 'bold')).grid(row=0, column=0, pady=(0, 20))
        
        info_text = "This will send a message to ALL visible DM conversations.\nThe bot will click through each conversation directly in the DMs page and send the message."
        ttk.Label(frame, text=info_text, foreground=self.text_color, justify=tk.LEFT, 
                 font=('Consolas', 9)).grid(row=1, column=0, pady=10, sticky=tk.W)
        
        # Message input
        ttk.Label(frame, text="Message:").grid(row=2, column=0, sticky=tk.W, pady=5)
        message_text = scrolledtext.ScrolledText(frame, height=10, width=60,
                                                bg="#0a0a0a", fg="#00ff41",
                                                insertbackground="#00d9ff",
                                                selectbackground="#1a1a1a",
                                                selectforeground="#00ff41",
                                                font=('Consolas', 10),
                                                borderwidth=2, relief='solid')
        message_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        frame.rowconfigure(3, weight=1)
        
        # Template selector
        ttk.Label(frame, text="Template:").grid(row=4, column=0, sticky=tk.W, pady=5)
        template_var = tk.StringVar()
        template_combo = ttk.Combobox(frame, textvariable=template_var, state="readonly", width=40)
        templates = [t['name'] for t in self.config.get_templates()]
        template_combo['values'] = templates if templates else ['No templates']
        template_combo.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        def load_template():
            template_name = template_var.get()
            if template_name and template_name != 'No templates':
                message_text.delete('1.0', tk.END)
                message_text.insert('1.0', self.config.get_template(template_name))
        
        ttk.Button(frame, text="Load Template", command=load_template).grid(row=6, column=0, pady=5)
        
        # Status
        status_label = ttk.Label(frame, text="Ready", foreground=self.text_color, font=('Consolas', 9))
        status_label.grid(row=7, column=0, pady=10)
        
        def get_and_send_all():
            if not self.bot or not self.bot.driver:
                messagebox.showerror("Error", "Please open browser and login first")
                return
            
            if not self.bot.ensure_driver_connected():
                messagebox.showerror("Error", "Browser not connected")
                return
            
            message = message_text.get('1.0', tk.END).strip()
            if not message:
                messagebox.showerror("Error", "Please enter a message")
                return
            
            # Confirm before sending
            confirm = messagebox.askyesno(
                "Confirm Send",
                "Send message to ALL visible DM conversations?\n\nThe bot will click through each conversation in the DMs page and send the message."
            )
            
            if not confirm:
                return
            
            status_label.config(text="Starting... Opening DMs page...", foreground="blue")
            self.log("🚀 Starting direct DM send - working directly in DMs page...")
            
            def process_thread():
                try:
                    # DIRECT METHOD: Work directly in DMs page, click each conversation
                    success_count = 0
                    failed_count = 0
                    conversation_num = 0
                    
                    # Open DMs page
                    self.root.after(0, lambda: status_label.config(text="Opening DMs page...", foreground="blue"))
                    self.root.after(0, lambda: self.log("Opening DMs inbox..."))
                    
                    if not self.bot.ensure_driver_connected():
                        self.root.after(0, lambda: messagebox.showerror("Error", "Browser not connected"))
                        return
                    
                    # Navigate to inbox
                    current_url = self.bot.driver.current_url
                    if '/direct/' not in current_url:
                        if not self.bot.click_dm_icon():
                            self.bot.driver.get("https://www.instagram.com/direct/inbox/")
                            time.sleep(1)
                    else:
                        time.sleep(0.5)
                    
                    # Wait for conversations to load
                    wait = WebDriverWait(self.bot.driver, 10)
                    try:
                        wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/t/')]")))
                    except:
                        self.root.after(0, lambda: self.log("⚠️ No conversations found in inbox"))
                    
                    # Get safety settings for delays
                    safety = self.config.get_safety_settings()
                    delay_range = (max(1, safety.get('min_delay_seconds', 2)), max(2, safety.get('max_delay_seconds', 4)))
                    
                    # Scroll and click through ALL conversations directly
                    max_iterations = 100  # Safety limit
                    iteration = 0
                    processed_conversations = set()  # Track which we've done
                    
                    while iteration < max_iterations:
                        iteration += 1
                        
                        # Get all visible conversation links
                        all_conversations = self.bot.driver.execute_script("""
                            var conversations = [];
                            var links = document.querySelectorAll('a[href*="/direct/t/"]');
                            for (var i = 0; i < links.length; i++) {
                                var link = links[i];
                                var href = link.getAttribute('href');
                                if (href && href.includes('/direct/t/')) {
                                    var username = href.split('/direct/t/')[1].split('/')[0].split('?')[0];
                                    if (username && link.offsetParent !== null) {
                                        conversations.push({
                                            element: link,
                                            href: href,
                                            username: username
                                        });
                                    }
                                }
                            }
                            return conversations;
                        """)
                        
                        if not all_conversations:
                            self.root.after(0, lambda: self.log("No more conversations found"))
                            break
                        
                        # Process each conversation
                        found_new = False
                        for conv in all_conversations:
                            username = conv['username']
                            
                            # Skip if already processed
                            if username in processed_conversations:
                                continue
                            
                            found_new = True
                            conversation_num += 1
                            processed_conversations.add(username)
                            
                            self.root.after(0, lambda u=username, n=conversation_num: status_label.config(
                                text=f"Processing {n}: {u}...", foreground="blue"
                            ))
                            self.root.after(0, lambda u=username, n=conversation_num: self.log(f"[{n}] Clicking conversation: {u}..."))
                            
                            try:
                                # Click the conversation
                                self.bot.driver.execute_script("arguments[0].click();", conv['element'])
                                time.sleep(0.8)  # Fast wait for DM to open
                                
                                # Send message
                                if self.bot.send_message(message):
                                    success_count += 1
                                    self.config.log_message(username, message, "success")
                                    self.root.after(0, lambda u=username, n=conversation_num: self.log(f"✓ [{n}] Sent to {u}"))
                                else:
                                    failed_count += 1
                                    self.config.log_message(username, message, "failed")
                                    self.root.after(0, lambda u=username, n=conversation_num: self.log(f"✗ [{n}] Failed: {u}"))
                                
                                # Delay between messages (marketing speed)
                                delay = random.uniform(delay_range[0], delay_range[1])
                                time.sleep(delay)
                                
                            except Exception as e:
                                failed_count += 1
                                self.root.after(0, lambda u=username, e=str(e): self.log(f"✗ Error with {u}: {e}"))
                                time.sleep(0.5)
                        
                        # If no new conversations found, scroll down to load more
                        if not found_new:
                            # Scroll to load more conversations
                            scroll_container = self.bot.driver.find_element(By.TAG_NAME, "body")
                            self.bot.driver.execute_script(
                                "arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container
                            )
                            time.sleep(0.8)  # Wait for new conversations to load
                            
                            # Check if we're at the bottom (no more conversations)
                            scroll_height = self.bot.driver.execute_script("return arguments[0].scrollHeight", scroll_container)
                            scroll_top = self.bot.driver.execute_script("return arguments[0].scrollTop", scroll_container)
                            client_height = self.bot.driver.execute_script("return arguments[0].clientHeight", scroll_container)
                            
                            if scroll_top >= scroll_height - client_height - 50:
                                # At bottom, no more conversations
                                self.root.after(0, lambda: self.log("✓ Reached end of conversations list"))
                                break
                    
                    # Final summary
                    self.root.after(0, lambda: status_label.config(
                        text=f"✓ Complete! Sent: {success_count}, Failed: {failed_count}", 
                        foreground="green" if success_count > 0 else "red"
                    ))
                    self.root.after(0, lambda: self.log(f"✓ Complete! Sent: {success_count}, Failed: {failed_count}"))
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Complete",
                        f"Processed {conversation_num} conversations\nSent: {success_count}\nFailed: {failed_count}"
                    ))
                    
                except Exception as e:
                    error_msg = str(e)  # Capture exception in outer scope
                    self.root.after(0, lambda: status_label.config(text="Error occurred", foreground="red"))
                    self.root.after(0, lambda msg=error_msg: self.log(f"✗ Error: {msg}"))
                    self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", f"Failed: {msg}"))
            
            threading.Thread(target=process_thread, daemon=True).start()
        
        ttk.Button(frame, text="🚀 Send to All DMs (Direct)", command=get_and_send_all).grid(row=8, column=0, pady=20)
    
    def show_get_followers(self):
        """Show get followers screen"""
        self.clear_content()
        
        frame = ttk.Frame(self.content_frame, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="[GET FOLLOWERS]", font=('Consolas', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        username_entry = ttk.Entry(frame, width=30)
        username_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="Max Followers:").grid(row=2, column=0, sticky=tk.W, pady=5)
        max_followers_entry = ttk.Entry(frame, width=10)
        max_followers_entry.insert(0, "100")
        max_followers_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="Min Followers:").grid(row=3, column=0, sticky=tk.W, pady=5)
        min_followers_entry = ttk.Entry(frame, width=10)
        min_followers_entry.insert(0, "10")
        min_followers_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # OPTION D: Visual scroll indicator/progress display
        progress_frame = tk.Frame(frame, bg="#0a0a0a")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(1, weight=1)
        
        ttk.Label(progress_frame, text="Progress:", font=('Consolas', 9)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # Progress bar
        progress_var = tk.StringVar(value="Ready to start...")
        progress_label = tk.Label(progress_frame, textvariable=progress_var, 
                                  font=('Consolas', 9), bg="#0a0a0a", fg="#00d9ff",
                                  anchor=tk.W, justify=tk.LEFT)
        progress_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Detailed stats
        stats_var = tk.StringVar(value="")
        stats_label = tk.Label(progress_frame, textvariable=stats_var,
                              font=('Consolas', 8), bg="#0a0a0a", fg="#00ff41",
                              anchor=tk.W, justify=tk.LEFT)
        stats_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(frame, text="Followers:").grid(row=5, column=0, sticky=tk.W, pady=5)
        followers_text = scrolledtext.ScrolledText(frame, height=15, width=50,
                                                   bg="#0a0a0a", fg="#00ff41",
                                                   insertbackground="#00d9ff",
                                                   selectbackground="#1a1a1a",
                                                   selectforeground="#00ff41",
                                                   font=('Consolas', 10),
                                                   borderwidth=2, relief='solid')
        followers_text.grid(row=5, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        frame.rowconfigure(5, weight=1)
        
        def get_followers():
            if not self.bot:
                messagebox.showerror("Error", "Please open browser first using 'Open Browser & Login Manually'")
                return
            
            if not self.bot.driver:
                messagebox.showerror("Error", "Browser not open. Please use 'Open Browser & Login Manually' first.")
                return
            
            # Check driver connection
            if not self.bot.ensure_driver_connected():
                messagebox.showerror("Error", "Browser connection lost. Please reopen browser using 'Open Browser & Login Manually'")
                return
            
            # Check login status
            self.log("Checking login status...")
            if not self.bot.is_logged_in:
                self.log("Login status unknown, checking...")
                if not self.bot.check_login_status():
                    messagebox.showerror("Error", "Please login first. Use the Login section to login, then try again.")
                    return
                else:
                    self.log("✓ Login confirmed")
            
            username = username_entry.get().strip()
            if not username:
                messagebox.showerror("Error", "Please enter username")
                return
            
            try:
                max_followers = int(max_followers_entry.get().strip() or "100")
                min_followers = int(min_followers_entry.get().strip() or "10")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for min/max followers")
                return
            
            self.update_status(f"Getting followers of {username}...")
            self.log(f"Fetching followers of {username} (max: {max_followers}, min: {min_followers})...")
            self.log("This may take a few minutes. Please wait...")
            
            # OPTION D: Progress callback for visual indicator
            def progress_callback(progress_data):
                """Update GUI with real-time progress"""
                try:
                    scroll_count = progress_data.get('scroll_count', 0)
                    followers_found = progress_data.get('followers_found', 0)
                    target = progress_data.get('target', max_followers)
                    progress_pct = progress_data.get('progress_percent', 0)
                    no_change = progress_data.get('no_change_count', 0)
                    max_no_change = progress_data.get('max_no_change', 20)
                    estimated_remaining = progress_data.get('estimated_remaining', 0)
                    status = progress_data.get('status', 'scrolling')
                    new_found = progress_data.get('new_found', 0)
                    
                    if status == 'found_new' and new_found:
                        progress_text = f"📊 Scroll {scroll_count} | Found: {followers_found}/{target} ({progress_pct}%) | +{new_found} new"
                    else:
                        progress_text = f"📊 Scroll {scroll_count} | Found: {followers_found}/{target} ({progress_pct}%) | Remaining: ~{estimated_remaining}"
                    
                    stats_text = f"Status: {status.upper()} | No-change: {no_change}/{max_no_change} | Target: {target} (min: {min_followers})"
                    
                    self.root.after(0, lambda: progress_var.set(progress_text))
                    self.root.after(0, lambda: stats_var.set(stats_text))
                    
                    # Also log every 20 scrolls
                    if scroll_count % 20 == 0:
                        self.root.after(0, lambda: self.log(progress_text))
                except Exception as e:
                    pass  # Don't break if callback fails
            
            def fetch_thread():
                try:
                    # OPTION B & D: Pass progress callback
                    followers = self.bot.get_followers_list(username, max_followers, min_followers=min_followers, progress_callback=progress_callback)
                    
                    # OPTION D: Final progress update
                    self.root.after(0, lambda: progress_var.set(f"✓ Complete! Retrieved {len(followers) if followers else 0} followers"))
                    self.root.after(0, lambda: stats_var.set("Status: COMPLETE"))
                    
                    if followers:
                        followers_text.delete('1.0', tk.END)
                        followers_text.insert('1.0', '\n'.join(followers))
                        self.root.after(0, lambda: self.log(f"✓ Successfully retrieved {len(followers)} followers"))
                        self.root.after(0, lambda: self.update_status(f"Retrieved {len(followers)} followers"))
                        
                        # OPTION B: Warn if minimum not met
                        if len(followers) < min_followers:
                            self.root.after(0, lambda: self.log(f"⚠️ WARNING: Only retrieved {len(followers)} followers, but minimum requested was {min_followers}"))
                            self.root.after(0, lambda: messagebox.showwarning(
                                "Minimum Not Met",
                                f"Only retrieved {len(followers)} followers, but minimum requested was {min_followers}.\n\n"
                                "This might indicate:\n"
                                "- Account has fewer followers than requested\n"
                                "- Some followers are private/hidden\n"
                                "- Instagram rate limiting"
                            ))
                        
                        # Auto-save to contact list
                        if len(followers) > 0:
                            # Get account username if available
                            connection_settings = self.config.get_browser_connection()
                            account_username = connection_settings.get('connected_account')
                            
                            if account_username and username == account_username:
                                # Auto-save to auto-followers list
                                self.config.save_auto_followers(account_username, followers)
                                self.root.after(0, lambda: self.log(f"✓ Auto-saved {len(followers)} followers to contact list"))
                            
                            auto_save = messagebox.askyesno(
                                "Auto-Save", 
                                f"Found {len(followers)} followers. Would you like to save them to a contact list?"
                            )
                            if auto_save:
                                list_name = simpledialog.askstring(
                                    "Save Contact List", 
                                    f"Enter list name (default: '{username}_followers'):"
                                )
                                if not list_name:
                                    list_name = f"{username}_followers"
                                self.config.save_contact_list(list_name, followers)
                                self.root.after(0, lambda: self.log(f"✓ Auto-saved to '{list_name}'"))
                                self.root.after(0, lambda: messagebox.showinfo("Saved", f"Saved {len(followers)} followers to '{list_name}'"))
                    else:
                        self.root.after(0, lambda: self.log("✗ No followers retrieved. Make sure the username is correct and you're logged in."))
                        self.root.after(0, lambda: self.update_status("No followers found"))
                        self.root.after(0, lambda: messagebox.showwarning("No Followers", "Could not retrieve followers. Check:\n- Username is correct\n- You're logged in\n- Account is not private"))
                except Exception as e:
                    self.root.after(0, lambda: self.log(f"✗ Error: {str(e)}"))
                    self.root.after(0, lambda: self.update_status("Error occurred"))
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to get followers: {str(e)}"))
            
            threading.Thread(target=fetch_thread, daemon=True).start()
        
        def save_to_contact_list():
            followers_list = followers_text.get('1.0', tk.END).strip().split('\n')
            followers_list = [f.strip() for f in followers_list if f.strip()]
            
            if not followers_list:
                messagebox.showerror("Error", "No followers to save")
                return
            
            list_name = simpledialog.askstring("Save Contact List", "Enter list name:")
            if list_name:
                self.config.save_contact_list(list_name, followers_list)
                self.log(f"✓ Saved {len(followers_list)} usernames to '{list_name}'")
                messagebox.showinfo("Success", f"Saved {len(followers_list)} usernames to '{list_name}'")
        
        def test_connection():
            """Test browser connection"""
            if not self.bot or not self.bot.driver:
                messagebox.showerror("Error", "Browser not open. Please use 'Open Browser & Login Manually' first.")
                return
            
            self.log("Testing browser connection...")
            
            def test_thread():
                try:
                    # Test driver connection
                    if not self.bot.ensure_driver_connected():
                        self.root.after(0, lambda: self.log("✗ Browser connection failed"))
                        self.root.after(0, lambda: messagebox.showerror("Connection Failed", "Browser is not connected. Please reopen browser."))
                        return
                    
                    self.root.after(0, lambda: self.log("✓ Browser is connected"))
                    
                    # Test login status
                    self.root.after(0, lambda: self.log("Checking login status..."))
                    is_logged_in = self.bot.check_login_status()
                    
                    if is_logged_in:
                        self.root.after(0, lambda: self.log("✓ You are logged in"))
                        try:
                            current_url = self.bot.driver.current_url
                            self.root.after(0, lambda: self.log(f"Current URL: {current_url}"))
                        except:
                            pass
                        self.root.after(0, lambda: messagebox.showinfo("Connection Test", "✓ Browser connected\n✓ Logged in\n\nYou can now use bot features."))
                    else:
                        self.root.after(0, lambda: self.log("✗ Not logged in"))
                        self.root.after(0, lambda: messagebox.showwarning("Connection Test", "✓ Browser connected\n✗ Not logged in\n\nPlease log in manually in the browser."))
                        
                except Exception as e:
                    self.root.after(0, lambda: self.log(f"✗ Error: {str(e)}"))
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Connection test failed: {str(e)}"))
            
            threading.Thread(target=test_thread, daemon=True).start()
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="🔍 Test Connection", command=test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Get Followers", command=get_followers).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="Save to Contact List", command=save_to_contact_list).grid(row=5, column=0, columnspan=2, pady=10)
    
    def show_templates(self):
        """Show templates management screen"""
        self.clear_content()
        
        frame = ttk.Frame(self.content_frame, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        
        ttk.Label(frame, text="[MESSAGE TEMPLATES]", font=('Consolas', 16, 'bold')).grid(row=0, column=0, pady=(0, 20))
        
        # Template list
        list_frame = ttk.Frame(frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        list_frame.columnconfigure(0, weight=1)
        
        template_listbox = tk.Listbox(list_frame, height=8)
        template_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=template_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        template_listbox.config(yscrollcommand=scrollbar.set)
        
        def refresh_list():
            template_listbox.delete(0, tk.END)
            for template in self.config.get_templates():
                template_listbox.insert(tk.END, template['name'])
        
        refresh_list()
        
        # Template editor
        editor_frame = ttk.LabelFrame(frame, text="Edit Template", padding="10")
        editor_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        editor_frame.columnconfigure(0, weight=1)
        
        ttk.Label(editor_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(editor_frame, width=40)
        name_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(editor_frame, text="Message:").grid(row=2, column=0, sticky=tk.W, pady=5)
        message_text = scrolledtext.ScrolledText(editor_frame, height=8, width=50,
                                                bg="#0a0a0a", fg="#00ff41",
                                                insertbackground="#00d9ff",
                                                selectbackground="#1a1a1a",
                                                selectforeground="#00ff41",
                                                font=('Consolas', 10),
                                                borderwidth=2, relief='solid')
        message_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        editor_frame.rowconfigure(3, weight=1)
        
        def load_selected():
            selection = template_listbox.curselection()
            if selection:
                template_name = template_listbox.get(selection[0])
                name_entry.delete(0, tk.END)
                name_entry.insert(0, template_name)
                message_text.delete('1.0', tk.END)
                message_text.insert('1.0', self.config.get_template(template_name))
        
        def save_template():
            name = name_entry.get().strip()
            message = message_text.get('1.0', tk.END).strip()
            
            if not name or not message:
                messagebox.showerror("Error", "Please enter name and message")
                return
            
            self.config.add_template(name, message)
            refresh_list()
            self.log(f"✓ Template '{name}' saved")
            messagebox.showinfo("Success", f"Template '{name}' saved")
        
        def delete_template():
            selection = template_listbox.curselection()
            if not selection:
                messagebox.showerror("Error", "Please select a template to delete")
                return
            
            template_name = template_listbox.get(selection[0])
            if messagebox.askyesno("Confirm", f"Delete template '{template_name}'?"):
                self.config.delete_template(template_name)
                refresh_list()
                name_entry.delete(0, tk.END)
                message_text.delete('1.0', tk.END)
                self.log(f"✓ Template '{template_name}' deleted")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, pady=10)
        
        ttk.Button(button_frame, text="Load Selected", command=load_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Template", command=save_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Template", command=delete_template).pack(side=tk.LEFT, padx=5)
    
    def show_contact_lists(self):
        """Show contact lists management screen"""
        self.clear_content()
        
        frame = ttk.Frame(self.content_frame, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        ttk.Label(frame, text="[CONTACT LISTS]", font=('Consolas', 16, 'bold')).grid(row=0, column=0, pady=(0, 20))
        
        # List selection
        list_frame = ttk.Frame(frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        list_frame.columnconfigure(1, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        ttk.Label(list_frame, text="Contact Lists:").grid(row=0, column=0, sticky=tk.W, pady=5)
        list_var = tk.StringVar()
        list_combo = ttk.Combobox(list_frame, textvariable=list_var, state="readonly", width=30)
        contact_lists = list(self.config.get_contact_lists().keys())
        list_combo['values'] = contact_lists if contact_lists else ['No contact lists']
        list_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Download button
        download_btn = ttk.Button(list_frame, text="📥 Download List", 
                                  command=lambda: self.download_contact_list(list_var.get()))
        download_btn.grid(row=0, column=2, padx=10)
        
        ttk.Label(list_frame, text="Usernames:").grid(row=1, column=0, sticky=tk.W, pady=5)
        usernames_text = scrolledtext.ScrolledText(list_frame, height=15, width=50,
                                                   bg="#0a0a0a", fg="#00ff41",
                                                   insertbackground="#00d9ff",
                                                   selectbackground="#1a1a1a",
                                                   selectforeground="#00ff41",
                                                   font=('Consolas', 10),
                                                   borderwidth=2, relief='solid')
        usernames_text.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        
        def load_list():
            list_name = list_var.get()
            if list_name and list_name != 'No contact lists':
                usernames = self.config.get_contact_list(list_name)
                usernames_text.delete('1.0', tk.END)
                usernames_text.insert('1.0', '\n'.join(usernames))
                self.log(f"Loaded '{list_name}' with {len(usernames)} usernames")
        
        def save_list():
            list_name = list_var.get()
            if not list_name or list_name == 'No contact lists':
                list_name = simpledialog.askstring("Save Contact List", "Enter list name:")
                if not list_name:
                    return
            
            usernames_text_content = usernames_text.get('1.0', tk.END).strip()
            usernames = [u.strip() for u in usernames_text_content.split('\n') if u.strip()]
            
            self.config.save_contact_list(list_name, usernames)
            contact_lists = list(self.config.get_contact_lists().keys())
            list_combo['values'] = contact_lists if contact_lists else ['No contact lists']
            list_var.set(list_name)
            self.log(f"✓ Saved '{list_name}' with {len(usernames)} usernames")
            messagebox.showinfo("Success", f"Saved '{list_name}' with {len(usernames)} usernames")
        
        def delete_list():
            list_name = list_var.get()
            if not list_name or list_name == 'No contact lists':
                messagebox.showerror("Error", "Please select a contact list to delete")
                return
            
            if messagebox.askyesno("Confirm", f"Delete contact list '{list_name}'?"):
                self.config.delete_contact_list(list_name)
                contact_lists = list(self.config.get_contact_lists().keys())
                list_combo['values'] = contact_lists if contact_lists else ['No contact lists']
                list_var.set('')
                usernames_text.delete('1.0', tk.END)
                self.log(f"✓ Deleted contact list '{list_name}'")
        
        def import_from_file():
            filepath = filedialog.askopenfilename(
                title="Import Contact List",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filepath:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        usernames = [line.strip() for line in f.readlines() if line.strip()]
                    usernames_text.delete('1.0', tk.END)
                    usernames_text.insert('1.0', '\n'.join(usernames))
                    self.log(f"✓ Imported {len(usernames)} usernames from file")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to import file: {e}")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        def export_to_file():
            list_name = list_var.get()
            if not list_name or list_name == 'No contact lists':
                messagebox.showerror("Error", "Please select a contact list to export")
                return
            
            filepath = filedialog.asksaveasfilename(
                title="Download Contact List",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filepath:
                try:
                    usernames = self.config.get_contact_list(list_name)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        if filepath.endswith('.csv'):
                            f.write("Username\n")
                            for username in usernames:
                                f.write(f"{username}\n")
                        else:
                            f.write('\n'.join(usernames))
                    
                    self.log(f"✓ Downloaded '{list_name}' to {filepath}")
                    messagebox.showinfo("Success", f"Downloaded {len(usernames)} usernames to:\n{filepath}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to download: {str(e)}")
                    self.log(f"✗ Error downloading: {str(e)}")
        
        ttk.Button(button_frame, text="Load List", command=load_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save List", command=save_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete List", command=delete_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import from File", command=import_from_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📥 Download", command=export_to_file).pack(side=tk.LEFT, padx=5)
        
        list_combo.bind('<<ComboboxSelected>>', lambda e: load_list())
    
    def show_settings(self):
        """Show settings screen"""
        self.clear_content()
        
        frame = ttk.Frame(self.content_frame, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="[SETTINGS]", font=('Consolas', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        safety = self.config.get_safety_settings()
        
        ttk.Label(frame, text="[SAFETY SETTINGS]", font=('Consolas', 12, 'bold')).grid(row=1, column=0, columnspan=2, pady=(10, 10), sticky=tk.W)
        
        ttk.Label(frame, text="Min Delay (seconds):").grid(row=2, column=0, sticky=tk.W, pady=5)
        min_delay_entry = ttk.Entry(frame, width=10)
        min_delay_entry.insert(0, str(safety.get('min_delay_seconds', 5)))
        min_delay_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="Max Delay (seconds):").grid(row=3, column=0, sticky=tk.W, pady=5)
        max_delay_entry = ttk.Entry(frame, width=10)
        max_delay_entry.insert(0, str(safety.get('max_delay_seconds', 10)))
        max_delay_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="Daily Message Limit:").grid(row=4, column=0, sticky=tk.W, pady=5)
        daily_limit_entry = ttk.Entry(frame, width=10)
        daily_limit_entry.insert(0, str(safety.get('daily_message_limit', 50)))
        daily_limit_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="Hourly Message Limit:").grid(row=5, column=0, sticky=tk.W, pady=5)
        hourly_limit_entry = ttk.Entry(frame, width=10)
        hourly_limit_entry.insert(0, str(safety.get('hourly_message_limit', 10)))
        hourly_limit_entry.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        def save_settings():
            try:
                new_settings = {
                    'min_delay_seconds': int(min_delay_entry.get()),
                    'max_delay_seconds': int(max_delay_entry.get()),
                    'daily_message_limit': int(daily_limit_entry.get()),
                    'hourly_message_limit': int(hourly_limit_entry.get())
                }
                self.config.update_safety_settings(new_settings)
                self.log("✓ Settings saved")
                messagebox.showinfo("Success", "Settings saved successfully")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
        
        ttk.Button(frame, text="Save Settings", command=save_settings).grid(row=6, column=0, columnspan=2, pady=20)
    
    def show_statistics(self):
        """Show statistics screen"""
        self.clear_content()
        
        frame = ttk.Frame(self.content_frame, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="[STATISTICS]", font=('Consolas', 16, 'bold')).grid(row=0, column=0, pady=(0, 20))
        
        stats_text = scrolledtext.ScrolledText(frame, height=20, width=60,
                                               bg="#0a0a0a", fg="#00ff41",
                                               insertbackground="#00d9ff",
                                               selectbackground="#1a1a1a",
                                               selectforeground="#00ff41",
                                               font=('Consolas', 10),
                                               borderwidth=2, relief='solid',
                                               state=tk.DISABLED)
        stats_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.rowconfigure(1, weight=1)
        
        # Calculate statistics
        if self.bot:
            sent = self.bot.sent_messages_count
            failed = self.bot.failed_messages_count
            total = sent + failed
            success_rate = (sent / total * 100) if total > 0 else 0
        else:
            sent = failed = total = success_rate = 0
        
        logs = self.config.config.get('sent_messages_log', [])
        success_logs = [l for l in logs if l.get('status') == 'success']
        failed_logs = [l for l in logs if l.get('status') == 'failed']
        
        stats = f"""
Bot Statistics
{'='*50}

Current Session:
  Messages Sent: {sent}
  Messages Failed: {failed}
  Total Attempts: {total}
  Success Rate: {success_rate:.1f}%

All Time (from logs):
  Total Messages Sent: {len(success_logs)}
  Total Messages Failed: {len(failed_logs)}
  Total Messages: {len(logs)}

Configuration:
  Templates: {len(self.config.get_templates())}
  Contact Lists: {len(self.config.get_contact_lists())}
  
Safety Settings:
  Delay Range: {self.config.get_safety_settings().get('min_delay_seconds', 5)}-{self.config.get_safety_settings().get('max_delay_seconds', 10)} seconds
  Daily Limit: {self.config.get_safety_settings().get('daily_message_limit', 50)}
  Hourly Limit: {self.config.get_safety_settings().get('hourly_message_limit', 10)}
"""
        
        stats_text.insert('1.0', stats)
        stats_text.config(state=tk.DISABLED)
    
    def load_config(self):
        """Load configuration on startup"""
        self.log("Configuration loaded")
    
    def auto_connect_browser(self):
        """Auto-connect to browser on startup if configured"""
        connection_settings = self.config.get_browser_connection()
        if connection_settings.get('auto_connect', False):
            self.log("Auto-connecting to persistent browser...")
            self.update_status("Auto-connecting...")
            # Use persistent browser initialization
            self.init_persistent_browser()
    
    def auto_fetch_followers(self, account_username):
        """Automatically fetch and save all followers for the account"""
        # Check if we already have followers for this account
        existing = self.config.get_auto_followers(account_username)
        if existing and len(existing) > 0:
            self.log(f"Followers list already exists for {account_username} ({len(existing)} followers)")
            return
        
        self.log(f"Auto-fetching all followers for {account_username}...")
        self.update_status(f"Fetching followers for {account_username}...")
        
        def fetch_thread():
            try:
                # Get ALL followers (very high max to get everything)
                all_followers = self.bot.get_followers_list(account_username, max_followers=10000, min_followers=1)
                
                if all_followers:
                    # Save to auto-followers list
                    self.config.save_auto_followers(account_username, all_followers)
                    self.root.after(0, lambda: self.log(f"✓ Auto-saved {len(all_followers)} followers for {account_username}"))
                    self.root.after(0, lambda: self.update_status(f"Ready - {len(all_followers)} followers"))
                else:
                    self.root.after(0, lambda: self.log("✗ No followers found or error occurred"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"✗ Error auto-fetching followers: {str(e)}"))
        
        threading.Thread(target=fetch_thread, daemon=True).start()
    
    def on_closing(self):
        """Handle window closing"""
        if self.bot:
            self.bot.save_session()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = InstagramBotGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
