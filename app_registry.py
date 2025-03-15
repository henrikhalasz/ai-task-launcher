import os
import sys
from typing import Dict, Optional, List
import winreg
import subprocess
from pathlib import Path

class AppRegistry:
    """
    Manages the registry of applications and their executable paths.
    Provides methods to lookup applications by user-friendly names.
    Dynamically discovers application paths without hardcoding.
    """
    
    def __init__(self):
        # Initialize empty application registry
        self.app_registry = {}
        
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
        
        # Common application names and their executable filenames
        self.common_apps = {
            "chrome": ["chrome.exe"],
            "firefox": ["firefox.exe"],
            "edge": ["msedge.exe"],
            "word": ["WINWORD.EXE", "winword.exe"],
            "excel": ["EXCEL.EXE", "excel.exe"],
            "powerpoint": ["POWERPNT.EXE", "powerpnt.exe"],
            "notepad": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "spotify": ["Spotify.exe"],
            "explorer": ["explorer.exe"],
            "paint": ["mspaint.exe"],
            "cmd": ["cmd.exe"],
            "powershell": ["powershell.exe"],
        }
        
        # Common installation directories to search
        self.search_paths = self._get_search_paths()
        
        # Discover applications using multiple methods
        self._discover_apps()
    
    def _get_search_paths(self) -> List[str]:
        """Get common paths to search for applications"""
        paths = []
        
        # System directories
        system_drive = os.environ.get("SystemDrive", "C:")
        system_root = os.environ.get("SystemRoot", r"C:\Windows")
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        
        # Add system paths
        paths.extend([
            system_root,
            os.path.join(system_root, "System32"),
            os.path.join(system_root, "SysWOW64"),
            program_files,
            program_files_x86,
        ])
        
        # Add common application directories
        paths.extend([
            os.path.join(program_files, "Microsoft Office", "root", "Office16"),
            os.path.join(program_files, "Microsoft Office", "root", "Office15"),
            os.path.join(program_files, "Mozilla Firefox"),
            os.path.join(program_files_x86, "Google", "Chrome", "Application"),
            os.path.join(program_files_x86, "Microsoft", "Edge", "Application"),
        ])
        
        # Add user-specific paths
        user_profile = os.environ.get("USERPROFILE", "")
        if user_profile:
            paths.extend([
                os.path.join(user_profile, "AppData", "Local", "Microsoft", "WindowsApps"),
                os.path.join(user_profile, "AppData", "Local", "Programs"),
                os.path.join(user_profile, "AppData", "Roaming"),
            ])
        
        # Add PATH environment directories
        paths.extend(os.environ.get("PATH", "").split(os.pathsep))
        
        # Filter out empty paths and ensure they exist
        return [p for p in paths if p and os.path.exists(p)]
    
    def _discover_apps(self):
        """Discover applications using multiple methods"""
        # Method 1: Discover from Windows registry App Paths
        self._discover_from_app_paths()
        
        # Method 2: Discover from Windows registry Uninstall information
        self._discover_from_uninstall_registry()
        
        # Method 3: Search in common paths for known executables
        self._discover_from_filesystem()
        
        # Method 4: Use where.exe to find executables in PATH
        self._discover_from_where_command()
    
    def _discover_from_app_paths(self):
        """Discover applications from Windows registry App Paths"""
        try:
            # Open the App Paths registry key
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
                    
                    # Add to registry if path exists
                    if os.path.exists(path):
                        self.app_registry[app_name] = path
                        # Also add a simple window pattern if not already present
                        if app_name not in self.window_patterns:
                            self.window_patterns[app_name] = app_name.title()
                    
                    index += 1
                    
                except WindowsError:
                    # No more subkeys
                    break
                    
        except Exception as e:
            # Just continue with other discovery methods if registry access fails
            pass
    
    def _discover_from_uninstall_registry(self):
        """Discover applications from Windows registry Uninstall information"""
        try:
            # Open the Uninstall registry key
            registry_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                0, winreg.KEY_READ
            )
            
            # Enumerate subkeys
            index = 0
            while True:
                try:
                    # Get the next subkey
                    subkey_name = winreg.EnumKey(registry_key, index)
                    
                    # Open the subkey
                    subkey = winreg.OpenKey(registry_key, subkey_name)
                    
                    try:
                        # Get display name and executable path
                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                        install_location, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                        
                        # Clean up the display name and use as app name
                        app_name = display_name.lower().split()[0]
                        
                        # Check if we can find an executable in the install location
                        if install_location and os.path.exists(install_location):
                            # Look for executables in the install location
                            for file in os.listdir(install_location):
                                if file.lower().endswith(".exe"):
                                    exe_path = os.path.join(install_location, file)
                                    # Add to registry if not already present
                                    if app_name not in self.app_registry:
                                        self.app_registry[app_name] = exe_path
                                        # Also add a simple window pattern
                                        if app_name not in self.window_patterns:
                                            self.window_patterns[app_name] = display_name
                                    break
                    except:
                        # Missing values, just continue
                        pass
                    
                    index += 1
                    
                except WindowsError:
                    # No more subkeys
                    break
                    
        except Exception as e:
            # Just continue with other discovery methods if registry access fails
            pass
    
    def _discover_from_filesystem(self):
        """Search for known applications in common paths"""
        for app_name, exe_names in self.common_apps.items():
            # Skip if already found
            if app_name in self.app_registry:
                continue
                
            # Search in all paths
            for search_path in self.search_paths:
                for exe_name in exe_names:
                    # Check direct path
                    exe_path = os.path.join(search_path, exe_name)
                    if os.path.exists(exe_path):
                        self.app_registry[app_name] = exe_path
                        break
                        
                    # Check subdirectories (one level)
                    try:
                        for subdir in os.listdir(search_path):
                            subdir_path = os.path.join(search_path, subdir)
                            if os.path.isdir(subdir_path):
                                exe_path = os.path.join(subdir_path, exe_name)
                                if os.path.exists(exe_path):
                                    self.app_registry[app_name] = exe_path
                                    break
                    except:
                        # Permission error or other issue, just continue
                        pass
                
                # Break if found
                if app_name in self.app_registry:
                    break
    
    def _discover_from_where_command(self):
        """Use the where.exe command to find executables in PATH"""
        for app_name, exe_names in self.common_apps.items():
            # Skip if already found
            if app_name in self.app_registry:
                continue
                
            for exe_name in exe_names:
                try:
                    # Run where.exe to find the executable
                    result = subprocess.run(
                        ["where", exe_name], 
                        capture_output=True, 
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    if result.returncode == 0:
                        # Get the first path found (usually the one that would be executed)
                        paths = result.stdout.strip().split('\n')
                        if paths:
                            self.app_registry[app_name] = paths[0]
                            break
                except:
                    # Command failed, just continue
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
        
        # Try to find the application on-demand
        return self._find_app_on_demand(app_name)
    
    def _find_app_on_demand(self, app_name: str) -> Optional[str]:
        """
        Attempt to find an application that wasn't in the initial discovery.
        
        Args:
            app_name (str): User-friendly name of the application
            
        Returns:
            Optional[str]: Executable path or None if not found
        """
        # Try using where.exe command
        try:
            # Try with .exe extension
            exe_name = f"{app_name}.exe"
            result = subprocess.run(
                ["where", exe_name], 
                capture_output=True, 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                # Get the first path found
                paths = result.stdout.strip().split('\n')
                if paths:
                    # Cache the result for future use
                    self.app_registry[app_name] = paths[0]
                    return paths[0]
        except:
            pass
        
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
        return app_name.title()
    
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
            self.window_patterns[name] = name.title()
