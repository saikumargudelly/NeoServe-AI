import sys
from google.cloud import discoveryengine

def main():
    print("Python Path:")
    for path in sys.path:
        print(f"  {path}")
    
    print("\nDiscovery Engine module info:")
    print(f"  Module file: {discoveryengine.__file__}")
    print(f"  Version: {getattr(discoveryengine, '__version__', 'Not available')}")
    
    # Try to create a client
    try:
        client = discoveryengine.DocumentServiceClient()
        print("\nSuccessfully created DocumentServiceClient!")
    except Exception as e:
        print(f"\nError creating client: {e}")

if __name__ == "__main__":
    main()
