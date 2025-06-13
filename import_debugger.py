import sys
import os
import importlib
from pathlib import Path

def log(message):
    with open('import_debug.log', 'a') as f:
        f.write(f"{message}\n")

def check_import(module_name):
    try:
        log(f"\n{'='*80}")
        log(f"Attempting to import: {module_name}")
        log(f"Current sys.path:")
        for p in sys.path:
            log(f"  - {p}")
        
        # Check if module is already in sys.modules
        if module_name in sys.modules:
            log(f"  Module {module_name} is already in sys.modules")
            module = sys.modules[module_name]
            log(f"  Module file: {getattr(module, '__file__', 'Unknown')}")
            return True
            
        # Try to import the module
        module = importlib.import_module(module_name)
        log(f"✅ Successfully imported {module_name}")
        log(f"  Module file: {getattr(module, '__file__', 'Unknown')}")
        log(f"  Module attributes: {[attr for attr in dir(module) if not attr.startswith('_')]}")
        return True
        
    except ImportError as e:
        log(f"❌ Failed to import {module_name}")
        log(f"  Error: {str(e)}")
        log(f"  sys.path_importer_cache: {sys.path_importer_cache}")
        log(f"  Python executable: {sys.executable}")
        log(f"  Python version: {sys.version}")
        log(f"  Environment variables:")
        for k, v in os.environ.items():
            if 'PYTHON' in k.upper() or 'PATH' in k.upper():
                log(f"    {k} = {v}")
        return False

if __name__ == "__main__":
    # Clear the log file
    with open('import_debug.log', 'w') as f:
        f.write("Import Debugger Started\n")
    
    # Test the problematic import
    check_import("google.cloud.discoveryengine")
    
    # Also test importing the specific client
    try:
        from google.cloud import discoveryengine
        log("\n✅ Successfully imported discoveryengine directly")
        log(f"  discoveryengine.__file__: {discoveryengine.__file__}")
        log(f"  discoveryengine.__path__: {discoveryengine.__path__}")
    except Exception as e:
        log(f"\n❌ Failed to import discoveryengine directly: {e}")
    
    log("\nImport debugger completed")
