#!/usr/bin/env python3
"""
SimpleEnvs vs python-dotenv 성능 벤치마크
"""

import os
import time
import tempfile
import statistics
from pathlib import Path
from typing import List, Dict, Any

# 벤치마크 대상들
try:
    from dotenv import load_dotenv as dotenv_load

    DOTENV_AVAILABLE = True
except ImportError:
    print("⚠️  python-dotenv가 설치되지 않았습니다. pip install python-dotenv")
    DOTENV_AVAILABLE = False

try:
    from simpleenvs import load_dotenv as simpleenvs_load

    SIMPLEENVS_AVAILABLE = True
except ImportError:
    print("⚠️  simpleenvs-python이 설치되지 않았습니다.")
    SIMPLEENVS_AVAILABLE = False


class BenchmarkRunner:
    """벤치마크 실행기"""

    def __init__(self, rounds: int = 10):
        self.rounds = rounds
        self.results = {}

    def create_test_env_file(self, var_count: int, file_suffix: str = "") -> str:
        """테스트용 .env 파일 생성"""
        # 임시 파일 생성
        fd, path = tempfile.mkstemp(suffix=f".env{file_suffix}", text=True)

        try:
            with os.fdopen(fd, 'w') as f:
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

                # 일부 복잡한 값들 추가
                f.write('DB_URL="postgresql://user:pass@localhost:5432/mydb"\n')
                f.write("API_KEY=abc123def456ghi789\n")
                f.write("DEBUG=true\n")
                f.write("PORT=8080\n")
                f.write("TIMEOUT=30.5\n")

        except Exception:
            os.unlink(path)
            raise

        return path

    def clear_env_vars(self, prefix_list: List[str]):
        """테스트 환경변수들 정리"""
        keys_to_remove = []
        for key in os.environ:
            for prefix in prefix_list:
                if key.startswith(prefix):
                    keys_to_remove.append(key)

        for key in keys_to_remove:
            del os.environ[key]

    def measure_function(self, func, *args, **kwargs) -> float:
        """함수 실행 시간 측정"""
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        return end_time - start_time

    def run_benchmark(self, name: str, func, test_file: str, rounds: int = None) -> Dict[str, float]:
        """개별 벤치마크 실행"""
        if rounds is None:
            rounds = self.rounds

        times = []
        prefixes = ['VAR_', 'NUM_', 'BOOL_', 'PATH_', 'DB_', 'API_', 'DEBUG', 'PORT', 'TIMEOUT']

        print(f"🔄 {name} 벤치마크 실행 중... (rounds: {rounds})")

        for i in range(rounds):
            # 환경변수 정리
            self.clear_env_vars(prefixes)

            # 실행 시간 측정
            exec_time = self.measure_function(func, test_file)
            times.append(exec_time)

            if (i + 1) % max(1, rounds // 4) == 0:
                print(f"  Progress: {i + 1}/{rounds}")

        # 통계 계산
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'times': times
        }

    def compare_performance(self, var_count: int) -> Dict[str, Any]:
        """성능 비교 실행"""
        print(f"\n📊 {var_count}개 변수 파일로 벤치마크...")

        # 테스트 파일 생성
        test_file = self.create_test_env_file(var_count)

        try:
            results = {
                'var_count': var_count,
                'file_size': Path(test_file).stat().st_size
            }

            # python-dotenv 벤치마크
            if DOTENV_AVAILABLE:
                results['dotenv'] = self.run_benchmark(
                    "python-dotenv",
                    dotenv_load,
                    test_file
                )

            # simpleenvs 벤치마크
            if SIMPLEENVS_AVAILABLE:
                results['simpleenvs'] = self.run_benchmark(
                    "SimpleEnvs",
                    simpleenvs_load,
                    test_file
                )

            return results

        finally:
            # 테스트 파일 정리
            try:
                os.unlink(test_file)
            except OSError:
                pass

    def print_results(self, results: Dict[str, Any]):
        """결과 출력"""
        var_count = results['var_count']
        file_size = results['file_size']

        print(f"\n{'=' * 60}")
        print(f"📈 결과: {var_count}개 변수 (파일 크기: {file_size:,} bytes)")
        print(f"{'=' * 60}")

        if 'dotenv' in results and 'simpleenvs' in results:
            dotenv_mean = results['dotenv']['mean']
            simpleenvs_mean = results['simpleenvs']['mean']

            print(f"🐍 python-dotenv:")
            print(f"   평균: {dotenv_mean * 1000:.3f}ms")
            print(f"   중간값: {results['dotenv']['median'] * 1000:.3f}ms")
            print(f"   최소/최대: {results['dotenv']['min'] * 1000:.3f}ms / {results['dotenv']['max'] * 1000:.3f}ms")

            print(f"\n⚡ SimpleEnvs:")
            print(f"   평균: {simpleenvs_mean * 1000:.3f}ms")
            print(f"   중간값: {results['simpleenvs']['median'] * 1000:.3f}ms")
            print(
                f"   최소/최대: {results['simpleenvs']['min'] * 1000:.3f}ms / {results['simpleenvs']['max'] * 1000:.3f}ms")

            # 비교
            ratio = dotenv_mean / simpleenvs_mean
            if ratio > 1:
                print(f"\n🏆 SimpleEnvs가 {ratio:.2f}배 빠름!")
            else:
                print(f"\n🏆 python-dotenv가 {1 / ratio:.2f}배 빠름!")

        elif 'dotenv' in results:
            print(f"🐍 python-dotenv: {results['dotenv']['mean'] * 1000:.3f}ms")

        elif 'simpleenvs' in results:
            print(f"⚡ SimpleEnvs: {results['simpleenvs']['mean'] * 1000:.3f}ms")

    def run_comprehensive_benchmark(self):
        """종합 벤치마크 실행"""
        print("🚀 SimpleEnvs vs python-dotenv 성능 벤치마크")
        print("=" * 60)

        if not (DOTENV_AVAILABLE or SIMPLEENVS_AVAILABLE):
            print("❌ 벤치마크할 라이브러리가 없습니다.")
            return

        # 다양한 크기로 테스트
        test_sizes = [10, 50, 100, 500, 1000, 5000]
        all_results = []

        for size in test_sizes:
            try:
                result = self.compare_performance(size)
                all_results.append(result)
                self.print_results(result)

            except Exception as e:
                print(f"❌ {size}개 변수 테스트 실패: {e}")

        # 요약 출력
        self.print_summary(all_results)

    def print_summary(self, all_results: List[Dict[str, Any]]):
        """전체 결과 요약"""
        if not all_results:
            return

        print(f"\n{'=' * 60}")
        print("📊 전체 요약")
        print(f"{'=' * 60}")

        print(f"{'변수 개수':>8} | {'파일크기':>10} | {'dotenv(ms)':>12} | {'SimpleEnvs(ms)':>15} | {'비율':>8}")
        print("-" * 70)

        for result in all_results:
            var_count = result['var_count']
            file_size = result['file_size']

            dotenv_time = result.get('dotenv', {}).get('mean', 0) * 1000
            simpleenvs_time = result.get('simpleenvs', {}).get('mean', 0) * 1000

            if dotenv_time > 0 and simpleenvs_time > 0:
                ratio = dotenv_time / simpleenvs_time
                print(
                    f"{var_count:>8} | {file_size:>8}B | {dotenv_time:>10.3f} | {simpleenvs_time:>13.3f} | {ratio:>6.2f}x")
            elif dotenv_time > 0:
                print(f"{var_count:>8} | {file_size:>8}B | {dotenv_time:>10.3f} | {'N/A':>13} | {'N/A':>8}")
            elif simpleenvs_time > 0:
                print(f"{var_count:>8} | {file_size:>8}B | {'N/A':>10} | {simpleenvs_time:>13.3f} | {'N/A':>8}")


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="SimpleEnvs vs python-dotenv 벤치마크")
    parser.add_argument("--rounds", "-r", type=int, default=10, help="각 테스트 라운드 수")
    parser.add_argument("--size", "-s", type=int, help="특정 크기로만 테스트 (변수 개수)")
    parser.add_argument("--quick", "-q", action="store_true", help="빠른 테스트 (3라운드)")

    args = parser.parse_args()

    if args.quick:
        args.rounds = 3

    runner = BenchmarkRunner(rounds=args.rounds)

    if args.size:
        # 특정 크기만 테스트
        result = runner.compare_performance(args.size)
        runner.print_results(result)
    else:
        # 종합 벤치마크
        runner.run_comprehensive_benchmark()


if __name__ == "__main__":
    main()