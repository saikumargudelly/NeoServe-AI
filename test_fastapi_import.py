import sys
import importlib
from importlib import reload

def print_section(title):
    print(f"\n{'='*40}")
    print(f"{title}")
    print(f"{'='*40}")

# Print Python and path information
print_section("Python Environment")
print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")
print("\nPython Path:")
for path in sys.path:
    print(f" - {path}")

# Test basic import
print_section("Testing Basic Import")
try:
    from google.cloud import discoveryengine
    print("✅ Successfully imported google.cloud.discoveryengine")
    print(f"   Location: {discoveryengine.__file__}")
except Exception as e:
    print(f"❌ Failed to import google.cloud.discoveryengine: {e}")

# Test importing the orchestrator
print_section("Testing AgentOrchestrator Import")
try:
    from neoserve_ai.agents.orchestrator import AgentOrchestrator
    print("✅ Successfully imported AgentOrchestrator")
    print(f"   Location: {AgentOrchestrator.__module__}")
except Exception as e:
    print(f"❌ Failed to import AgentOrchestrator: {e}")

# Test importing knowledge_agent directly
print_section("Testing KnowledgeBaseAgent Import")
try:
    from neoserve_ai.agents.knowledge_agent import KnowledgeBaseAgent
    print("✅ Successfully imported KnowledgeBaseAgent")
    print(f"   Location: {KnowledgeBaseAgent.__module__}")
except Exception as e:
    print(f"❌ Failed to import KnowledgeBaseAgent: {e}")

# Check if the module is in sys.modules
print_section("Checking sys.modules")
if 'google.cloud.discoveryengine' in sys.modules:
    print("✅ google.cloud.discoveryengine is in sys.modules")
    print(f"   Location: {sys.modules['google.cloud.discoveryengine'].__file__}")
else:
    print("❌ google.cloud.discoveryengine is NOT in sys.modules")

# Try to import the module with importlib
print_section("Testing importlib.import_module")
try:
    module = importlib.import_module('google.cloud.discoveryengine')
    print(f"✅ Successfully imported with importlib: {module}")
    print(f"   Location: {module.__file__}")
except Exception as e:
    print(f"❌ Failed to import with importlib: {e}")
