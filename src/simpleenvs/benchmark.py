#!/usr/bin/env python3
"""
SimpleEnvs vs python-dotenv Performance Benchmark
Includes Secure API benchmarking with improved dependency management
"""

import asyncio
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List


def check_dependencies():
    """Check and guide user for missing dependencies"""
    missing_deps = []
    install_commands = []

    # Check python-dotenv
    try:
        import dotenv

        DOTENV_AVAILABLE = True
    except ImportError:
        DOTENV_AVAILABLE = False
        missing_deps.append("python-dotenv")

    # Check simpleenvs
    try:
        import simpleenvs

        SIMPLEENVS_AVAILABLE = True
    except ImportError:
        SIMPLEENVS_AVAILABLE = False
        missing_deps.append("simpleenvs-python")

    if missing_deps:
        print("❌ Missing required dependencies for benchmarking!")
        print("=" * 60)

        # Show what's missing
        print("Missing packages:")
        for dep in missing_deps:
            print(f"  • {dep}")

        print("\n📦 Installation Options:")
        print("=" * 60)

        # Option 1: Install benchmark extras (recommended)
        print("🚀 Option 1 (Recommended): Install benchmark dependencies")
        print("   pip install 'simpleenvs-python[benchmark]'")
        print("   This installs SimpleEnvs with benchmark dependencies")

        # Option 2: Manual installation
        print("\n🔧 Option 2: Manual installation")
        if "python-dotenv" in missing_deps:
            print("   pip install python-dotenv")
        if "simpleenvs-python" in missing_deps:
            print("   pip install simpleenvs-python")

        # Option 3: Dev environment
        print("\n🛠️  Option 3: For development")
        print("   pip install -e '.[benchmark]'")
        print("   Use this if you're working on SimpleEnvs source code")

        print("\n💡 What each package does:")
        print(
            "  • python-dotenv: Comparison baseline (the library we're benchmarking against)"
        )
        print("  • simpleenvs-python: Our high-performance .env loader")

        print("\n🔄 After installation, run this benchmark again:")
        print(f"   python {' '.join(sys.argv)}")

        sys.exit(1)

    return DOTENV_AVAILABLE, SIMPLEENVS_AVAILABLE


# Check dependencies first
DOTENV_AVAILABLE, SIMPLEENVS_AVAILABLE = check_dependencies()

# Import after dependency check
if DOTENV_AVAILABLE:
    from dotenv import load_dotenv as dotenv_load

if SIMPLEENVS_AVAILABLE:
    import simpleenvs
    from simpleenvs import get_secure
    from simpleenvs import load_dotenv as simpleenvs_load
    from simpleenvs import load_dotenv_secure

    SIMPLEENVS_SECURE_AVAILABLE = True
else:
    SIMPLEENVS_SECURE_AVAILABLE = False


class BenchmarkRunner:
    """Performance benchmark runner"""

    def __init__(self, rounds: int = 10):
        self.rounds = rounds
        self.results = {}

    def create_test_env_file(self, var_count: int, file_suffix: str = "") -> str:
        """Create test .env file for benchmarking"""
        # Create temporary file in current directory for Secure API
        import uuid

        # Generate safe filename (relative path)
        filename = f"benchmark_test_{uuid.uuid4().hex[:8]}.env{file_suffix}"
        path = os.path.join(".", filename)

        try:
            with open(path, "w") as f:
                f.write("# Test .env file\n")
                f.write("# Generated for benchmarking\n\n")

                for i in range(var_count):
                    if i % 4 == 0:
                        f.write(f"VAR_{i:04d}=string_value_{i}\n")
                    elif i % 4 == 1:
                        f.write(f"NUM_{i:04d}={i}\n")
                    elif i % 4 == 2:
                        f.write(f"BOOL_{i:04d}={'true' if i % 2 == 0 else 'false'}\n")
                    else:
                        f.write(f"PATH_{i:04d}=/path/to/file_{i}.txt\n")

                # Add some complex values
                f.write('DB_URL="postgresql://user:pass@localhost:5432/mydb"\n')
                f.write("API_KEY=abc123def456ghi789\n")
                f.write("DEBUG=true\n")
                f.write("PORT=8080\n")
                f.write("TIMEOUT=30.5\n")

                # Add security test variables
                f.write("SECRET_KEY=super-secret-jwt-key-here\n")
                f.write("DATABASE_PASSWORD=secure-db-password-123\n")
                f.write("ENCRYPTION_KEY=encryption-key-for-sensitive-data\n")

        except Exception:
            if os.path.exists(path):
                os.unlink(path)
            raise

        return path

    def clear_env_vars(self, prefix_list: List[str]):
        """Clean up test environment variables"""
        keys_to_remove = []
        for key in os.environ:
            for prefix in prefix_list:
                if key.startswith(prefix):
                    keys_to_remove.append(key)

        for key in keys_to_remove:
            del os.environ[key]

    def measure_function(self, func, *args, **kwargs) -> float:
        """Measure function execution time"""
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        return end_time - start_time

    async def measure_async_function(self, func, *args, **kwargs) -> float:
        """Measure async function execution time"""
        start_time = time.perf_counter()
        await func(*args, **kwargs)
        end_time = time.perf_counter()
        return end_time - start_time

    def run_benchmark(
        self, name: str, func, test_file: str, rounds: int = None
    ) -> Dict[str, float]:
        """Run individual benchmark"""
        if rounds is None:
            rounds = self.rounds

        times = []
        prefixes = [
            "VAR_",
            "NUM_",
            "BOOL_",
            "PATH_",
            "DB_",
            "API_",
            "DEBUG",
            "PORT",
            "TIMEOUT",
            "SECRET_",
            "DATABASE_",
            "ENCRYPTION_",
        ]

        print(f"🔄 Running {name} benchmark... (rounds: {rounds})")

        for i in range(rounds):
            # Clean environment variables
            self.clear_env_vars(prefixes)

            # Also clean SimpleEnvs secure data
            if "Secure" in name and SIMPLEENVS_AVAILABLE:
                simpleenvs.clear()

            # Measure execution time
            exec_time = self.measure_function(func, test_file)
            times.append(exec_time)

            if (i + 1) % max(1, rounds // 4) == 0:
                print(f"  Progress: {i + 1}/{rounds}")

        # Calculate statistics
        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0,
            "times": times,
        }

    async def run_async_benchmark(
        self, name: str, func, test_file: str, rounds: int = None
    ) -> Dict[str, float]:
        """Run async benchmark"""
        if rounds is None:
            rounds = self.rounds

        times = []
        prefixes = [
            "VAR_",
            "NUM_",
            "BOOL_",
            "PATH_",
            "DB_",
            "API_",
            "DEBUG",
            "PORT",
            "TIMEOUT",
            "SECRET_",
            "DATABASE_",
            "ENCRYPTION_",
        ]

        print(f"🔄 Running {name} benchmark... (rounds: {rounds})")

        for i in range(rounds):
            # Clean environment variables and secure data
            self.clear_env_vars(prefixes)
            if SIMPLEENVS_AVAILABLE:
                simpleenvs.clear()

            # Measure execution time
            exec_time = await self.measure_async_function(func, test_file)
            times.append(exec_time)

            if (i + 1) % max(1, rounds // 4) == 0:
                print(f"  Progress: {i + 1}/{rounds}")

        # Calculate statistics
        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0,
            "times": times,
        }

    def compare_performance(
        self, var_count: int, include_secure: bool = False
    ) -> Dict[str, Any]:
        """Run performance comparison"""
        print(f"\n📊 Benchmarking with {var_count} variables...")
        if include_secure:
            print("🔒 Including Secure API benchmark")

        # Create test file
        test_file = self.create_test_env_file(var_count)

        try:
            results = {
                "var_count": var_count,
                "file_size": Path(test_file).stat().st_size,
            }

            # python-dotenv benchmark
            if DOTENV_AVAILABLE:
                results["dotenv"] = self.run_benchmark(
                    "python-dotenv", dotenv_load, test_file
                )

            # simpleenvs standard benchmark
            if SIMPLEENVS_AVAILABLE:
                results["simpleenvs"] = self.run_benchmark(
                    "SimpleEnvs", simpleenvs_load, test_file
                )

            # simpleenvs secure benchmark (optional)
            if include_secure and SIMPLEENVS_SECURE_AVAILABLE:
                # Synchronous secure benchmark
                results["simpleenvs_secure"] = self.run_benchmark(
                    "SimpleEnvs Secure", load_dotenv_secure, test_file
                )

                # Asynchronous secure benchmark
                async def async_secure_load(file_path):
                    await simpleenvs.load_secure(file_path)

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    results["simpleenvs_async_secure"] = loop.run_until_complete(
                        self.run_async_benchmark(
                            "SimpleEnvs Async Secure", async_secure_load, test_file
                        )
                    )
                finally:
                    loop.close()

            return results

        finally:
            # Clean up test file
            try:
                os.unlink(test_file)
            except OSError:
                pass

    def print_results(self, results: Dict[str, Any]):
        """Print benchmark results"""
        var_count = results["var_count"]
        file_size = results["file_size"]

        print(f"\n{'=' * 70}")
        print(f"📈 Results: {var_count} variables (file size: {file_size:,} bytes)")
        print(f"{'=' * 70}")

        # Basic comparison (dotenv vs simpleenvs)
        if "dotenv" in results and "simpleenvs" in results:
            dotenv_mean = results["dotenv"]["mean"]
            simpleenvs_mean = results["simpleenvs"]["mean"]

            print(f"🐍 python-dotenv:")
            print(f"   Average: {dotenv_mean * 1000:.3f}ms")
            print(f"   Median: {results['dotenv']['median'] * 1000:.3f}ms")
            print(
                f"   Min/Max: {results['dotenv']['min'] * 1000:.3f}ms / {results['dotenv']['max'] * 1000:.3f}ms"
            )

            print(f"\n⚡ SimpleEnvs (Standard):")
            print(f"   Average: {simpleenvs_mean * 1000:.3f}ms")
            print(f"   Median: {results['simpleenvs']['median'] * 1000:.3f}ms")
            print(
                f"   Min/Max: {results['simpleenvs']['min'] * 1000:.3f}ms / {results['simpleenvs']['max'] * 1000:.3f}ms"
            )

            # Comparison
            ratio = dotenv_mean / simpleenvs_mean
            if ratio > 1:
                print(f"\n🏆 SimpleEnvs is {ratio:.2f}x faster!")
            else:
                print(f"\n🏆 python-dotenv is {1 / ratio:.2f}x faster!")

        # Secure API results
        if "simpleenvs_secure" in results:
            secure_mean = results["simpleenvs_secure"]["mean"]
            print(f"\n🔒 SimpleEnvs Secure (Sync):")
            print(f"   Average: {secure_mean * 1000:.3f}ms")
            print(f"   Median: {results['simpleenvs_secure']['median'] * 1000:.3f}ms")

            # Compare with standard SimpleEnvs
            if "simpleenvs" in results:
                overhead = (secure_mean / results["simpleenvs"]["mean"] - 1) * 100
                print(f"   Security overhead: {overhead:.1f}%")

        if "simpleenvs_async_secure" in results:
            async_secure_mean = results["simpleenvs_async_secure"]["mean"]
            print(f"\n🔒⚡ SimpleEnvs Async Secure:")
            print(f"   Average: {async_secure_mean * 1000:.3f}ms")
            print(
                f"   Median: {results['simpleenvs_async_secure']['median'] * 1000:.3f}ms"
            )

            # Compare with sync secure
            if "simpleenvs_secure" in results:
                async_improvement = (
                    results["simpleenvs_secure"]["mean"] / async_secure_mean - 1
                ) * 100
                if async_improvement > 0:
                    print(f"   Async improvement: {async_improvement:.1f}% faster")
                else:
                    print(f"   Async overhead: {-async_improvement:.1f}%")

        # Individual results for partial availability
        elif "dotenv" in results:
            print(f"🐍 python-dotenv: {results['dotenv']['mean'] * 1000:.3f}ms")

        elif "simpleenvs" in results:
            print(f"⚡ SimpleEnvs: {results['simpleenvs']['mean'] * 1000:.3f}ms")

    def run_comprehensive_benchmark(self, include_secure: bool = False):
        """Run comprehensive benchmark suite"""
        print("🚀 SimpleEnvs vs python-dotenv Performance Benchmark")
        if include_secure:
            print("🔒 Including Secure API performance tests")
        print("=" * 70)

        # Availability check
        available_libs = []
        if DOTENV_AVAILABLE:
            available_libs.append("python-dotenv")
        if SIMPLEENVS_AVAILABLE:
            available_libs.append("SimpleEnvs")

        print(f"📦 Available libraries: {', '.join(available_libs)}")

        if include_secure and not SIMPLEENVS_SECURE_AVAILABLE:
            print("⚠️  Secure API not available.")
            include_secure = False

        # Test with various sizes
        test_sizes = [10, 50, 100, 500, 1000, 5000]
        all_results = []

        for size in test_sizes:
            try:
                result = self.compare_performance(size, include_secure)
                all_results.append(result)
                self.print_results(result)

            except Exception as e:
                print(f"❌ {size} variable test failed: {e}")

        # Print summary
        self.print_summary(all_results, include_secure)

    def print_summary(
        self, all_results: List[Dict[str, Any]], include_secure: bool = False
    ):
        """Print overall summary"""
        if not all_results:
            return

        print(f"\n{'=' * 90}")
        print("📊 Overall Summary")
        print(f"{'=' * 90}")

        if include_secure:
            # Summary including Secure API
            print(
                f"{'Vars':>4} | {'FileSize':>8} | {'dotenv':>8} | {'Simple':>8} | {'Secure':>8} | {'AsyncSec':>8} | {'Ratio':>6}"
            )
            print("-" * 90)

            for result in all_results:
                var_count = result["var_count"]
                file_size = result["file_size"]

                dotenv_time = result.get("dotenv", {}).get("mean", 0) * 1000
                simpleenvs_time = result.get("simpleenvs", {}).get("mean", 0) * 1000
                secure_time = result.get("simpleenvs_secure", {}).get("mean", 0) * 1000
                async_secure_time = (
                    result.get("simpleenvs_async_secure", {}).get("mean", 0) * 1000
                )

                ratio = (
                    dotenv_time / simpleenvs_time
                    if dotenv_time > 0 and simpleenvs_time > 0
                    else 0
                )

                print(
                    f"{var_count:>4} | {file_size:>6}B | {dotenv_time:>6.1f}ms | {simpleenvs_time:>6.1f}ms | "
                    f"{secure_time:>6.1f}ms | {async_secure_time:>6.1f}ms | {ratio:>4.1f}x"
                )
        else:
            # Standard summary
            print(
                f"{'Variables':>8} | {'File Size':>10} | {'dotenv(ms)':>12} | {'SimpleEnvs(ms)':>15} | {'Ratio':>8}"
            )
            print("-" * 70)

            for result in all_results:
                var_count = result["var_count"]
                file_size = result["file_size"]

                dotenv_time = result.get("dotenv", {}).get("mean", 0) * 1000
                simpleenvs_time = result.get("simpleenvs", {}).get("mean", 0) * 1000

                if dotenv_time > 0 and simpleenvs_time > 0:
                    ratio = dotenv_time / simpleenvs_time
                    print(
                        f"{var_count:>8} | {file_size:>8}B | {dotenv_time:>10.3f} | {simpleenvs_time:>13.3f} | {ratio:>6.2f}x"
                    )
                elif dotenv_time > 0:
                    print(
                        f"{var_count:>8} | {file_size:>8}B | {dotenv_time:>10.3f} | {'N/A':>13} | {'N/A':>8}"
                    )
                elif simpleenvs_time > 0:
                    print(
                        f"{var_count:>8} | {file_size:>8}B | {'N/A':>10} | {simpleenvs_time:>13.3f} | {'N/A':>8}"
                    )

        # Secure API analysis
        if include_secure:
            print(f"\n🔒 Security Performance Analysis:")
            total_overhead = 0
            count = 0

            for result in all_results:
                if "simpleenvs" in result and "simpleenvs_secure" in result:
                    base_time = result["simpleenvs"]["mean"]
                    secure_time = result["simpleenvs_secure"]["mean"]
                    overhead = (secure_time / base_time - 1) * 100
                    total_overhead += overhead
                    count += 1

            if count > 0:
                avg_overhead = total_overhead / count
                print(f"   Average security overhead: {avg_overhead:.1f}%")
                if avg_overhead < 20:
                    print("   ✅ Excellent performance for security features!")
                elif avg_overhead < 50:
                    print("   ✅ Reasonable performance for security features")
                else:
                    print("   ⚠️  Noticeable performance impact from security features")


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="SimpleEnvs vs python-dotenv benchmark"
    )
    parser.add_argument(
        "--rounds",
        "-r",
        type=int,
        default=10,
        help="Number of test rounds per benchmark",
    )
    parser.add_argument(
        "--size", "-s", type=int, help="Test only specific size (number of variables)"
    )
    parser.add_argument(
        "--quick", "-q", action="store_true", help="Quick test (3 rounds)"
    )
    parser.add_argument(
        "--secure", action="store_true", help="Include Secure API benchmark"
    )

    args = parser.parse_args()

    if args.quick:
        args.rounds = 3

    runner = BenchmarkRunner(rounds=args.rounds)

    if args.size:
        # Test specific size only
        result = runner.compare_performance(args.size, args.secure)
        runner.print_results(result)
    else:
        # Comprehensive benchmark
        runner.run_comprehensive_benchmark(args.secure)


if __name__ == "__main__":
    main()
