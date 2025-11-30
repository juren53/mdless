#!/usr/bin/env python3
"""Interactive config editor for mdless-py."""

import yaml
from pathlib import Path
import sys

# Available colors
AVAILABLE_COLORS = [
    'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white',
    'bright_black', 'bright_red', 'bright_green', 'bright_yellow',
    'bright_blue', 'bright_magenta', 'bright_cyan', 'bright_white',
    'bold', 'italic', 'underline'
]

CONFIG_PATH = Path.home() / 'AppData' / 'Roaming' / 'mdless-py' / 'config.yaml'


def load_config():
    """Load the current config."""
    if not CONFIG_PATH.exists():
        print(f"Config file not found at: {CONFIG_PATH}")
        sys.exit(1)
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_config(config):
    """Save config to file."""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    print(f"\n✓ Config saved to: {CONFIG_PATH}")


def show_colors():
    """Display available colors."""
    print("\nAvailable colors:")
    print("  Basic: black, red, green, yellow, blue, magenta, cyan, white")
    print("  Bright: bright_black (gray), bright_red, bright_green, bright_yellow,")
    print("          bright_blue, bright_magenta, bright_cyan, bright_white")
    print("  Styles: bold, italic, underline")


def edit_color_settings(config):
    """Interactive color editor."""
    colors = config.get('colors', {})
    
    print("\n" + "="*60)
    print("Color Settings Editor")
    print("="*60)
    
    print("\nCurrent color settings:")
    for i, (key, value) in enumerate(colors.items(), 1):
        print(f"  {i:2}. {key:15} = {value}")
    
    print("\nOptions:")
    print("  1-15: Edit a specific color")
    print("  a:    Show available colors")
    print("  s:    Save and exit")
    print("  q:    Quit without saving")
    
    while True:
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == 'q':
            print("Exiting without saving.")
            return False
        elif choice == 's':
            return True
        elif choice == 'a':
            show_colors()
        elif choice.isdigit():
            idx = int(choice)
            items = list(colors.items())
            if 1 <= idx <= len(items):
                key, current = items[idx - 1]
                print(f"\nEditing: {key} (current: {current})")
                show_colors()
                new_value = input(f"Enter new color for {key} [or press Enter to keep '{current}']: ").strip()
                
                if new_value:
                    if new_value not in AVAILABLE_COLORS:
                        print(f"⚠ Warning: '{new_value}' is not in the standard color list")
                        confirm = input("Use it anyway? (y/n): ").strip().lower()
                        if confirm != 'y':
                            continue
                    colors[key] = new_value
                    print(f"✓ Updated {key} to '{new_value}'")
            else:
                print("Invalid number. Try again.")
        else:
            print("Invalid choice. Try again.")


def quick_edit_headings(config):
    """Quick editor for just headings."""
    colors = config.get('colors', {})
    
    print("\n" + "="*60)
    print("Quick Heading Color Editor")
    print("="*60)
    
    print("\nCurrent heading colors:")
    for i in range(1, 7):
        key = f'heading{i}'
        print(f"  {key} (#{i * '#'}): {colors.get(key, 'not set')}")
    
    show_colors()
    
    print("\nEnter new colors (or press Enter to keep current):")
    
    for i in range(1, 7):
        key = f'heading{i}'
        current = colors.get(key, 'not set')
        new_value = input(f"  {key} [{current}]: ").strip()
        
        if new_value:
            if new_value not in AVAILABLE_COLORS:
                print(f"    ⚠ Warning: '{new_value}' is not standard")
            colors[key] = new_value
            print(f"    ✓ Updated to '{new_value}'")
    
    confirm = input("\nSave changes? (y/n): ").strip().lower()
    return confirm == 'y'


def main():
    """Main entry point."""
    print("="*60)
    print("mdless-py Configuration Editor")
    print("="*60)
    print(f"\nConfig file: {CONFIG_PATH}")
    
    config = load_config()
    
    print("\nWhat would you like to edit?")
    print("  1. All color settings (interactive)")
    print("  2. Heading colors only (quick)")
    print("  3. View current config")
    print("  q. Quit")
    
    choice = input("\nChoice: ").strip()
    
    if choice == '1':
        if edit_color_settings(config):
            save_config(config)
    elif choice == '2':
        if quick_edit_headings(config):
            save_config(config)
        else:
            print("Changes discarded.")
    elif choice == '3':
        print("\nCurrent configuration:")
        print(yaml.dump(config, default_flow_style=False, sort_keys=False))
    elif choice == 'q':
        print("Goodbye!")
    else:
        print("Invalid choice.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. No changes saved.")
        sys.exit(0)
