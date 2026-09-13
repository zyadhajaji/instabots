"""
Instagram DM Automation Bot
Core bot logic for sending messages and managing conversations
"""

import time
import random
import json
import os
import pyperclip
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class InstagramBot:
    def __init__(self, headless=False, delay_range=(0.5, 1.5)):
        """
        Initialize Instagram Bot
        
        Args:
            headless: Run browser in headless mode
            delay_range: Tuple of (min, max) seconds for random delays (optimized for speed)
        """
        self.delay_range = delay_range
        self.driver = None
        self.is_logged_in = False
        self.sent_messages_count = 0
        self.failed_messages_count = 0
        self.session_data = {}
        self.headless = headless
        
    def connect_to_existing_browser(self, debug_port=9222):
        """
        Connect to an existing Chrome browser instance using remote debugging
        
        Args:
            debug_port: Chrome remote debugging port (default 9222)
        
        Returns:
            bool: True if connected successfully
        """
        try:
            logger.info(f"Attempting to connect to existing Chrome browser on port {debug_port}...")
            
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
            
            # Try to use webdriver-manager if available
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except ImportError:
                # Fallback to system ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Test connection
            try:
                current_url = self.driver.current_url
                logger.info(f"✓ Successfully connected to existing browser! Current URL: {current_url}")
                return True
            except Exception as e:
                logger.error(f"Connected but couldn't access browser: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to existing browser: {e}")
            logger.info("Make sure Chrome is running with remote debugging enabled")
            return False
    
    def setup_driver(self, connect_existing=False, debug_port=9222):
        """
        Setup Chrome WebDriver with appropriate options
        
        Args:
            connect_existing: If True, connect to existing browser instead of creating new
            debug_port: Port for remote debugging (default 9222)
        """
        # If connecting to existing browser
        if connect_existing:
            if self.connect_to_existing_browser(debug_port):
                return
            else:
                logger.warning("Failed to connect to existing browser, creating new one...")
        
        # Create new browser instance
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Prevent detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Keep browser open and reuse window
        chrome_options.add_experimental_option("detach", True)
        
        # Use persistent user data directory to maintain session
        import os
        user_data_dir = os.path.join(os.getenv('APPDATA', ''), 'instabot_chrome_profile')
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        
        # Window management - keep one window
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')
        
        try:
            # Try to use webdriver-manager if available, otherwise use system ChromeDriver
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except ImportError:
                # Fallback to system ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize driver: {e}")
            logger.error("Make sure Chrome browser is installed and ChromeDriver is available")
            raise
    
    def human_delay(self, min_seconds=None, max_seconds=None):
        """Add random delay to mimic human behavior"""
        min_delay = min_seconds or self.delay_range[0]
        max_delay = max_seconds or self.delay_range[1]
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def open_instagram(self, connect_existing=False):
        """
        Open Instagram in browser or navigate if already open
        
        Args:
            connect_existing: If True, try to connect to existing browser first
        """
        if not self.driver:
            self.setup_driver(connect_existing=connect_existing)
        
        # Check if we're already on Instagram
        try:
            current_url = self.driver.current_url
            if 'instagram.com' in current_url:
                logger.info(f"Already on Instagram: {current_url}")
                # Just refresh to ensure we're logged in
                self.driver.refresh()
                self.human_delay(2, 3)
                return
        except:
            pass
        
        logger.info("Navigating to Instagram...")
        self.driver.get("https://www.instagram.com")
        self.human_delay(2, 4)
    
    def get_current_username(self):
        """Get the current logged-in Instagram username"""
        try:
            if not self.driver:
                return None
            
            # Try to get username from current page
            try:
                current_url = self.driver.current_url
                if '/accounts/edit/' in current_url:
                    username = self.driver.execute_script("""
                        var url = window.location.href;
                        if (url.includes('/accounts/edit/')) {
                            return url.split('/accounts/edit/')[1].split('/')[0];
                        }
                        return null;
                    """)
                    if username:
                        return username
            except:
                pass
            
            # Navigate to edit page to get username
            try:
                self.driver.get("https://www.instagram.com/accounts/edit/")
                time.sleep(1)
                username = self.driver.execute_script("""
                    var url = window.location.href;
                    if (url.includes('/accounts/edit/')) {
                        return url.split('/accounts/edit/')[1].split('/')[0];
                    }
                    return null;
                """)
                return username
            except:
                return None
        except:
            return None
    
    def check_login_status(self):
        """
        Check if user is already logged in to Instagram
        
        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            if not self.driver:
                logger.error("Driver is None")
                return False
            
            # Check if driver is still connected
            if not self.ensure_driver_connected():
                logger.error("Driver connection lost")
                return False
            
            # Refresh page to get current state
            try:
                current_url = self.driver.current_url
                logger.debug(f"Current URL: {current_url}")
                if 'instagram.com' not in current_url:
                    logger.info("Navigating to Instagram...")
                    self.driver.get("https://www.instagram.com")
                    time.sleep(3)
            except Exception as e:
                logger.warning(f"Error getting current URL: {e}, navigating to Instagram...")
                try:
                    self.driver.get("https://www.instagram.com")
                    time.sleep(3)
                except Exception as e2:
                    logger.error(f"Failed to navigate to Instagram: {e2}")
                    return False
            
            # Wait a bit for page to load
            time.sleep(1)
            
            # Check for elements that indicate logged-in status
            logged_in_indicators = [
                "//a[contains(@href, '/direct/inbox/')]",  # DM icon
                "//a[contains(@href, '/accounts/activity/')]",  # Activity icon
                "//a[contains(@href, '/accounts/edit/')]",  # Profile edit
                "//svg[@aria-label='Home']",  # Home icon
                "//a[contains(@aria-label, 'Home')]",  # Home link
                "//a[contains(@href, '/explore/')]",  # Explore icon
                "//div[contains(@role, 'button')]//img[contains(@alt, 'profile picture')]",  # Profile picture
            ]
            
            for xpath in logged_in_indicators:
                try:
                    element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    if element:
                        logger.info("Login detected - user is already logged in")
                        self.is_logged_in = True
                        return True
                except (NoSuchElementException, TimeoutException):
                    continue
            
            # Check for login form (indicates NOT logged in)
            try:
                login_form = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                if login_form:
                    logger.info("Login form detected - user is not logged in")
                    self.is_logged_in = False
                    return False
            except (NoSuchElementException, TimeoutException):
                pass
            
            # Check URL - if we're on login page, not logged in
            current_url = self.driver.current_url
            if '/accounts/login/' in current_url or '/accounts/emailsignup/' in current_url:
                logger.info("On login page - user is not logged in")
                self.is_logged_in = False
                return False
            
            # If we can't determine, check if we can access profile
            try:
                # Try to find any navigation element that requires login
                nav_elements = self.driver.find_elements(By.XPATH, "//nav")
                if nav_elements:
                    logger.info("Navigation found - assuming logged in")
                    self.is_logged_in = True
                    return True
            except:
                pass
            
            logger.warning("Could not determine login status")
            self.is_logged_in = False
            return False
            
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            self.is_logged_in = False
            return False
    
    def get_current_username(self):
        """Get the current logged-in Instagram username"""
        try:
            if not self.driver:
                return None
            
            # Try to get username from current page
            try:
                current_url = self.driver.current_url
                if '/accounts/edit/' in current_url:
                    username = self.driver.execute_script("""
                        var url = window.location.href;
                        if (url.includes('/accounts/edit/')) {
                            return url.split('/accounts/edit/')[1].split('/')[0];
                        }
                        return null;
                    """)
                    if username:
                        return username
            except:
                pass
            
            # Navigate to edit page to get username
            try:
                self.driver.get("https://www.instagram.com/accounts/edit/")
                time.sleep(1)
                username = self.driver.execute_script("""
                    var url = window.location.href;
                    if (url.includes('/accounts/edit/')) {
                        return url.split('/accounts/edit/')[1].split('/')[0];
                    }
                    return null;
                """)
                return username
            except:
                return None
        except:
            return None
    
    def check_login_status(self):
        """
        Check if user is already logged in to Instagram
        
        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            if not self.driver:
                logger.error("Driver is None")
                return False
            
            # Check if driver is still connected - try to reconnect if lost
            if not self.ensure_driver_connected(reconnect=True):
                logger.error("Driver connection lost and reconnection failed")
                return False
            
            # Refresh page to get current state
            try:
                current_url = self.driver.current_url
                logger.debug(f"Current URL: {current_url}")
                if 'instagram.com' not in current_url:
                    logger.info("Navigating to Instagram...")
                    self.driver.get("https://www.instagram.com")
                    time.sleep(3)
            except Exception as e:
                logger.warning(f"Error getting current URL: {e}, navigating to Instagram...")
                try:
                    self.driver.get("https://www.instagram.com")
                    time.sleep(3)
                except Exception as e2:
                    logger.error(f"Failed to navigate to Instagram: {e2}")
                    return False
            
            # Wait a bit for page to load
            time.sleep(1)
            
            # Check for elements that indicate logged-in status
            logged_in_indicators = [
                "//a[contains(@href, '/direct/inbox/')]",  # DM icon
                "//a[contains(@href, '/accounts/activity/')]",  # Activity icon
                "//a[contains(@href, '/accounts/edit/')]",  # Profile edit
                "//svg[@aria-label='Home']",  # Home icon
                "//a[contains(@aria-label, 'Home')]",  # Home link
                "//a[contains(@href, '/explore/')]",  # Explore icon
                "//div[contains(@role, 'button')]//img[contains(@alt, 'profile picture')]",  # Profile picture
            ]
            
            for xpath in logged_in_indicators:
                try:
                    element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    if element:
                        logger.info("Login detected - user is already logged in")
                        self.is_logged_in = True
                        return True
                except (NoSuchElementException, TimeoutException):
                    continue
            
            # Check for login form (indicates NOT logged in)
            try:
                login_form = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                if login_form:
                    logger.info("Login form detected - user is not logged in")
                    self.is_logged_in = False
                    return False
            except (NoSuchElementException, TimeoutException):
                pass
            
            # Check URL - if we're on login page, not logged in
            current_url = self.driver.current_url
            if '/accounts/login/' in current_url or '/accounts/emailsignup/' in current_url:
                logger.info("On login page - user is not logged in")
                self.is_logged_in = False
                return False
            
            # If we can't determine, check if we can access profile
            try:
                # Try to find any navigation element that requires login
                nav_elements = self.driver.find_elements(By.XPATH, "//nav")
                if nav_elements:
                    logger.info("Navigation found - assuming logged in")
                    self.is_logged_in = True
                    return True
            except:
                pass
            
            logger.warning("Could not determine login status")
            return False
            
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False
    
    def open_and_wait_for_login(self, timeout=300, connect_existing=False):
        """
        Open Instagram and wait for user to manually log in
        Can connect to existing browser session
        
        Args:
            timeout: Maximum seconds to wait for login (default 5 minutes)
            connect_existing: If True, connect to existing browser instead of opening new
        
        Returns:
            bool: True if login detected, False if timeout
        """
        try:
            if connect_existing:
                logger.info("Connecting to existing browser session...")
                if not self.driver:
                    if not self.connect_to_existing_browser():
                        logger.error("Could not connect to existing browser. Make sure Chrome is running with remote debugging.")
                        return False
                
                # Check if already logged in
                if self.check_login_status():
                    logger.info("✓ Already logged in! Ready to use.")
                    return True
                
                logger.info("Connected to existing browser. Checking login status...")
            else:
                self.open_instagram(connect_existing=False)
                logger.info("Browser opened. Please log in manually in the browser window.")
            
            logger.info(f"Waiting up to {timeout} seconds for you to log in...")
            
            start_time = time.time()
            check_interval = 3  # Check every 3 seconds
            
            while time.time() - start_time < timeout:
                if self.check_login_status():
                    logger.info("✓ Login detected! You're ready to use the bot.")
                    return True
                
                time.sleep(check_interval)
            
            logger.warning("Timeout waiting for login. Please try again.")
            return False
            
        except Exception as e:
            logger.error(f"Error in open_and_wait_for_login: {e}")
            return False
    
    def login(self, username, password):
        """
        Login to Instagram
        
        Args:
            username: Instagram username
            password: Instagram password
        """
        try:
            self.open_instagram()
            
            # Wait for login form
            wait = WebDriverWait(self.driver, 10)
            
            # Enter username
            username_input = wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.clear()
            self.human_delay(0.5, 1.5)
            username_input.send_keys(username)
            
            # Enter password
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.clear()
            self.human_delay(0.5, 1.5)
            password_input.send_keys(password)
            
            # Click login button
            self.human_delay(1, 2)
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            self.human_delay(3, 5)
            
            # Check for "Not Now" on save login info
            try:
                not_now_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                not_now_button.click()
                self.human_delay(1, 2)
            except TimeoutException:
                pass
            
            # Check for "Not Now" on notifications
            try:
                not_now_notif = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                not_now_notif.click()
                self.human_delay(1, 2)
            except TimeoutException:
                pass
            
            self.is_logged_in = True
            logger.info("Login successful")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            self.is_logged_in = False
            return False
    
    def scroll_to_element(self, element):
        """Fast scroll to element"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", element)
            time.sleep(0.2)  # Minimal delay
        except:
            pass
    
    def move_cursor_to_element(self, element):
        """Move cursor to element for visibility (fast)"""
        try:
            # Skip cursor movement for speed - just ensure element is visible
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", element)
            time.sleep(0.1)  # Minimal delay
        except:
            pass
    
    def click_dm_icon(self):
        """Click the DM/message icon in Instagram navigation"""
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Find DM icon using multiple strategies
            dm_icon_selectors = [
                "//a[contains(@href, '/direct/inbox/')]",
                "//a[contains(@href, '/direct/')]",
                "//svg[@aria-label='Direct']",
                "//svg[@aria-label='Messages']",
                "//a[@aria-label='Direct']",
                "//a[@aria-label='Messages']",
                "//div[@role='link']//a[contains(@href, '/direct/')]",
            ]
            
            for selector in dm_icon_selectors:
                try:
                    dm_icon = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    self.scroll_to_element(dm_icon)
                    self.move_cursor_to_element(dm_icon)
                    dm_icon.click()
                    time.sleep(1)  # Fast wait
                    logger.info("✓ Clicked DM icon")
                    return True
                except:
                    continue
            
            return False
        except Exception as e:
            logger.debug(f"Failed to click DM icon: {e}")
            return False
    
    def click_profile_from_current_page(self, username):
        """Click on a profile link from current page"""
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Try to find profile link
            profile_selectors = [
                f"//a[contains(@href, '/{username}/')]",
                f"//a[@href='/{username}/']",
                f"//a[contains(@href, '{username}')]//span[contains(text(), '{username}')]",
            ]
            
            for selector in profile_selectors:
                try:
                    profile_link = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    self.scroll_to_element(profile_link)
                    self.move_cursor_to_element(profile_link)
                    profile_link.click()
                    time.sleep(1)  # Fast wait
                    logger.info(f"✓ Clicked profile for {username}")
                    return True
                except:
                    continue
            
            return False
        except:
            return False
    
    def click_message_button(self):
        """Click the Message button on a profile page - FAST"""
        try:
            # JavaScript-first approach (fastest)
            clicked = self.driver.execute_script("""
                // Find all elements with "Message" text
                var allElements = document.querySelectorAll('*');
                for (var i = 0; i < allElements.length; i++) {
                    var el = allElements[i];
                    var text = (el.textContent || el.innerText || '').trim();
                    if (text === 'Message' && el.offsetParent !== null) {
                        el.click();
                        return true;
                    }
                }
                
                // Try links with /direct/t/ in href
                var links = document.querySelectorAll('a[href*="/direct/t/"]');
                for (var i = 0; i < links.length; i++) {
                    if (links[i].offsetParent !== null) {
                        links[i].click();
                        return true;
                    }
                }
                
                return false;
            """)
            
            if clicked:
                time.sleep(0.3)
                logger.info("✓ Clicked Message button")
                return True
            
            # Selenium fallback
            wait = WebDriverWait(self.driver, 3)
            message_button_selectors = [
                "//div[contains(text(), 'Message')]",
                "//a[contains(text(), 'Message')]",
                "//button[contains(text(), 'Message')]",
                "//a[contains(@href, '/direct/t/')]",
            ]
            
            for selector in message_button_selectors:
                try:
                    msg_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    self.driver.execute_script("arguments[0].click();", msg_button)
                    time.sleep(0.3)
                    logger.info("✓ Clicked Message button (Selenium)")
                    return True
                except:
                    continue
            
            return False
        except Exception as e:
            logger.debug(f"Failed to click Message button: {e}")
            return False
    
    def is_account_private(self, username=None):
        """
        Check if current profile page shows account is private - FAST
        
        Returns:
            bool: True if account is private, False otherwise
        """
        try:
            # Fast JavaScript check
            is_private = self.driver.execute_script("""
                var pageText = document.body.innerText || document.body.textContent || '';
                if (pageText.toLowerCase().includes('this account is private') || 
                    pageText.toLowerCase().includes('private account')) {
                    return true;
                }
                
                // Check for Follow button (indicates private if no posts visible)
                var followBtn = null;
                var buttons = document.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {
                    var text = (buttons[i].textContent || '').trim();
                    if (text === 'Follow' || text === 'Follow Back') {
                        followBtn = buttons[i];
                        break;
                    }
                }
                
                if (followBtn) {
                    // Check if posts are visible
                    var posts = document.querySelectorAll('article, [role="main"] img');
                    if (posts.length === 0) {
                        return true;
                    }
                }
                
                return false;
            """)
            
            if is_private:
                return True
            
            # Quick Selenium fallback
            try:
                private_text = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'This Account is Private')]"))
                )
                if private_text:
                    return True
            except:
                pass
            
            return False
        except:
            return False
    
    def handle_private_account_dm(self, username):
        """
        Handle DM for private account: Click 3 dots, select "Send message"
        ULTRA-AGGRESSIVE detection with multiple fallbacks for bulletproof operation
        
        Args:
            username: Instagram username
        """
        try:
            logger.info(f"Handling private account DM for {username}...")
            
            # Minimal wait for page load
            time.sleep(0.3)
            
            # ULTRA-AGGRESSIVE: Try ALL possible ways to find 3 dots menu
            logger.info("🔍 Ultra-aggressive 3 dots detection...")
            three_dots_clicked = self.driver.execute_script("""
                // Strategy 1: All possible selectors
                var selectors = [
                    'button[aria-label*="More options"]',
                    'button[aria-label*="Options"]',
                    'button[aria-label*="more"]',
                    'button[aria-label*="More"]',
                    'svg[aria-label*="More"]',
                    'svg[aria-label*="options"]',
                    'div[role="button"][aria-label*="More"]',
                    'div[role="button"][aria-label*="options"]',
                    'button[type="button"] svg',
                    'button svg[width="24"]',
                    'button svg[height="24"]',
                    'button:has(svg)',
                    '[data-testid*="more"]',
                    '[data-testid*="options"]'
                ];
                
                for (var s = 0; s < selectors.length; s++) {
                    try {
                        var elements = document.querySelectorAll(selectors[s]);
                        for (var i = 0; i < elements.length; i++) {
                            var el = elements[i];
                            // If SVG, get parent button
                            if (el.tagName === 'SVG') {
                                el = el.closest('button') || el.parentElement || el.parentElement?.parentElement;
                            }
                            if (!el || el.tagName !== 'BUTTON') continue;
                            
                            // Check visibility (relaxed check)
                            if (el.offsetParent !== null || el.getBoundingClientRect().width > 0) {
                                el.scrollIntoView({behavior: 'auto', block: 'center'});
                                el.click();
                                return true;
                            }
                        }
                    } catch(e) {}
                }
                
                // Strategy 2: Find ALL buttons and check for 3 dots pattern
                var allButtons = document.querySelectorAll('button');
                for (var b = 0; b < allButtons.length; b++) {
                    var btn = allButtons[b];
                    if (!btn.offsetParent && btn.getBoundingClientRect().width === 0) continue;
                    
                    var ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                    var hasSvg = btn.querySelector('svg') !== null;
                    var svgCount = btn.querySelectorAll('svg').length;
                    
                    // Look for buttons with SVG (likely 3 dots icon) near profile header
                    if (hasSvg && (ariaLabel.includes('more') || ariaLabel.includes('options') || svgCount > 0)) {
                        var rect = btn.getBoundingClientRect();
                        // Check if button is in top-right area of profile (where 3 dots usually are)
                        if (rect.top < window.innerHeight * 0.3 && rect.right > window.innerWidth * 0.5) {
                            btn.scrollIntoView({behavior: 'auto', block: 'center'});
                            btn.click();
                            return true;
                        }
                    }
                }
                
                // Strategy 3: Find Follow button and look for sibling button
                var followBtn = null;
                for (var f = 0; f < allButtons.length; f++) {
                    var btn = allButtons[f];
                    var text = (btn.textContent || btn.innerText || '').trim();
                    if (text === 'Follow' || text === 'Follow Back' || text === 'Message' || text === 'Following') {
                        followBtn = btn;
                        break;
                    }
                }
                
                if (followBtn) {
                    // Check parent container for other buttons
                    var parent = followBtn.parentElement;
                    while (parent && parent !== document.body) {
                        var siblings = parent.querySelectorAll('button');
                        for (var i = 0; i < siblings.length; i++) {
                            var btn = siblings[i];
                            if (btn !== followBtn && btn.offsetParent !== null) {
                                var hasSvg = btn.querySelector('svg') !== null;
                                if (hasSvg) {
                                    btn.scrollIntoView({behavior: 'auto', block: 'center'});
                                    btn.click();
                                    return true;
                                }
                            }
                        }
                        parent = parent.parentElement;
                    }
                }
                
                // Strategy 4: Click ANY button with SVG in profile header area
                var header = document.querySelector('header') || document.querySelector('[role="main"]') || document.body;
                if (header) {
                    var headerButtons = header.querySelectorAll('button');
                    for (var h = 0; h < headerButtons.length; h++) {
                        var btn = headerButtons[h];
                        if (btn.offsetParent !== null && btn.querySelector('svg')) {
                            btn.scrollIntoView({behavior: 'auto', block: 'center'});
                            btn.click();
                            return true;
                        }
                    }
                }
                
                return false;
            """)
            
            # If JavaScript failed, try Selenium with more selectors
            if not three_dots_clicked:
                logger.info("Trying Selenium fallback for 3 dots...")
                three_dots_selectors = [
                    "//button[@aria-label='More options']",
                    "//button[contains(@aria-label, 'More options')]",
                    "//button[contains(@aria-label, 'Options')]",
                    "//button[contains(@aria-label, 'more')]",
                    "//svg[@aria-label='More options']/ancestor::button",
                    "//svg[@aria-label='More']/ancestor::button",
                    "//div[@role='button'][contains(@aria-label, 'More')]",
                    "//button[.//svg[@width='24']]",
                    "//button[.//svg[@height='24']]",
                    "//button[.//svg]",
                ]
                
                for selector in three_dots_selectors:
                    try:
                        three_dots = WebDriverWait(self.driver, 1).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        if three_dots:
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", three_dots)
                            self.driver.execute_script("arguments[0].click();", three_dots)
                            logger.info("✓ Clicked 3 dots via Selenium")
                            three_dots_clicked = True
                            break
                    except:
                        continue
            
            if not three_dots_clicked:
                logger.error("✗ Could not find 3 dots menu")
                # For private accounts, we MUST use 3 dots - direct URL won't work
                # Try one more time with different approach
                logger.info("Retrying 3 dots detection with alternative method...")
                time.sleep(0.5)
                
                # Try finding by position (3 dots are usually top-right of profile header)
                try:
                    three_dots = self.driver.execute_script("""
                        // Find profile header section
                        var header = document.querySelector('header') || 
                                     document.querySelector('[role="main"]') ||
                                     document.querySelector('section');
                        
                        if (!header) return null;
                        
                        // Find all buttons in header
                        var buttons = header.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var btn = buttons[i];
                            if (!btn.offsetParent) continue;
                            
                            var rect = btn.getBoundingClientRect();
                            // 3 dots are usually in top-right area
                            if (rect.top < 200 && rect.right > window.innerWidth * 0.7) {
                                var hasSvg = btn.querySelector('svg') !== null;
                                if (hasSvg) {
                                    return btn;
                                }
                            }
                        }
                        return null;
                    """)
                    
                    if three_dots:
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", three_dots)
                        self.driver.execute_script("arguments[0].click();", three_dots)
                        logger.info("✓ Clicked 3 dots via position-based detection")
                        three_dots_clicked = True
                except:
                    pass
                
                if not three_dots_clicked:
                    logger.error("✗ All 3 dots detection methods failed - cannot proceed with private account")
                    return False
            
            # Wait for menu to appear (critical - menu needs time to render)
            time.sleep(1.0)  # Increased wait for menu animation
            
            # ULTRA-AGGRESSIVE: Find "Send message" option with multiple strategies
            logger.info("🔍 Finding 'Send message' option...")
            
            # Strategy 1: Search in visible menus first (most reliable - matches screenshot)
            send_msg_clicked = self.driver.execute_script("""
                // First, find all visible menus/dialogs (the popup menu from screenshot)
                var menus = document.querySelectorAll('div[role="menu"], div[role="dialog"], div[role="listbox"], div[role="presentation"]');
                for (var m = 0; m < menus.length; m++) {
                    var menu = menus[m];
                    // Check if menu is visible (the popup menu)
                    var rect = menu.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0 && menu.offsetParent !== null) {
                        // Search within this menu - look for "Send message" (exact match from screenshot)
                        var items = menu.querySelectorAll('div[role="menuitem"], div, a, button, span');
                        for (var j = 0; j < items.length; j++) {
                            var item = items[j];
                            var itemText = (item.textContent || item.innerText || '').trim();
                            var itemTextLower = itemText.toLowerCase();
                            var ariaLabel = (item.getAttribute('aria-label') || '').toLowerCase();
                            
                            // Exact match for "Send message" (as shown in screenshot - white text in menu)
                            if ((itemTextLower === 'send message' || itemTextLower.includes('send message') || 
                                 itemText === 'Send message' || itemText === 'Message' ||
                                 ariaLabel.includes('send message') || ariaLabel.includes('message')) &&
                                item.offsetParent !== null) {
                                // Make sure it's clickable
                                item.scrollIntoView({behavior: 'auto', block: 'center'});
                                item.click();
                                return true;
                            }
                        }
                    }
                }
                
                // Strategy 2: Search all menu items directly (more aggressive)
                var menuItems = document.querySelectorAll('div[role="menuitem"]');
                for (var i = 0; i < menuItems.length; i++) {
                    var item = menuItems[i];
                    var text = (item.textContent || item.innerText || '').trim();
                    var textLower = text.toLowerCase();
                    
                    // Look for "Send message" or "Message" (exact match)
                    if ((textLower === 'send message' || textLower.includes('send message') || 
                         text === 'Send message' || text === 'Message') &&
                        item.offsetParent !== null) {
                        item.scrollIntoView({behavior: 'auto', block: 'center'});
                        item.click();
                        return true;
                    }
                }
                
                // Strategy 3: Search all clickable elements (fallback)
                var allElements = document.querySelectorAll('div, a, button, span');
                for (var i = 0; i < allElements.length; i++) {
                    var el = allElements[i];
                    var text = (el.textContent || el.innerText || '').trim();
                    var textLower = text.toLowerCase();
                    var ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
                    
                    // Look for "Send message" or "Message" (exact match)
                    if ((textLower === 'send message' || textLower.includes('send message') || 
                         text === 'Send message' || text === 'Message' ||
                         ariaLabel.includes('send message') || ariaLabel.includes('message')) &&
                        el.offsetParent !== null) {
                        el.scrollIntoView({behavior: 'auto', block: 'center'});
                        el.click();
                        return true;
                    }
                }
                
                return false;
            """)
            
            # Retry with longer delay if needed (menu might still be animating)
            if not send_msg_clicked:
                time.sleep(1.0)  # Wait longer for menu animation
                send_msg_clicked = self.driver.execute_script("""
                    // Try menus again - look for "Send message" (exact match from screenshot)
                    var menus = document.querySelectorAll('div[role="menu"], div[role="dialog"]');
                    for (var m = 0; m < menus.length; m++) {
                        var menu = menus[m];
                        if (menu.offsetParent !== null) {
                            // Look for menu items first
                            var menuItems = menu.querySelectorAll('div[role="menuitem"]');
                            for (var j = 0; j < menuItems.length; j++) {
                                var item = menuItems[j];
                                var text = (item.textContent || item.innerText || '').trim();
                                var textLower = text.toLowerCase();
                                if ((textLower === 'send message' || textLower.includes('send message') || 
                                     text === 'Send message' || text === 'Message') &&
                                    item.offsetParent !== null) {
                                    item.click();
                                    return true;
                                }
                            }
                            
                            // Fallback: all items in menu
                            var items = menu.querySelectorAll('*');
                            for (var j = 0; j < items.length; j++) {
                                var item = items[j];
                                var text = (item.textContent || item.innerText || '').trim();
                                var textLower = text.toLowerCase();
                                if ((textLower === 'send message' || textLower.includes('send message') || 
                                     text === 'Send message' || text === 'Message') &&
                                    item.offsetParent !== null) {
                                    item.click();
                                    return true;
                                }
                            }
                        }
                    }
                    
                    // Fallback: all elements - look for "Send message" or "Message"
                    var allElements = document.querySelectorAll('*');
                    for (var i = 0; i < allElements.length; i++) {
                        var el = allElements[i];
                        var text = (el.textContent || el.innerText || '').trim();
                        var textLower = text.toLowerCase();
                        if ((textLower === 'send message' || textLower.includes('send message') || 
                             text === 'Send message' || text === 'Message') &&
                            el.offsetParent !== null) {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                """)
            
            # Selenium fallback - also look for just "Message"
            if not send_msg_clicked:
                send_message_selectors = [
                    "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send message')]",
                    "//*[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='message']",
                    "//*[contains(@aria-label, 'Send message')]",
                    "//*[contains(@aria-label, 'Message')]",
                    "//div[@role='menuitem']//*[contains(text(), 'Send message')]",
                    "//div[@role='menuitem']//*[text()='Message']",
                    "//a[contains(@href, '/direct/')]",
                ]
                
                for selector in send_message_selectors:
                    try:
                        send_msg = WebDriverWait(self.driver, 1).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        if send_msg:
                            self.driver.execute_script("arguments[0].click();", send_msg)
                            send_msg_clicked = True
                            break
                    except:
                        continue
            
            if not send_msg_clicked:
                logger.error("✗ Could not find 'Send message' option")
                # For private accounts, we MUST find "Send message" - no direct URL fallback
                # Try one more time with longer wait (menu might be animating)
                time.sleep(0.8)
                send_msg_clicked = self.driver.execute_script("""
                    // Search all clickable elements
                    var clickables = document.querySelectorAll('div[role="menuitem"], div[role="button"], a, button, div');
                    for (var i = 0; i < clickables.length; i++) {
                        var el = clickables[i];
                        var text = (el.textContent || el.innerText || '').trim().toLowerCase();
                        if (text.includes('send message') && el.offsetParent !== null) {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                """)
                
                if not send_msg_clicked:
                    logger.error("✗ Cannot proceed - 'Send message' option not found")
                    return False
            
            # Minimal wait for DM to open
            time.sleep(0.5)
            
            # Verify DM opened
            if self.find_message_input_improved(max_wait=3):
                logger.info("✓ Private account DM opened successfully")
                return True
            else:
                # For private accounts, direct URL won't work - must use 3 dots menu
                logger.warning("⚠ DM may not have opened - message input not found")
                return False
            
        except Exception as e:
            logger.error(f"✗ Error handling private account DM: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # For private accounts, direct URL won't work - must use 3 dots menu
            return False
    
    def navigate_to_dm(self, username, use_existing=True):
        """
        Navigate to DM - PROPER FLOW: Profile → Check Private → Click 3 dots OR Message button
        Based on best practices: Always go through profile page for reliable detection
        
        Args:
            username: Instagram username to message
            use_existing: If True, tries to open existing DM first
        """
        try:
            # STRATEGY 1: Quick existing DM check (if already in inbox) - FASTEST
            if use_existing and '/direct/' in self.driver.current_url:
                try:
                    logger.info(f"Checking existing DMs for {username}...")
                    # Fast JavaScript search for conversation
                    found = self.driver.execute_script("""
                        var links = document.querySelectorAll('a[href*="/direct/t/"]');
                        for (var i = 0; i < links.length; i++) {
                            var href = links[i].getAttribute('href');
                            if (href && href.includes('/direct/t/')) {
                                var user = href.split('/direct/t/')[1].split('/')[0].split('?')[0];
                                if (user === arguments[0] || user.includes(arguments[0])) {
                                    links[i].click();
                                    return true;
                                }
                            }
                        }
                        return false;
                    """, username)
                    
                    if found:
                        time.sleep(0.5)
                        if self.find_message_input_improved(max_wait=2):
                            logger.info("✓ Opened existing DM conversation")
                            return True
                except Exception as e:
                    logger.debug(f"Existing DM check failed: {e}")
            
            # OPTION A: Navigate to PROFILE FIRST (NO DIRECT URLS - Instagram blocks them)
            # Always use button clicks: Profile → Message button (public) or 3 dots → Send message (private)
            logger.info(f"Navigating to profile for {username}...")
            self.driver.get(f"https://www.instagram.com/{username}/")
            time.sleep(0.7)  # Wait for profile to load
            
            # Check if account is private
            is_private = self.is_account_private(username)
            
            if is_private:
                # PRIVATE ACCOUNT: Use 3 dots menu → "Send message" (as shown in screenshot)
                logger.info("🔒 Account is PRIVATE - using 3 dots menu → Send message...")
                if self.handle_private_account_dm(username):
                    return True
                else:
                    logger.error(f"✗ Failed to open DM for private account {username}")
                    return False
            else:
                # PUBLIC ACCOUNT: Use Message button ONLY (no direct URLs)
                logger.info("✓ Account is PUBLIC - clicking Message button...")
                if self.click_message_button():
                    time.sleep(0.6)
                    if self.find_message_input_improved(max_wait=4):
                        logger.info("✓ Opened DM via Message button")
                        return True
                    else:
                        logger.warning("Message button clicked but DM didn't open")
                else:
                    logger.warning("Could not find/click Message button")
            
            logger.error(f"✗ All DM navigation methods failed for {username}")
            return False
            
        except Exception as e:
            logger.error(f"✗ Failed to navigate to DM for {username}: {e}")
            return False
    
    def find_message_input_improved(self, max_wait=5):
        """Find message input using fast methods"""
        wait = WebDriverWait(self.driver, max_wait)
        
        # Strategy 1: JavaScript find (most reliable for Instagram)
        try:
            input_found = self.driver.execute_script("""
                // Find textarea with message placeholder
                var textarea = document.querySelector('textarea[placeholder*="Message" i], textarea[placeholder*="message" i]');
                if (textarea && textarea.offsetParent !== null) {
                    return {type: 'textarea', element: textarea};
                }
                
                // Find contenteditable divs
                var divs = document.querySelectorAll('div[contenteditable="true"]');
                for (var i = 0; i < divs.length; i++) {
                    var div = divs[i];
                    var placeholder = (div.getAttribute('placeholder') || div.getAttribute('aria-label') || '').toLowerCase();
                    var role = div.getAttribute('role') || '';
                    
                    if (placeholder.includes('message') || role === 'textbox' || 
                        div.closest('[role="textbox"]') || div.closest('form')) {
                        if (div.offsetParent !== null) {
                            return {type: 'div', element: div};
                        }
                    }
                }
                
                // Return first visible contenteditable
                for (var i = 0; i < divs.length; i++) {
                    if (divs[i].offsetParent !== null) {
                        return {type: 'div', element: divs[i]};
                    }
                }
                
                return null;
            """)
            
            if input_found:
                # Find element using Selenium
                if input_found['type'] == 'textarea':
                    try:
                        element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
                        if element.is_displayed():
                            return element
                    except:
                        pass
                
                # Try to find by contenteditable
                try:
                    element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']")))
                    if element.is_displayed():
                        return element
                except:
                    pass
        except Exception as e:
            logger.debug(f"JavaScript find failed: {e}")
        
        # Strategy 2: Selenium find with multiple selectors
        selectors = [
            "//textarea[contains(@placeholder, 'Message')]",
            "//textarea[contains(@placeholder, 'message')]",
            "//div[@contenteditable='true'][@role='textbox']",
            "//div[@contenteditable='true']",
            "//textarea",
        ]
        
        for selector in selectors:
            try:
                element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                if element.is_displayed():
                    return element
            except:
                continue
        
        return None
    
    def send_message(self, message_text):
        """
        Send a text message using improved methods with clipboard paste
        
        Args:
            message_text: Text message to send
        """
        try:
            logger.info("Finding message input...")
            
            # Find input with improved method
            message_input = self.find_message_input_improved()
            if not message_input:
                logger.error("Could not find message input element")
                return False
            
            logger.info("✓ Found message input")
            
            # Ultra-fast scroll and focus
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", message_input)
            time.sleep(0.1)  # Reduced from 0.2
            
            # Click to focus (ultra-fast)
            try:
                message_input.click()
            except:
                self.driver.execute_script("arguments[0].click();", message_input)
            
            time.sleep(0.2)  # Reduced from 0.3
            
            # Clear existing content (fast)
            try:
                if message_input.tag_name == 'textarea':
                    message_input.clear()
                else:
                    # For contenteditable divs - clear using JavaScript
                    self.driver.execute_script("arguments[0].innerHTML = '';", message_input)
            except:
                pass
            
            time.sleep(0.05)  # Ultra-minimal wait
            
            # PASTE MESSAGE using clipboard (ultra-fast - skip verification)
            logger.info("Pasting message...")
            
            # Ensure message is in clipboard
            try:
                pyperclip.copy(message_text)
                time.sleep(0.05)  # Ultra-fast clipboard copy
            except Exception as e:
                logger.error(f"Failed to copy to clipboard: {e}")
                return False
            
            # Paste using Ctrl+V (ultra-fast - no verification)
            try:
                message_input.send_keys(Keys.CONTROL + "v")
                time.sleep(0.2)  # Ultra-fast wait time - just enough for paste to register
                logger.info("✓ Message pasted")
                    
            except Exception as e:
                logger.debug(f"Standard paste failed: {e}, trying JavaScript paste...")
                
                # Alternative: JavaScript paste
                try:
                    self.driver.execute_script("""
                        var input = arguments[0];
                        var text = arguments[1];
                        
                        // Clear first
                        input.textContent = '';
                        input.innerHTML = '';
                        
                        // Set text
                        if (input.tagName === 'TEXTAREA') {
                            input.value = text;
                        } else {
                            input.textContent = text;
                        }
                        
                        // Trigger events
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        input.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true }));
                    """, message_input, message_text)
                    
                    self.human_delay(0.5, 1)
                    logger.info("✓ Message set via JavaScript")
                except Exception as e2:
                    logger.error(f"All paste methods failed: {e2}")
                    return False
            
            time.sleep(0.2)  # Wait for paste to register
            
            # Send message - MULTIPLE METHODS to ensure it works
            logger.info("Sending message...")
            
            # Method 1: Enter key (fastest and most reliable)
            try:
                message_input.send_keys(Keys.RETURN)
                time.sleep(0.3)
                logger.info(f"✓ Message sent via Enter key")
                self.sent_messages_count += 1
                return True
            except Exception as e:
                logger.debug(f"Enter key failed: {e}")
            
            # Method 2: Find and click send button
            try:
                send_button = self.driver.execute_script("""
                    var buttons = document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {
                        var btn = buttons[i];
                        var ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                        var text = (btn.textContent || btn.innerText || '').trim().toLowerCase();
                        if ((ariaLabel.includes('send') || text === 'send' || ariaLabel.includes('post')) &&
                            btn.offsetParent !== null) {
                            return btn;
                        }
                    }
                    return null;
                """)
                
                if send_button:
                    self.driver.execute_script("arguments[0].click();", send_button)
                    time.sleep(0.3)
                    logger.info(f"✓ Message sent via Send button")
                    self.sent_messages_count += 1
                    return True
            except Exception as e:
                logger.debug(f"Send button failed: {e}")
            
            # Method 3: JavaScript Enter event
            try:
                self.driver.execute_script("""
                    var input = arguments[0];
                    var event = new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        which: 13,
                        bubbles: true
                    });
                    input.dispatchEvent(event);
                    input.dispatchEvent(new KeyboardEvent('keyup', {
                        key: 'Enter',
                        keyCode: 13,
                        bubbles: true
                    }));
                """, message_input)
                time.sleep(0.3)
                logger.info(f"✓ Message sent via JavaScript event")
                self.sent_messages_count += 1
                return True
            except Exception as e:
                logger.error(f"All send methods failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.failed_messages_count += 1
            return False
    
    def send_dm_to_user(self, username, message_text, use_existing_dm=True):
        """
        Send DM to a specific user - supports existing and new DMs
        
        Args:
            username: Instagram username
            message_text: Message to send
            use_existing_dm: If True, tries to open existing DM first
        """
        try:
            # Check driver connection first - try to reconnect if lost
            if not self.ensure_driver_connected(reconnect=True):
                logger.error("Browser driver not connected. Please reconnect browser.")
                return False
            
            # Check login status
            if not self.is_logged_in:
                logger.warning("Login status unknown, checking...")
                if not self.check_login_status():
                    logger.error("Not logged in. Please login first.")
                    return False
            
            # Navigate to user's DM (try existing first, then new)
            logger.info(f"Navigating to DM for {username}...")
            if not self.navigate_to_dm(username, use_existing=use_existing_dm):
                logger.error(f"Failed to navigate to DM for {username}")
                return False
            
            # Send message
            logger.info(f"Sending message to {username}...")
            if not self.send_message(message_text):
                logger.error(f"Failed to send message to {username}")
                return False
            
            # Ultra-minimal delay between messages (for speed)
            time.sleep(0.3)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending DM to {username}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            
            # Try to reconnect if session lost
            if 'invalid session' in str(e).lower() or 'session id' in str(e).lower():
                logger.warning("Session lost, attempting to reconnect...")
                if self.ensure_driver_connected(reconnect=True):
                    logger.info("Reconnected! You may need to retry the operation.")
            
            self.failed_messages_count += 1
            return False
    
    def get_all_existing_dms(self):
        """
        Get list of all existing DM conversations by clicking and scrolling
        
        Returns:
            list: List of usernames from existing DMs
        """
        conversations = []
        try:
            if not self.ensure_driver_connected():
                return conversations
            
            logger.info("Opening inbox by clicking DM icon...")
            
            # Click DM icon if not already in inbox
            current_url = self.driver.current_url
            if '/direct/' not in current_url:
                if not self.click_dm_icon():
                    logger.warning("Could not click DM icon, trying URL navigation...")
                    self.driver.get("https://www.instagram.com/direct/inbox/")
                    time.sleep(1.5)
            else:
                time.sleep(1)
            
            wait = WebDriverWait(self.driver, 15)
            
            # Wait for conversation list to load
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/t/')]")))
            except:
                logger.warning("Conversation list not found")
                return conversations
            
            # Find scrollable conversation list
            scroll_container = None
            try:
                scroll_container = wait.until(EC.presence_of_element_located((
                    By.XPATH, "//div[contains(@role, 'list')] | //div[contains(@class, 'conversation')] | //div[@role='dialog']"
                )))
            except:
                scroll_container = self.driver.find_element(By.TAG_NAME, "body")
            
            logger.info("Scrolling through conversations to collect all DMs...")
            
            # Scroll and collect all conversations
            last_scroll = 0
            scroll_attempts = 0
            max_scrolls = 20
            all_links = set()
            
            while scroll_attempts < max_scrolls:
                # Get all conversation links on current view
                conversation_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/direct/t/')]")
                
                for link in conversation_links:
                    try:
                        href = link.get_attribute('href')
                        if href and '/direct/t/' in href:
                            all_links.add(href)
                    except:
                        continue
                
                # Scroll down
                scroll_height = self.driver.execute_script(
                    "return arguments[0].scrollHeight", scroll_container
                )
                self.driver.execute_script("""
                    arguments[0].scrollTo({
                        top: arguments[0].scrollHeight,
                        behavior: 'smooth'
                    });
                """, scroll_container)
                time.sleep(0.8)
                
                new_scroll = self.driver.execute_script(
                    "return arguments[0].scrollTop", scroll_container
                )
                
                if new_scroll == last_scroll:
                    break
                last_scroll = new_scroll
                scroll_attempts += 1
            
            # Extract usernames from all collected links
            for href in all_links:
                try:
                    parts = href.split('/direct/t/')
                    if len(parts) > 1:
                        username = parts[1].split('/')[0].split('?')[0].strip()
                        if username and username not in conversations:
                            conversations.append(username)
                except:
                    continue
            
            logger.info(f"✓ Retrieved {len(conversations)} existing conversations")
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting existing DMs: {e}")
            return conversations
    
    def ensure_driver_connected(self, reconnect=False):
        """
        Ensure driver is connected and working
        
        Args:
            reconnect: If True, try to reconnect to existing browser
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            if not self.driver:
                logger.error("Driver is None - browser not initialized")
                if reconnect:
                    logger.info("Attempting to reconnect to existing browser...")
                    return self.connect_to_existing_browser()
                return False
            
            # Try to get current URL to test connection
            try:
                _ = self.driver.current_url
                return True
            except Exception as e:
                error_msg = str(e).lower()
                if 'invalid session' in error_msg or 'session id' in error_msg:
                    logger.warning("Browser session lost - connection invalidated")
                    self.driver = None  # Clear invalid driver
                    
                    if reconnect:
                        logger.info("Attempting to reconnect to existing browser...")
                        return self.connect_to_existing_browser()
                    else:
                        logger.error("Browser session lost. Please reconnect using 'Connect to Existing Browser'")
                        return False
                else:
                    logger.error(f"Driver connection error: {e}")
                    return False
        except Exception as e:
            logger.error(f"Error checking driver connection: {e}")
            if reconnect:
                try:
                    return self.connect_to_existing_browser()
                except:
                    pass
            return False
    
    def click_followers_button(self):
        """Click the Followers button on a profile page"""
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Find Followers link/button
            followers_selectors = [
                "//a[contains(@href, '/followers/')]",
                "//div[contains(text(), 'followers')]//a",
                "//span[contains(text(), 'followers')]//parent::a",
                "//a[contains(text(), 'followers')]",
            ]
            
            for selector in followers_selectors:
                try:
                    followers_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    self.scroll_to_element(followers_btn)
                    self.move_cursor_to_element(followers_btn)
                    followers_btn.click()
                    time.sleep(1.5)  # Fast wait
                    logger.info("✓ Clicked Followers button")
                    return True
                except:
                    continue
            
            return False
        except Exception as e:
            logger.debug(f"Failed to click Followers button: {e}")
            return False
    
    def get_followers_list(self, target_username, max_followers=100, min_followers=10, progress_callback=None):
        """
        Get list of followers by clicking buttons and scrolling
        Tracks previously collected followers and filters them out
        
        Args:
            target_username: Username to get followers from
            max_followers: Maximum number of followers to retrieve
            min_followers: Minimum number of followers required (default 10)
            progress_callback: Optional callback function(status_dict) for progress updates
        """
        from config import Config
        config = Config()
        
        # Load previously collected followers for this user
        previously_collected_key = f"collected_followers_{target_username}"
        previously_collected = set(config.config.get('collected_followers', {}).get(target_username, []))
        
        if previously_collected:
            logger.info(f"Found {len(previously_collected)} previously collected followers for {target_username}. Will skip them.")
        
        followers = []
        seen_usernames = set(previously_collected)  # Start with previously collected
        
        try:
            # Check driver connection first - try to reconnect if lost
            if not self.ensure_driver_connected(reconnect=True):
                logger.error("Browser driver not connected. Please reconnect browser.")
                return followers
            
            logger.info(f"Fetching followers for {target_username}...")
            
            # Navigate to profile by clicking (not URL)
            current_url = self.driver.current_url
            if f'/{target_username}/' not in current_url:
                logger.info(f"Navigating to profile: {target_username}")
                # Try search first
                try:
                    search_icon = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, 
                            "//a[contains(@href, '/explore/')] | //svg[@aria-label='Search']"
                        ))
                    )
                    search_icon.click()
                    time.sleep(0.5)
                    
                    search_input = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@placeholder*='Search']"))
                    )
                    search_input.clear()
                    search_input.send_keys(target_username)
                    time.sleep(0.5)
                    
                    user_result = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '/{target_username}/')]"))
                    )
                    user_result.click()
                    time.sleep(1)
                except:
                    # Fallback to URL navigation
                    self.driver.get(f"https://www.instagram.com/{target_username}/")
                    time.sleep(1.5)
            else:
                logger.info("Already on profile page")
                time.sleep(0.5)
            
            # Click Followers button (not URL navigation)
            logger.info("Clicking Followers button...")
            if not self.click_followers_button():
                logger.error("Could not click Followers button")
                return followers
            
            time.sleep(2)  # Fast wait for modal
            
            # Wait for dialog to appear - try multiple methods
            wait = WebDriverWait(self.driver, 20)
            
            logger.info("Looking for followers dialog...")
            
            # Try to find the followers dialog/modal - Instagram uses various structures
            dialog = None
            dialog_selectors = [
                "//div[@role='dialog']",
                "//div[contains(@class, '_aano')]",  # Instagram's follower list container
                "//div[contains(@class, 'x1n2onr6')]",  # Common Instagram modal class
                "//div[contains(@style, 'position: fixed')]",
                "//div[contains(@class, 'dialog')]",
                "//div[contains(@aria-labelledby, 'Followers')]",
            ]
            
            for selector in dialog_selectors:
                try:
                    logger.debug(f"Trying selector: {selector}")
                    dialog = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    if dialog and dialog.is_displayed():
                        logger.info(f"✓ Found dialog with selector: {selector[:50]}")
                        break
                except Exception as e:
                    logger.debug(f"Selector failed: {e}")
                    continue
            
            if not dialog:
                # Try JavaScript to find modal
                try:
                    dialog = self.driver.execute_script("""
                        var dialogs = document.querySelectorAll('div[role="dialog"], div[class*="dialog"], div[style*="position: fixed"]');
                        for (var i = 0; i < dialogs.length; i++) {
                            if (dialogs[i].offsetHeight > 200) {
                                return dialogs[i];
                            }
                        }
                        return null;
                    """)
                    if dialog:
                        logger.info("✓ Found dialog using JavaScript")
                except Exception as e:
                    logger.debug(f"JavaScript dialog search failed: {e}")
            
            if not dialog:
                logger.error("Could not find followers dialog. Page might not have loaded.")
                logger.error(f"Current URL: {self.driver.current_url}")
                logger.error("Trying to take screenshot for debugging...")
                try:
                    self.driver.save_screenshot("debug_followers_page.png")
                    logger.info("Screenshot saved as debug_followers_page.png")
                except:
                    pass
                return followers
            
            logger.info("Followers dialog found, starting extraction...")
            
            # Find scrollable container - Instagram's follower list
            scroll_container = None
            scroll_container_selectors = [
                ".//div[contains(@class, '_aano')]",  # Instagram's scrollable container
                ".//div[contains(@style, 'overflow')]",
                ".//ul",
                ".//div[contains(@class, 'scroll')]",
                ".//div[contains(@class, 'x1n2onr6')]//div[contains(@style, 'overflow')]",
                ".//div[@role='dialog']//div[contains(@style, 'overflow-y')]",
                ".//div[@role='dialog']//div[contains(@class, '_aano')]",
            ]
            
            for selector in scroll_container_selectors:
                try:
                    found = dialog.find_element(By.XPATH, selector)
                    if found:
                        scroll_container = found
                        logger.info("✓ Found scroll container")
                        break
                except:
                    continue
            
            if not scroll_container:
                # Try JavaScript to find scrollable area
                try:
                    scroll_container = self.driver.execute_script("""
                        var dialog = arguments[0];
                        var scrollables = dialog.querySelectorAll('div[style*="overflow"], ul, div[class*="scroll"]');
                        for (var i = 0; i < scrollables.length; i++) {
                            if (scrollables[i].scrollHeight > scrollables[i].clientHeight) {
                                return scrollables[i];
                            }
                        }
                        return dialog;
                    """, dialog)
                except:
                    scroll_container = dialog
            
            logger.info("Phase 1: Scanning ALL followers to build complete list...")
            logger.info(f"Phase 2: Will select {min_followers}-{max_followers} new followers (excluding {len(previously_collected)} previously collected)")
            
            # PHASE 1: Collect ALL followers first
            all_followers_set = set()  # Use set for fast lookup
            last_scroll_height = 0
            no_change_count = 0
            max_no_change = 20  # INCREASED: More scrolls to ensure we get everything (was 10)
            scroll_count = 0
            max_scrolls = 2000  # INCREASED: Very high limit to scan entire list (was 1000)
            
            logger.info("Scrolling through entire followers list...")
            logger.info(f"Will continue until {max_no_change} consecutive scrolls with no new followers")
            logger.info(f"OPTION B: Will continue until we have at least {min_followers} followers")
            
            # OPTION B: Force minimum followers - continue until we have at least min_followers
            # Scroll through ENTIRE list to collect ALL followers
            while (no_change_count < max_no_change and scroll_count < max_scrolls and 
                   len(all_followers_set) < min_followers):  # OPTION B: Force minimum
                scroll_count += 1
                
                # OPTION D: Visual scroll indicator - calculate progress
                total_needed = max_followers
                current_count = len(all_followers_set)
                progress_pct = min(100, int((current_count / total_needed) * 100)) if total_needed > 0 else 0
                estimated_remaining = max(0, total_needed - current_count)
                
                # Update progress callback if provided (OPTION D)
                if progress_callback:
                    try:
                        progress_callback({
                            'scroll_count': scroll_count,
                            'followers_found': current_count,
                            'target': total_needed,
                            'progress_percent': progress_pct,
                            'no_change_count': no_change_count,
                            'max_no_change': max_no_change,
                            'estimated_remaining': estimated_remaining,
                            'status': 'scrolling'
                        })
                    except:
                        pass  # Don't break if callback fails
                
                if scroll_count % 10 == 0:  # More frequent updates
                    logger.info(f"📊 Scroll {scroll_count} | Found: {current_count}/{total_needed} followers ({progress_pct}%) | No-change: {no_change_count}/{max_no_change} | Remaining: ~{estimated_remaining}")
                
                # IMPROVED SCROLL - scroll to bottom with better detection
                try:
                    # Get current scroll position BEFORE scrolling
                    scroll_height_before = self.driver.execute_script(
                        "return arguments[0].scrollHeight", scroll_container
                    )
                    scroll_top_before = self.driver.execute_script(
                        "return arguments[0].scrollTop", scroll_container
                    )
                    client_height = self.driver.execute_script(
                        "return arguments[0].clientHeight", scroll_container
                    )
                    
                    # IMPROVED SCROLL: Multiple scroll methods to ensure content loads
                    # Method 1: Scroll to bottom
                    self.driver.execute_script("""
                        arguments[0].scrollTop = arguments[0].scrollHeight;
                    """, scroll_container)
                    
                    # Method 2: Smooth scroll (triggers lazy loading better)
                    self.driver.execute_script("""
                        arguments[0].scrollTo({
                            top: arguments[0].scrollHeight,
                            behavior: 'smooth'
                        });
                    """, scroll_container)
                    
                    # Method 3: Scroll window as well
                    self.driver.execute_script("window.scrollBy(0, 1000);")
                    
                    # INCREASED WAIT: Give Instagram more time to load content
                    time.sleep(1.0)  # INCREASED from 0.5s to 1.0s for better loading
                    
                    # Check if new content loaded AFTER scrolling
                    new_scroll_height = self.driver.execute_script(
                        "return arguments[0].scrollHeight", scroll_container
                    )
                    new_scroll_top = self.driver.execute_script(
                        "return arguments[0].scrollTop", scroll_container
                    )
                    
                    # IMPROVED DETECTION: Check if content actually loaded
                    height_increased = new_scroll_height > scroll_height_before
                    is_at_bottom = new_scroll_top >= (new_scroll_height - client_height - 100)
                    
                    if height_increased:
                        # Height increased, new content loaded - reset counter
                        no_change_count = 0
                        logger.debug(f"✓ New content loaded: height {scroll_height_before} -> {new_scroll_height}")
                    elif is_at_bottom and new_scroll_height == scroll_height_before:
                        # At bottom and height didn't change - might be end
                        no_change_count += 1
                        if no_change_count >= max_no_change:
                            logger.info(f"✓ Reached end of followers list after {scroll_count} scrolls")
                            break
                    else:
                        # Not at bottom yet, continue scrolling
                        no_change_count = 0
                    
                except Exception as e:
                    logger.debug(f"Scroll error: {e}")
                
                # NOW extract followers after scrolling
                # IMPROVED: Use multiple extraction methods to catch all followers
                try:
                    # Get ALL followers from the entire scrollable container
                    try:
                        js_followers = self.driver.execute_script("""
                            var followers = [];
                            var seen = new Set();
                            
                            // Method 1: Get all links
                            var links = arguments[0].querySelectorAll('a[href*="/"]');
                            
                            // Method 2: Also check for divs with usernames (Instagram sometimes uses divs)
                            var divs = arguments[0].querySelectorAll('div[role="button"] a, div a[href*="/"]');
                            
                            // Combine both
                            var allElements = [];
                            for (var i = 0; i < links.length; i++) allElements.push(links[i]);
                            for (var i = 0; i < divs.length; i++) {
                                if (allElements.indexOf(divs[i]) === -1) allElements.push(divs[i]);
                            }
                            
                            for (var i = 0; i < allElements.length; i++) {
                                var element = allElements[i];
                                var href = element.getAttribute('href');
                                
                                // Also try to get username from text content if href fails
                                if (!href || href === '#') {
                                    var text = element.textContent || element.innerText;
                                    if (text && text.trim().length > 0 && text.trim().length <= 30) {
                                        var possibleUsername = text.trim().split('\\n')[0].split(' ')[0].replace('@', '');
                                        if (possibleUsername && !seen.has(possibleUsername)) {
                                            seen.add(possibleUsername);
                                            followers.push(possibleUsername);
                                        }
                                    }
                                    continue;
                                }
                                
                                if (seen.has(href)) continue;
                                seen.add(href);
                                
                                // Skip non-profile links
                                if (href.includes('/p/') || href.includes('/reel/') || 
                                    href.includes('/explore/') || href.includes('/accounts/') ||
                                    href.includes('/direct/') || href.includes('/stories/') ||
                                    href.includes('/tv/') || href.includes('/tagged/') ||
                                    href.includes('/saved/') || href.includes('/tag/') ||
                                    href.includes('/location/') || href.includes('/help/')) {
                                    continue;
                                }
                                
                                // Extract username
                                var username = null;
                                if (href.includes('instagram.com/')) {
                                    var parts = href.split('instagram.com/');
                                    if (parts.length > 1) {
                                        username = parts[1].split('/')[0].split('?')[0].split('#')[0].trim();
                                    }
                                } else if (href.startsWith('/') && !href.startsWith('//')) {
                                    username = href.split('/')[1].split('?')[0].split('#')[0].trim();
                                }
                                
                                // Validate username
                                if (username && username.length > 1 && username.length <= 30) {
                                    var invalid = ['p', 'reel', 'explore', 'accounts', 'direct', 'stories', 
                                                  'tv', 'tagged', 'saved', 'tag', 'location', 'help', 
                                                  'about', 'blog', 'developers', 'reels', 'explore'];
                                    if (invalid.indexOf(username.toLowerCase()) === -1) {
                                        followers.push(username);
                                    }
                                }
                            }
                            
                            return followers;
                        """, scroll_container)
                        
                        # Add ALL followers to the complete set (no filtering yet)
                        new_followers_count = 0
                        for username in js_followers:
                            if username and username != target_username:
                                if username not in all_followers_set:
                                    all_followers_set.add(username)
                                    new_followers_count += 1
                        
                        if new_followers_count > 0:
                            no_change_count = 0  # Reset counter if we found new ones
                            logger.debug(f"Found {new_followers_count} new followers this scroll")
                            
                            # OPTION D: Update progress after finding new followers
                            if progress_callback:
                                try:
                                    current_count = len(all_followers_set)
                                    progress_callback({
                                        'scroll_count': scroll_count,
                                        'followers_found': current_count,
                                        'target': max_followers,
                                        'progress_percent': min(100, int((current_count / max_followers) * 100)) if max_followers > 0 else 0,
                                        'new_found': new_followers_count,
                                        'status': 'found_new'
                                    })
                                except:
                                    pass
                        else:
                            # No new followers found this scroll - but continue if we haven't reached target
                            # OPTION B: Force minimum - continue if we don't have min_followers yet
                            if len(all_followers_set) < min_followers:
                                # Haven't reached minimum yet, continue scrolling (OPTION B)
                                no_change_count = 0  # Don't count as "no change" if we haven't reached minimum
                                logger.info(f"⚠️ Only {len(all_followers_set)}/{min_followers} followers (minimum not met), continuing to scroll...")
                            elif len(all_followers_set) < max_followers:
                                # Haven't reached target yet, continue scrolling
                                no_change_count = 0  # Don't count as "no change" if we haven't reached target
                                logger.debug(f"No new followers this scroll, but only have {len(all_followers_set)}/{max_followers}, continuing...")
                            else:
                                # We have enough, but check if we should continue
                                no_change_count += 1
                                if no_change_count >= max_no_change:
                                    logger.info(f"✓ Finished scanning! No more new followers after {max_no_change} scrolls")
                                    break
                            
                    except Exception as e:
                        logger.debug(f"JavaScript extraction failed: {e}")
                        no_change_count += 1
                    
                    # Skip the slower XPath extraction - JavaScript is faster and more reliable
                        
                except Exception as e:
                    logger.error(f"Error extracting followers: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
                    # Don't break, continue scrolling
                    no_change_count += 1
            
            # OPTION B: Check if we got minimum followers
            if len(all_followers_set) < min_followers:
                logger.warning(f"⚠️ OPTION B: Only found {len(all_followers_set)} followers, but minimum required is {min_followers}")
                logger.warning("This might indicate:")
                logger.warning("  - Account has fewer followers than requested")
                logger.warning("  - Some followers are private/hidden")
                logger.warning("  - Instagram rate limiting")
            
            # OPTION D: Final progress update
            if progress_callback:
                try:
                    progress_callback({
                        'scroll_count': scroll_count,
                        'followers_found': len(all_followers_set),
                        'target': max_followers,
                        'progress_percent': 100,
                        'status': 'filtering'
                    })
                except:
                    pass
            
            # PHASE 2: Convert set to list and filter out previously collected
            logger.info(f"Phase 2: Filtering {len(all_followers_set)} total followers...")
            
            # Convert set to list (preserve order by converting to list)
            all_followers_list = list(all_followers_set)
            
            # Filter out previously collected followers
            new_followers = [f for f in all_followers_list if f not in previously_collected]
            
            logger.info(f"Total followers found: {len(all_followers_list)}")
            logger.info(f"Previously collected: {len(previously_collected)}")
            logger.info(f"New followers available: {len(new_followers)}")
            
            # Select the requested amount from new followers
            if len(new_followers) >= min_followers:
                # Take up to max_followers, but at least min_followers
                selected_followers = new_followers[:max_followers]
                logger.info(f"✓ Selected {len(selected_followers)} new followers from available {len(new_followers)}")
            else:
                # Not enough new followers, take what we have
                selected_followers = new_followers[:min_followers] if len(new_followers) > 0 else []
                logger.warning(f"Only {len(new_followers)} new followers available (minimum {min_followers} required)")
            
            # Save ALL collected followers to config (complete list)
            if selected_followers:
                if 'collected_followers' not in config.config:
                    config.config['collected_followers'] = {}
                
                # Update the complete list (merge with previously collected)
                if target_username not in config.config['collected_followers']:
                    config.config['collected_followers'][target_username] = []
                
                # Add new followers to the list (avoid duplicates)
                existing_set = set(config.config['collected_followers'][target_username])
                new_to_add = [f for f in selected_followers if f not in existing_set]
                config.config['collected_followers'][target_username].extend(new_to_add)
                config.save_config()
                
                logger.info(f"✓ Saved {len(new_to_add)} new followers to collection history")
                logger.info(f"  Total saved for {target_username}: {len(config.config['collected_followers'][target_username])}")
            
            # Log final results
            logger.info(f"✓ Collection complete: {len(selected_followers)} new followers selected")
            logger.info(f"  Complete list size: {len(all_followers_list)} followers")
            logger.info(f"  Previously collected: {len(previously_collected)}")
            logger.info(f"  New followers selected: {len(selected_followers)}")
            
            if len(selected_followers) < min_followers:
                logger.warning(f"Only {len(selected_followers)} new followers available, minimum required: {min_followers}")
                if len(all_followers_list) > 0:
                    logger.warning(f"Total followers scanned: {len(all_followers_list)}, but {len(previously_collected)} were already collected")
            else:
                logger.info(f"✓ Successfully selected {len(selected_followers)} new followers (minimum {min_followers} met)")
            
            return selected_followers
            
        except Exception as e:
            logger.error(f"Error getting followers: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []  # Return empty list on error
    
    def send_bulk_messages(self, usernames, message_text, max_messages=None, delay_between=(2, 4)):
        """
        Send messages to multiple users - OPTIMIZED FOR SPEED (marketing mode)
        
        Args:
            usernames: List of usernames
            message_text: Message to send
            max_messages: Maximum number of messages to send (None for all)
            delay_between: Tuple of (min, max) seconds between messages (reduced for speed: 2-4s)
        """
        if max_messages:
            usernames = usernames[:max_messages]
        
        results = {
            'success': [],
            'failed': []
        }
        
        total = len(usernames)
        logger.info(f"🚀 BULK SEND MODE: Sending to {total} users (FAST - optimized for marketing)")
        
        for i, username in enumerate(usernames, 1):
            logger.info(f"[{i}/{total}] Sending to {username}...")
            
            # FAST: Try existing DM first (faster), then profile method (handles private accounts)
            success = self.send_dm_to_user(username, message_text, use_existing_dm=True)
            
            if success:
                results['success'].append(username)
                logger.info(f"✓ [{i}/{total}] Success: {username}")
            else:
                results['failed'].append(username)
                logger.warning(f"✗ [{i}/{total}] Failed: {username}")
            
            # MINIMAL DELAY: Reduced delay for marketing speed (except for last one)
            if i < total:
                delay = random.uniform(delay_between[0], delay_between[1])  # Now 2-4s instead of 5-10s
                time.sleep(delay)
        
        logger.info(f"✓ Bulk send complete. Success: {len(results['success'])}, Failed: {len(results['failed'])}")
        return results
    
    def save_session(self, filepath='session.json'):
        """Save session data"""
        self.session_data = {
            'sent_count': self.sent_messages_count,
            'failed_count': self.failed_messages_count,
            'last_update': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(self.session_data, f, indent=2)
    
    def load_session(self, filepath='session.json'):
        """Load session data"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.session_data = json.load(f)
                self.sent_messages_count = self.session_data.get('sent_count', 0)
                self.failed_messages_count = self.session_data.get('failed_count', 0)
    
    def close(self):
        """Close browser and cleanup"""
        if self.driver:
            self.save_session()
            # Don't close browser, let user close it manually
            logger.info("Session saved. Browser will remain open.")
    
