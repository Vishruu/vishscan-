"""
Utility functions for file handling and validation
"""

import os
from typing import List, Tuple


class FileUtils:
    """File system helpers with Android compatibility"""

    @staticmethod
    def get_output_dir() -> str:
        """Get a safe output directory"""
        # Try external storage first, fallback to app dir
        candidates = ["/sdcard/VishScan", "./output", "/storage/emulated/0/VishScan"]

        for path in candidates:
            try:
                os.makedirs(path, exist_ok=True)
                # Test write
                test_file = os.path.join(path, ".test")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                return path
            except Exception:
                continue

        # Absolute fallback
        os.makedirs("./output", exist_ok=True)
        return "./output"

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    @staticmethod
    def get_file_info(path: str) -> dict:
        """Get file metadata"""
        try:
            stat = os.stat(path)
            return {
                "name": os.path.basename(path),
                "size": FileUtils.format_size(stat.st_size),
                "size_bytes": stat.st_size,
                "modified": stat.st_mtime,
            }
        except Exception:
            return {"name": os.path.basename(path), "size": "unknown", "size_bytes": 0}