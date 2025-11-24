#!/usr/bin/env python3
"""
Script to duplicate the INSIGHTs SIM-U application for a new criteria set.

Usage:
    python scripts/create_criteria_instance.py --name "Clinical_Reasoning" --port 8503

This creates a new directory in instances/ with updated criteria groups that you can customize.
"""

import argparse
import shutil
from pathlib import Path
import re


def create_instance(source_dir: Path, target_name: str, port: int = 8502):
    """
    Create a new criteria instance by copying and updating files.
    
    Args:
        source_dir: Path to the source application directory (e.g., instances/professional_integrity)
        target_name: Name for the new criteria (e.g., "Clinical_Reasoning")
        port: Port number for the new Streamlit instance
    """
    
    # Create target directory in instances folder
    instances_dir = source_dir.parent
    target_dir = instances_dir / target_name.lower().replace(" ", "_")
    
    if target_dir.exists():
        print(f"❌ Directory {target_dir} already exists!")
        response = input("Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
        shutil.rmtree(target_dir)
    
    print(f"📁 Creating new instance: {target_dir}")
    target_dir.mkdir(parents=True)
    
    # Files to copy and modify
    files_to_copy = [
        'streamlit_app.py',
        'simu_prototype.py',
        'requirements.txt',
        'INSIGHTs_SimU_prototype_README.txt'
    ]
    
    # Copy and update files
    for filename in files_to_copy:
        source_file = source_dir / filename
        target_file = target_dir / filename
        
        if not source_file.exists():
            print(f"⚠️  Skipping {filename} (not found)")
            continue
            
        print(f"📄 Copying {filename}...")
        
        # Read source content
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply transformations based on file type
        if filename == 'streamlit_app.py':
            content = update_streamlit_app(content, target_name, port)
        elif filename == 'simu_prototype.py':
            content = update_simu_prototype(content, target_name)
        
        # Write to target
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Create virtual environment
    print(f"🐍 Creating virtual environment...")
    venv_dir = target_dir / '.venv'
    import subprocess
    subprocess.run(['python3', '-m', 'venv', str(venv_dir)], check=True)
    
    # Install requirements
    print(f"📦 Installing requirements...")
    pip_path = venv_dir / 'bin' / 'pip'
    requirements_file = target_dir / 'requirements.txt'
    subprocess.run([str(pip_path), 'install', '-r', str(requirements_file)], check=True)
    
    # Create a launch script
    launch_script = target_dir / 'run.sh'
    with open(launch_script, 'w') as f:
        f.write(f"""#!/bin/bash
# Launch script for {target_name} SIM-U application

cd "$(dirname "$0")"
source .venv/bin/activate
streamlit run streamlit_app.py --server.port {port}
""")
    launch_script.chmod(0o755)
    
    print(f"\n✅ Success! New instance created at: {target_dir}")
    print(f"\n📝 Next steps:")
    print(f"   1. cd {target_dir}")
    print(f"   2. Edit simu_prototype.py and update the GROUPS dictionary with your criteria")
    print(f"   3. Run: ./run.sh  (or: source .venv/bin/activate && streamlit run streamlit_app.py --server.port {port})")
    print(f"\n🌐 The app will be available at: http://localhost:{port}")


def update_streamlit_app(content: str, target_name: str, port: int) -> str:
    """Update streamlit_app.py with new criteria name and port."""
    
    # Update page title
    content = re.sub(
        r'page_title="INSIGHTs Sim-U Demo"',
        f'page_title="INSIGHTs Sim-U - {target_name}"',
        content
    )
    
    # Update schema info message (update the criteria names)
    content = re.sub(
        r'Professional Integrity criteria \(PI_01, PI_02, PI_03\)',
        f'{target_name} criteria (update this message)',
        content
    )
    
    # Add a note in the title or header about which criteria set this is
    # Look for the first st.title or st.header and add a badge
    content = re.sub(
        r'(st\.title\(["\'].*?["\']\))',
        f'\\1\n        st.caption(f"**Criteria Set:** {target_name}")',
        content,
        count=1
    )
    
    return content


def update_simu_prototype(content: str, target_name: str) -> str:
    """Update simu_prototype.py with placeholder criteria groups."""
    
    # Create a template GROUPS structure with instructions
    new_groups = f'''GROUPS = {{
    # TODO: Update these criteria groups for {target_name}
    # Each key is a criterion name, each value is a list of element names
    # These element names become column names in the generated data
    
    "CRITERION_01_Example": [
        "element_1",
        "element_2",
        "element_3",
        "element_4",
    ],
    "CRITERION_02_Example": [
        "element_5",
        "element_6",
        "element_7",
        "element_8",
    ],
    "CRITERION_03_Example": [
        "element_9",
        "element_10",
        "element_11",
        "element_12",
    ],
    "CRITERION_04_Example": [
        "element_13",
        "element_14",
        "element_15",
        "element_16",
    ],
}}'''
    
    # Replace the GROUPS dictionary
    content = re.sub(
        r'GROUPS = \{[^}]+\{[^}]+\}[^}]+\{[^}]+\}[^}]+\{[^}]+\}[^}]+\{[^}]+\}\s*\}',
        new_groups,
        content,
        flags=re.DOTALL
    )
    
    return content


def main():
    parser = argparse.ArgumentParser(
        description='Create a new INSIGHTs SIM-U instance for different criteria'
    )
    parser.add_argument(
        '--name',
        required=True,
        help='Name for the new criteria set (e.g., "Clinical_Reasoning")'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8502,
        help='Port number for the new Streamlit instance (default: 8502)'
    )
    
    args = parser.parse_args()
    
    # Get the source directory (use professional_integrity as template)
    script_dir = Path(__file__).resolve().parent
    source_dir = script_dir.parent / "instances" / "professional_integrity"
    
    if not source_dir.exists():
        print(f"❌ Template directory not found: {source_dir}")
        print("Please ensure the professional_integrity instance exists.")
        return
    
    create_instance(source_dir, args.name, args.port)


if __name__ == '__main__':
    main()
