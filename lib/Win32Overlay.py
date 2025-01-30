import win32gui
import win32con
import win32api
import logging
from ctypes import windll

class Win32Overlay:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.hwnd = None
        self.is_active = False
        
        # Window class and name
        self.class_name = "WowFingerOverlay"
        self.window_name = "WowFingerStatus"
        
        # Window dimensions
        self.width = 80
        self.height = 40
        
        # GDI32 functions
        self.gdi32 = windll.gdi32
        
        # Create and show window
        self._create_window()
        
        # Initial paint
        self.update_status(False)
    
    def _create_window(self):
        """Create the overlay window"""
        try:
            # Register window class
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self._wnd_proc
            wc.hInstance = win32api.GetModuleHandle(None)
            wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
            wc.hbrBackground = win32gui.GetStockObject(win32con.BLACK_BRUSH)
            wc.lpszClassName = self.class_name
            
            # Register class
            win32gui.RegisterClass(wc)
            
            # Create window
            style = win32con.WS_POPUP | win32con.WS_VISIBLE
            ex_style = (win32con.WS_EX_TOOLWINDOW | 
                       win32con.WS_EX_LAYERED | 
                       win32con.WS_EX_TOPMOST)
            
            # Create the window
            self.hwnd = win32gui.CreateWindowEx(
                ex_style,
                self.class_name,
                self.window_name,
                style,
                self.config.overlay_position_x,
                self.config.overlay_position_y,
                self.width,
                self.height,
                0,
                0,
                wc.hInstance,
                None
            )
            
            # Set window transparency
            win32gui.SetLayeredWindowAttributes(
                self.hwnd, 
                0,  # Black
                192,  # 75% opacity
                win32con.LWA_ALPHA
            )
            
            # Show window
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
            win32gui.UpdateWindow(self.hwnd)
            
            self.logger.info("Win32 overlay window created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create overlay window: {e}", exc_info=True)
            raise
    
    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        """Window procedure"""
        if msg == win32con.WM_PAINT:
            try:
                hdc = win32gui.GetDC(hwnd)
                self._do_paint(hwnd, hdc)
                win32gui.ReleaseDC(hwnd, hdc)
                return 0
            except Exception as e:
                self.logger.error(f"Error in WM_PAINT: {e}")
                return 0
        elif msg == win32con.WM_ERASEBKGND:
            return 1  # Say we handled it
        
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    
    def _do_paint(self, hwnd, hdc):
        """Handle the paint message"""
        try:
            # Create font
            font_height = -self.config.overlay_font_size  # Negative for character height
            font = self.gdi32.CreateFontW(
                font_height,                   # Height
                0,                            # Width
                0,                            # Escapement
                0,                            # Orientation
                win32con.FW_BOLD,            # Weight
                0,                            # Italic
                0,                            # Underline
                0,                            # StrikeOut
                win32con.ANSI_CHARSET,       # CharSet
                win32con.OUT_DEFAULT_PRECIS, # OutPrecision
                win32con.CLIP_DEFAULT_PRECIS,# ClipPrecision
                win32con.ANTIALIASED_QUALITY,# Quality
                win32con.FF_DONTCARE,        # PitchAndFamily
                "Arial"                       # FaceName
            )
            
            # Select font
            old_font = self.gdi32.SelectObject(hdc, font)
            
            # Set text color
            if self.is_active:
                self.gdi32.SetTextColor(hdc, win32api.RGB(0, 255, 0))  # Green
            else:
                self.gdi32.SetTextColor(hdc, win32api.RGB(255, 0, 0))  # Red
            
            self.gdi32.SetBkColor(hdc, win32api.RGB(0, 0, 0))  # Black background
            
            # Get client area
            rect = win32gui.GetClientRect(hwnd)
            
            # Draw text
            text = "ON" if self.is_active else "OFF"
            self.gdi32.DrawTextW(
                hdc, 
                text, 
                len(text), 
                rect, 
                win32con.DT_CENTER | win32con.DT_VCENTER | win32con.DT_SINGLELINE
            )
            
            # Cleanup
            self.gdi32.SelectObject(hdc, old_font)
            self.gdi32.DeleteObject(font)
            
        except Exception as e:
            self.logger.error(f"Error painting: {e}", exc_info=True)
    
    def update_status(self, is_active):
        """Update the overlay status"""
        try:
            if self.is_active != is_active:
                self.is_active = is_active
                if self.hwnd:
                    win32gui.InvalidateRect(self.hwnd, None, True)
                    win32gui.UpdateWindow(self.hwnd)
                    self.logger.debug(f"Status updated to: {'ON' if is_active else 'OFF'}")
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
    
    def destroy(self):
        """Destroy the overlay window"""
        try:
            if self.hwnd:
                win32gui.DestroyWindow(self.hwnd)
                self.hwnd = None
                win32gui.UnregisterClass(self.class_name, win32api.GetModuleHandle(None))
                self.logger.info("Overlay window destroyed")
        except Exception as e:
            self.logger.error(f"Error destroying overlay: {e}") 