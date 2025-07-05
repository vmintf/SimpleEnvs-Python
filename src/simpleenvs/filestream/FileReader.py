#!/usr/bin/env python3
"""
GIL-optimized file reader for SimpleEnvs
Ultra-fast file reading using GIL release patterns
"""

import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, Tuple


class GILOptimizedFileReader:
    """
    GIL-aware file reader that maximizes I/O performance
    by strategically using GIL release during file operations
    """

    def __init__(self, max_workers: int = 2):
        """
        Initialize GIL-optimized reader

        Args:
            max_workers: Maximum threads for concurrent reading (default: 2)
        """
        self.max_workers = max_workers
        self._thread_pool: Optional[ThreadPoolExecutor] = None

    def __enter__(self):
        """Context manager entry"""
        self._thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup thread pool"""
        if self._thread_pool:
            self._thread_pool.shutdown(wait=True)
            self._thread_pool = None

    @staticmethod
    def _read_file_chunk(file_path: str, start: int, size: int) -> bytes:
        """
        Read file chunk - runs in separate thread with GIL released during I/O

        Args:
            file_path: Path to file
            start: Starting byte position
            size: Number of bytes to read
        """
        with open(file_path, "rb") as f:
            f.seek(start)
            return f.read(size)

    @staticmethod
    def _read_file_simple(file_path: str, encoding: str = "utf-8") -> str:
        """
        Simple synchronous file read - GIL released during I/O operations

        Args:
            file_path: Path to file
            encoding: File encoding (default: utf-8)
        """
        # GIL is automatically released during the file I/O operations
        with open(file_path, "r", encoding=encoding, buffering=8192) as f:
            return f.read()

    def read_optimized(self, file_path: str, encoding: str = "utf-8") -> str:
        """
        Read file with GIL optimization strategy

        Args:
            file_path: Path to file to read
            encoding: File encoding (default: utf-8)

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If encoding is incorrect
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = Path(file_path).stat().st_size

        # Strategy 1: Small files (< 64KB) - direct read is fastest
        if file_size < 64 * 1024:
            return self._read_file_simple(file_path, encoding)

        # Strategy 2: Medium files (64KB - 4MB) - optimized buffering
        elif file_size < 4 * 1024 * 1024:
            return self._read_file_simple(file_path, encoding)

        # Strategy 3: Large files (> 4MB) - threaded chunked reading
        else:
            return self._read_large_file_threaded(file_path, encoding)

    def _read_large_file_threaded(self, file_path: str, encoding: str) -> str:
        """
        Read large files using threaded approach for maximum GIL utilization

        Args:
            file_path: Path to file
            encoding: File encoding
        """
        file_size = Path(file_path).stat().st_size

        # Calculate optimal chunk size (typically 256KB - 1MB)
        chunk_size = min(1024 * 1024, max(256 * 1024, file_size // 4))

        # Create chunk tasks
        chunks = []
        for start in range(0, file_size, chunk_size):
            size = min(chunk_size, file_size - start)
            chunks.append((start, size))

        # Use thread pool only if it was initialized via context manager
        if self._thread_pool and len(chunks) > 1:
            # Submit all chunk read tasks
            future_to_chunk = {
                self._thread_pool.submit(
                    self._read_file_chunk, file_path, start, size
                ): (start, size)
                for start, size in chunks
            }

            # Collect results in order
            results = [None] * len(chunks)
            for future in as_completed(future_to_chunk):
                start, size = future_to_chunk[future]
                chunk_index = start // (chunks[0][1] if chunks else chunk_size)
                results[chunk_index] = future.result()

            # Combine chunks and decode
            combined = b"".join(results)
            return combined.decode(encoding)

        else:
            # Fallback to simple read if no thread pool or single chunk
            return self._read_file_simple(file_path, encoding)

    def read_multiple_files(self, file_paths: list, encoding: str = "utf-8") -> dict:
        """
        Read multiple files concurrently using GIL optimization

        Args:
            file_paths: List of file paths to read
            encoding: File encoding

        Returns:
            Dictionary mapping file paths to their content
        """
        if not self._thread_pool:
            raise RuntimeError("Must use context manager for concurrent operations")

        # Submit all file read tasks
        future_to_path = {
            self._thread_pool.submit(self._read_file_simple, path, encoding): path
            for path in file_paths
        }

        # Collect results
        results = {}
        for future in as_completed(future_to_path):
            file_path = future_to_path[future]
            try:
                results[file_path] = future.result()
            except Exception as e:
                results[file_path] = f"ERROR: {e}"

        return results


# Convenience functions
def read_env_file_optimized(file_path: str, encoding: str = "utf-8") -> str:
    """
    Convenience function to read a single .env file with GIL optimization

    Args:
        file_path: Path to .env file
        encoding: File encoding

    Returns:
        File content as string
    """
    reader = GILOptimizedFileReader()
    return reader.read_optimized(file_path, encoding)


def read_multiple_env_files(file_paths: list, encoding: str = "utf-8") -> dict:
    """
    Convenience function to read multiple .env files concurrently

    Args:
        file_paths: List of .env file paths
        encoding: File encoding

    Returns:
        Dictionary mapping file paths to their content
    """
    with GILOptimizedFileReader() as reader:
        return reader.read_multiple_files(file_paths, encoding)


# Benchmarking function
def benchmark_against_builtin(file_path: str, iterations: int = 1000) -> dict:
    """
    Benchmark GIL-optimized reader against built-in file reading

    Args:
        file_path: Test file path
        iterations: Number of test iterations

    Returns:
        Dictionary with benchmark results
    """
    import time

    # Benchmark built-in
    start_time = time.perf_counter()
    for _ in range(iterations):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    builtin_time = time.perf_counter() - start_time

    # Benchmark GIL-optimized
    reader = GILOptimizedFileReader()
    start_time = time.perf_counter()
    for _ in range(iterations):
        content = reader.read_optimized(file_path)
    gil_time = time.perf_counter() - start_time

    return {
        "builtin_time_ms": builtin_time * 1000,
        "gil_optimized_time_ms": gil_time * 1000,
        "speedup": builtin_time / gil_time if gil_time > 0 else 0,
        "iterations": iterations,
        "file_size_bytes": Path(file_path).stat().st_size,
    }


if __name__ == "__main__":
    # Example usage and testing
    import tempfile

    # Create test file
    test_content = "TEST_VAR=hello\nDEBUG=true\nPORT=3000\n" * 1000

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(test_content)
        test_file = f.name

    try:
        # Test single file reading
        print("🔧 Testing GIL-optimized file reader...")

        reader = GILOptimizedFileReader()
        content = reader.read_optimized(test_file)
        print(f"✅ Read {len(content)} characters successfully")

        # Test concurrent reading
        print("\n🚀 Testing concurrent file reading...")
        test_files = [test_file] * 5  # Read same file 5 times concurrently

        with GILOptimizedFileReader() as concurrent_reader:
            results = concurrent_reader.read_multiple_files(test_files)
            print(f"✅ Read {len(results)} files concurrently")

        # Benchmark
        print("\n📊 Benchmarking performance...")
        benchmark_results = benchmark_against_builtin(test_file, 100)
        print(f"Built-in time: {benchmark_results['builtin_time_ms']:.2f}ms")
        print(f"GIL-optimized time: {benchmark_results['gil_optimized_time_ms']:.2f}ms")
        print(f"Speedup: {benchmark_results['speedup']:.2f}x")

    finally:
        # Cleanup
        os.unlink(test_file)
