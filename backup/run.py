# run.py - The single, definitive entry point for the KYO QA Tool.
# This script ensures all dependencies and assets are ready before launch.
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

# --- Pre-flight Checks ---

def check_and_install_dependencies():
    """Check for requirements.txt and install any missing packages."""
    requirements_path = Path("requirements.txt")
    if not requirements_path.exists():
        print("⚠️ requirements.txt not found. Skipping dependency check.")
        return True

    print("📦 Checking for required packages...")
    try:
        # Use pip to check for missing packages and install them.
        # The '--quiet' flag reduces verbose output.
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_path), '--quiet'],
            stdout=subprocess.DEVNULL,
        )
        print("✅ All required packages are installed.")
        return True
    except subprocess.CalledProcessError:
        messagebox.showerror(
            "Dependency Error",
            "Failed to install required packages from requirements.txt.\n"
            "Please check your internet connection and ensure you have pip installed."
        )
        return False
    except Exception as e:
        messagebox.showerror("Dependency Error", f"An unexpected error occurred: {e}")
        return False

def check_assets():
    """Ensure all required UI assets (like icons) exist, creating them if necessary."""
    print("🎨 Checking for UI assets...")
    try:
        # We import the icon system here to ensure dependencies are ready.
        from auto_icon_system import check_and_create_icons
        if check_and_create_icons():
            print("✅ All UI assets are ready.")
            return True
        else:
            # The icon system will print its own errors.
            # We show a message box as a final fallback.
            messagebox.showwarning(
                "Asset Warning",
                "Could not create all required UI icons. The application will run, but some buttons may appear blank."
            )
            return True # Return True to allow the app to attempt to run anyway
    except ImportError:
        messagebox.showerror(
            "Asset Error",
            "The 'auto_icon_system.py' file is missing. Cannot verify UI assets."
        )
        return False
    except Exception as e:
        messagebox.showerror("Asset Error", f"An error occurred while checking assets: {e}")
        return False

# --- Main Application Launch ---

def launch_main_application():
    """Launch the main KyoQAToolApp window."""
    print("🚀 Launching KYO QA Knowledge Tool...")
    try:
        # We import the main app here, after all checks have passed.
        app = KyoQAToolApp()
        app.mainloop()
    except Exception as e:
        # This is the final safety net. If the app crashes on launch for any reason,
        # this will catch it and display a helpful error message.
        print(f"❌ A fatal error occurred during application launch: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror(
            "Fatal Launch Error",
            f"The application could not start.\n\n"
            f"Error: {e}\n\n"
            "Please check the console for more details."
        )

if __name__ == "__main__":
    print("--- KYO QA Tool Launcher ---")
    
    # Run all pre-flight checks. If any fail, the script will exit.
    if not check_and_install_dependencies():
        sys.exit(1)
        
    if not check_assets():
        sys.exit(1)
        
    # If all checks pass, launch the main application.
    launch_main_application()
    
    print("👋 Application closed. Goodbye!")
