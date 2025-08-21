#!/usr/bin/env python3
"""
Simple launcher script for the N-Grams Typing Test application.
Run this file to start the game directly.
"""

import sys
import os

def main():
    """Main launcher function."""
    print("🎯 N-Grams Typing Test - Launcher")
    print("=" * 40)
    
    try:
        # Import and run the game controller
        from game_controller import GameController
        
        print("✅ Game components loaded successfully!")
        print("🚀 Starting the typing test...")
        print("💡 Use ESC key or close window to exit")
        print("-" * 40)
        
        # Create and run the game
        controller = GameController()
        controller.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all required files are in the same directory")
        print("💡 Install pygame: pip install pygame")
        return 1
        
    except Exception as e:
        print(f"❌ Error starting game: {e}")
        print("💡 Check the README.md file for troubleshooting tips")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
