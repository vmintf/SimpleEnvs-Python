#!/usr/bin/env python3
"""
SimpleEnvs vs python-dotenv 성능 벤치마크
Secure API 벤치마크 포함
"""

import os
import time
import tempfile
import statistics
import asyncio
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
    from simpleenvs import load_dotenv_secure, get_secure
    import simpleenvs

    SIMPLEENVS_AVAILABLE = True
    SIMPLEENVS_SECURE_AVAILABLE = True
except ImportError:
    print("⚠️  simpleenvs-python이 설치되지 않았습니다.")
    SIMPLEENVS_AVAILABLE = False
    SIMPLEENVS_SECURE_AVAILABLE = False


class BenchmarkRunner:
    """벤치마크 실행기"""

    def __init__(self, rounds: int = 10):
        self.rounds = rounds
        self.results = {}

    def create_test_env_file(self, var_count: int, file_suffix: str = "") -> str:
        """테스트용 .env 파일 생성"""
        # Secure API를 위해 현재 디렉토리에 임시 파일 생성
        import uuid

        # 안전한 파일명 생성 (상대 경로)
        filename = f"benchmark_test_{uuid.uuid4().hex[:8]}.env{file_suffix}"
        path = os.path.join(".", filename)

        try:
            with open(path, 'w') as f:
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

                # 보안 테스트용 변수들 추가
                f.write("SECRET_KEY=super-secret-jwt-key-here\n")
                f.write("DATABASE_PASSWORD=secure-db-password-123\n")
                f.write("ENCRYPTION_KEY=encryption-key-for-sensitive-data\n")

        except Exception:
            if os.path.exists(path):
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

    async def measure_async_function(self, func, *args, **kwargs) -> float:
        """비동기 함수 실행 시간 측정"""
        start_time = time.perf_counter()
        await func(*args, **kwargs)
        end_time = time.perf_counter()
        return end_time - start_time

    def run_benchmark(self, name: str, func, test_file: str, rounds: int = None) -> Dict[str, float]:
        """개별 벤치마크 실행"""
        if rounds is None:
            rounds = self.rounds

        times = []
        prefixes = ['VAR_', 'NUM_', 'BOOL_', 'PATH_', 'DB_', 'API_', 'DEBUG', 'PORT', 'TIMEOUT', 'SECRET_', 'DATABASE_',
                    'ENCRYPTION_']

        print(f"🔄 {name} 벤치마크 실행 중... (rounds: {rounds})")

        for i in range(rounds):
            # 환경변수 정리
            self.clear_env_vars(prefixes)

            # SimpleEnvs secure 데이터도 정리
            if 'Secure' in name:
                simpleenvs.clear()

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

    async def run_async_benchmark(self, name: str, func, test_file: str, rounds: int = None) -> Dict[str, float]:
        """비동기 벤치마크 실행"""
        if rounds is None:
            rounds = self.rounds

        times = []
        prefixes = ['VAR_', 'NUM_', 'BOOL_', 'PATH_', 'DB_', 'API_', 'DEBUG', 'PORT', 'TIMEOUT', 'SECRET_', 'DATABASE_',
                    'ENCRYPTION_']

        print(f"🔄 {name} 벤치마크 실행 중... (rounds: {rounds})")

        for i in range(rounds):
            # 환경변수 및 secure 데이터 정리
            self.clear_env_vars(prefixes)
            simpleenvs.clear()

            # 실행 시간 측정
            exec_time = await self.measure_async_function(func, test_file)
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

    def compare_performance(self, var_count: int, include_secure: bool = False) -> Dict[str, Any]:
        """성능 비교 실행"""
        print(f"\n📊 {var_count}개 변수 파일로 벤치마크...")
        if include_secure:
            print("🔒 Secure API 벤치마크 포함")

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

            # simpleenvs 기본 벤치마크
            if SIMPLEENVS_AVAILABLE:
                results['simpleenvs'] = self.run_benchmark(
                    "SimpleEnvs",
                    simpleenvs_load,
                    test_file
                )

            # simpleenvs secure 벤치마크 (옵션)
            if include_secure and SIMPLEENVS_SECURE_AVAILABLE:
                # 동기 secure 벤치마크
                results['simpleenvs_secure'] = self.run_benchmark(
                    "SimpleEnvs Secure",
                    load_dotenv_secure,
                    test_file
                )

                # 비동기 secure 벤치마크
                async def async_secure_load(file_path):
                    await simpleenvs.load_secure(file_path)

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    results['simpleenvs_async_secure'] = loop.run_until_complete(
                        self.run_async_benchmark(
                            "SimpleEnvs Async Secure",
                            async_secure_load,
                            test_file
                        )
                    )
                finally:
                    loop.close()

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

        print(f"\n{'=' * 70}")
        print(f"📈 결과: {var_count}개 변수 (파일 크기: {file_size:,} bytes)")
        print(f"{'=' * 70}")

        # 기본 비교 (dotenv vs simpleenvs)
        if 'dotenv' in results and 'simpleenvs' in results:
            dotenv_mean = results['dotenv']['mean']
            simpleenvs_mean = results['simpleenvs']['mean']

            print(f"🐍 python-dotenv:")
            print(f"   평균: {dotenv_mean * 1000:.3f}ms")
            print(f"   중간값: {results['dotenv']['median'] * 1000:.3f}ms")
            print(f"   최소/최대: {results['dotenv']['min'] * 1000:.3f}ms / {results['dotenv']['max'] * 1000:.3f}ms")

            print(f"\n⚡ SimpleEnvs (기본):")
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

        # Secure API 결과
        if 'simpleenvs_secure' in results:
            secure_mean = results['simpleenvs_secure']['mean']
            print(f"\n🔒 SimpleEnvs Secure (동기):")
            print(f"   평균: {secure_mean * 1000:.3f}ms")
            print(f"   중간값: {results['simpleenvs_secure']['median'] * 1000:.3f}ms")

            # 기본 SimpleEnvs와 비교
            if 'simpleenvs' in results:
                overhead = (secure_mean / results['simpleenvs']['mean'] - 1) * 100
                print(f"   보안 오버헤드: {overhead:.1f}%")

        if 'simpleenvs_async_secure' in results:
            async_secure_mean = results['simpleenvs_async_secure']['mean']
            print(f"\n🔒⚡ SimpleEnvs Async Secure:")
            print(f"   평균: {async_secure_mean * 1000:.3f}ms")
            print(f"   중간값: {results['simpleenvs_async_secure']['median'] * 1000:.3f}ms")

            # 동기 secure와 비교
            if 'simpleenvs_secure' in results:
                async_improvement = (results['simpleenvs_secure']['mean'] / async_secure_mean - 1) * 100
                if async_improvement > 0:
                    print(f"   비동기 개선: {async_improvement:.1f}% 빠름")
                else:
                    print(f"   비동기 오버헤드: {-async_improvement:.1f}%")

        # 독립적인 결과들
        elif 'dotenv' in results:
            print(f"🐍 python-dotenv: {results['dotenv']['mean'] * 1000:.3f}ms")

        elif 'simpleenvs' in results:
            print(f"⚡ SimpleEnvs: {results['simpleenvs']['mean'] * 1000:.3f}ms")

    def run_comprehensive_benchmark(self, include_secure: bool = False):
        """종합 벤치마크 실행"""
        print("🚀 SimpleEnvs vs python-dotenv 성능 벤치마크")
        if include_secure:
            print("🔒 Secure API 성능 테스트 포함")
        print("=" * 70)

        if not (DOTENV_AVAILABLE or SIMPLEENVS_AVAILABLE):
            print("❌ 벤치마크할 라이브러리가 없습니다.")
            return

        if include_secure and not SIMPLEENVS_SECURE_AVAILABLE:
            print("⚠️  Secure API를 사용할 수 없습니다.")
            include_secure = False

        # 다양한 크기로 테스트
        test_sizes = [10, 50, 100, 500, 1000, 5000]
        all_results = []

        for size in test_sizes:
            try:
                result = self.compare_performance(size, include_secure)
                all_results.append(result)
                self.print_results(result)

            except Exception as e:
                print(f"❌ {size}개 변수 테스트 실패: {e}")

        # 요약 출력
        self.print_summary(all_results, include_secure)

    def print_summary(self, all_results: List[Dict[str, Any]], include_secure: bool = False):
        """전체 결과 요약"""
        if not all_results:
            return

        print(f"\n{'=' * 90}")
        print("📊 전체 요약")
        print(f"{'=' * 90}")

        if include_secure:
            # Secure API 포함 요약
            print(
                f"{'변수':>4} | {'파일크기':>8} | {'dotenv':>8} | {'Simple':>8} | {'Secure':>8} | {'AsyncSec':>8} | {'비율':>6}")
            print("-" * 90)

            for result in all_results:
                var_count = result['var_count']
                file_size = result['file_size']

                dotenv_time = result.get('dotenv', {}).get('mean', 0) * 1000
                simpleenvs_time = result.get('simpleenvs', {}).get('mean', 0) * 1000
                secure_time = result.get('simpleenvs_secure', {}).get('mean', 0) * 1000
                async_secure_time = result.get('simpleenvs_async_secure', {}).get('mean', 0) * 1000

                ratio = dotenv_time / simpleenvs_time if dotenv_time > 0 and simpleenvs_time > 0 else 0

                print(f"{var_count:>4} | {file_size:>6}B | {dotenv_time:>6.1f}ms | {simpleenvs_time:>6.1f}ms | "
                      f"{secure_time:>6.1f}ms | {async_secure_time:>6.1f}ms | {ratio:>4.1f}x")
        else:
            # 기본 요약
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

        # Secure API 분석
        if include_secure:
            print(f"\n🔒 보안 성능 분석:")
            total_overhead = 0
            count = 0

            for result in all_results:
                if 'simpleenvs' in result and 'simpleenvs_secure' in result:
                    base_time = result['simpleenvs']['mean']
                    secure_time = result['simpleenvs_secure']['mean']
                    overhead = (secure_time / base_time - 1) * 100
                    total_overhead += overhead
                    count += 1

            if count > 0:
                avg_overhead = total_overhead / count
                print(f"   평균 보안 오버헤드: {avg_overhead:.1f}%")
                if avg_overhead < 20:
                    print("   ✅ 보안 기능 대비 매우 효율적인 성능!")
                elif avg_overhead < 50:
                    print("   ✅ 보안 기능 대비 합리적인 성능")
                else:
                    print("   ⚠️  보안 기능으로 인한 성능 영향 있음")


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="SimpleEnvs vs python-dotenv 벤치마크")
    parser.add_argument("--rounds", "-r", type=int, default=10, help="각 테스트 라운드 수")
    parser.add_argument("--size", "-s", type=int, help="특정 크기로만 테스트 (변수 개수)")
    parser.add_argument("--quick", "-q", action="store_true", help="빠른 테스트 (3라운드)")
    parser.add_argument("--secure", action="store_true", help="Secure API 벤치마크 포함")

    args = parser.parse_args()

    if args.quick:
        args.rounds = 3

    runner = BenchmarkRunner(rounds=args.rounds)

    if args.size:
        # 특정 크기만 테스트
        result = runner.compare_performance(args.size, args.secure)
        runner.print_results(result)
    else:
        # 종합 벤치마크
        runner.run_comprehensive_benchmark(args.secure)


if __name__ == "__main__":
    main()