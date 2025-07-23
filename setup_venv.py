import os
import sys
from pathlib import Path

def create_venv_symlink(link_path: Path, target_path: Path):
    if link_path.exists() or link_path.is_symlink():
        if link_path.resolve() == target_path.resolve():
            print(f"✅ Symlink already exists: {link_path} → {target_path}")
            return
        else:
            print(f"⚠️ Removing existing link or folder at: {link_path}")
            if link_path.is_symlink() or link_path.is_file():
                link_path.unlink()
            else:
                # Only remove empty directories automatically
                try:
                    link_path.rmdir()
                except OSError:
                    print(f"❌ Cannot remove non-empty directory at {link_path}")
                    sys.exit(1)

    print(f"🔗 Creating symlink: {link_path} → {target_path}")
    try:
        link_path.symlink_to(target_path, target_is_directory=True)
        print("✅ Done.")
    except OSError as e:
        print(f"❌ Failed to create symlink: {e}")
        if os.name == 'nt':
            print("💡 On Windows, run this script as Administrator or enable Developer Mode.")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python link_venv.py /path/to/simulator")
        sys.exit(1)

    simulator_dir = Path(sys.argv[1]).resolve()
    venv_dir = simulator_dir / ".venv"

    if not venv_dir.exists():
        print(f"❌ Virtual environment not found at: {venv_dir}")
        print("💡 You may need to create it first. Refer to https://radio-spectrum.github.io/SHARC/docs/Contributing")
        sys.exit(1)

    current_dir = Path(__file__).resolve().parent
    symlink_path = current_dir / ".venv"

    create_venv_symlink(symlink_path, venv_dir)

if __name__ == "__main__":
    main()
