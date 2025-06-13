"""
Test runner script for Jammin' Eats
Runs tests in a controlled environment and logs output to a file
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run specified tests and log output"""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Output file
    log_file = logs_dir / "test_output.log"
    
    # Run all tests in these files to identify remaining issues
    test_files = [
        "tests/test_states.py",
        "tests/test_tutorial_completion.py"
    ]
    
    print(f"Running tests and logging to {log_file}")
    
    # Run the tests and capture output
    with open(log_file, "w") as f:
        f.write("=== Jammin' Eats Test Run ===\n\n")
        
        for test_file in test_files:
            f.write(f"\n\n=== Running {test_file} ===\n")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", test_file, "-v", "--no-header", "--showlocals", "-s"],
                    capture_output=True,
                    text=True
                )
                f.write("--- STDOUT ---\n")
                f.write(result.stdout or "No output\n")
                f.write("\n--- STDERR ---\n")
                f.write(result.stderr or "No errors\n")
                f.write(f"\nExit code: {result.returncode}\n")
            except Exception as e:
                f.write(f"Error running test: {e}\n")
    
    # Print the log file content
    print("\nTest output log:")
    with open(log_file, "r") as f:
        print(f.read())
    
    print(f"\nTest log written to {log_file}")

if __name__ == "__main__":
    main()
