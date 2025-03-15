import os
from typing import Dict, Optional
import winreg

class AppRegistry:
    """
    Manages the registry of applications and their executable paths.
    Provides methods to lookup applications by user-friendly names.
    """
    
    def __init__(self):
        # Default application mappings
        self.app_registry = {
            # Common applications with default paths
            "chrome": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
            "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
            "notepad": r"C:\Windows\system32\notepad.exe",
            "calculator": r"C:\Windows\System32\calc.exe",
            "spotify": r"C:\Users\henrikhalasz\AppData\Roaming\Spotify\Spotify.exe",
            "explorer": r"C:\Windows\explorer.exe",
            "paint": r"C:\Windows\system32\mspaint.exe",
            "cmd": r"C:\Windows\system32\cmd.exe",
            "powershell": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        }
        
        # Window title patterns for closing applications
        self.window_patterns = {
            "chrome": "Google Chrome",
            "firefox": "Mozilla Firefox",
            "edge": "Microsoft Edge",
            "word": "Word",
            "excel": "Excel",
            "powerpoint": "PowerPoint",
            "notepad": "Notepad",
            "calculator": "Calculator",
            "spotify": "Spotify",
            "explorer": "File Explorer",
            "paint": "Paint",
            "cmd": "Command Prompt",
            "powershell": "Windows PowerShell",
        }
        
        # Update paths with environment variables
        self._resolve_paths()
        
        # Try to discover more applications from Windows registry
        self._discover_apps_from_registry()
    
    def _resolve_paths(self):
        """Resolve any environment variables in paths"""
        for app, path in self.app_registry.items():
            if "%USERNAME%" in path:
                self.app_registry[app] = path.replace("%USERNAME%", os.getenv("USERNAME", ""))
    
    def _discover_apps_from_registry(self):
        """Attempt to discover installed applications from Windows registry"""
        try:
            # Open the Uninstall registry key
            registry_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
                0, winreg.KEY_READ
            )
            
            # Enumerate subkeys
            index = 0
            while True:
                try:
                    # Get the next subkey
                    subkey_name = winreg.EnumKey(registry_key, index)
                    
                    # Extract the app name from the executable filename
                    app_name = os.path.splitext(subkey_name)[0].lower()
                    
                    # Open the subkey to get the executable path
                    subkey = winreg.OpenKey(registry_key, subkey_name)
                    path, _ = winreg.QueryValueEx(subkey, "")
                    
                    # Add to registry if not already present
                    if app_name not in self.app_registry:
                        self.app_registry[app_name] = path
                        # Also add a simple window pattern
                        if app_name not in self.window_patterns:
                            self.window_patterns[app_name] = app_name
                    
                    index += 1
                    
                except WindowsError:
                    # No more subkeys
                    break
                    
        except Exception as e:
            # Just continue with default registry if registry access fails
            pass
    
    def get_app_path(self, app_name: str) -> Optional[str]:
        """
        Get the executable path for an application by name.
        
        Args:
            app_name (str): User-friendly name of the application
            
        Returns:
            Optional[str]: Executable path or None if not found
        """
        app_name = app_name.lower()
        
        # Direct match in registry
        if app_name in self.app_registry:
            return self.app_registry[app_name]
        
        # Try to find a partial match
        for name, path in self.app_registry.items():
            if app_name in name or name in app_name:
                return path
        
        # No match found
        return None
    
    def get_window_pattern(self, app_name: str) -> Optional[str]:
        """
        Get the window title pattern for an application by name.
        
        Args:
            app_name (str): User-friendly name of the application
            
        Returns:
            Optional[str]: Window title pattern or None if not found
        """
        app_name = app_name.lower()
        
        # Direct match in patterns
        if app_name in self.window_patterns:
            return self.window_patterns[app_name]
        
        # Try to find a partial match
        for name, pattern in self.window_patterns.items():
            if app_name in name or name in app_name:
                return pattern
        
        # Fallback to using the app name itself as the pattern
        return app_name
    
    def add_app(self, name: str, path: str, window_pattern: Optional[str] = None):
        """
        Add a new application to the registry.
        
        Args:
            name (str): User-friendly name of the application
            path (str): Executable path
            window_pattern (Optional[str]): Window title pattern for closing
        """
        name = name.lower()
        self.app_registry[name] = path
        
        if window_pattern:
            self.window_patterns[name] = window_pattern
        else:
            # Use name as fallback window pattern
            self.window_patterns[name] = name
