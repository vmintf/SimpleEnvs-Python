import gc
from typing import List, Optional

from .secure import SecureEnvLoader
from .utils import EnvValue


class SecureLoaderManager:
    """
    Manager class for SecureEnvLoader instances with magic method support

    Provides a clean interface for managing and accessing SecureEnvLoader instances
    with pythonic magic methods support.
    """

    def __init__(self, global_loader_ref: Optional[SecureEnvLoader] = None):
        self._global_loader_ref = global_loader_ref

    def get_active_loader(self) -> Optional[SecureEnvLoader]:
        """
        Get active SecureEnvLoader instance

        Returns the currently active SecureEnvLoader by checking:
        1. Global _secure_loader instance (highest priority)
        2. Memory introspection for existing loaders
        3. None if no loader found
        """
        # Priority 1: Check global loader first
        if self._global_loader_ref is not None and self._global_loader_ref.is_loaded():
            return self._global_loader_ref

        # Priority 2: Search memory for existing loaders
        found_loader = self._find_loader_in_memory()
        if found_loader is not None:
            return found_loader

        # Priority 3: No loader found
        return None

    def _find_loader_in_memory(self) -> Optional[SecureEnvLoader]:
        """
        Find existing SecureEnvLoader instance in memory
        """
        try:
            for obj in gc.get_objects():
                if isinstance(obj, SecureEnvLoader):
                    # Safe access to private attribute using getattr
                    env_data = getattr(obj, "_SecureEnvLoader__env_data", None)
                    if env_data:  # Has loaded data
                        return obj
        except Exception:
            pass  # Silently fail if introspection not possible

        return None

    def get_all_loaders(self) -> List[SecureEnvLoader]:
        """Get all SecureEnvLoader instances in memory (for debugging)"""
        loaders = []
        try:
            for obj in gc.get_objects():
                if isinstance(obj, SecureEnvLoader):
                    loaders.append(obj)
        except Exception:
            pass
        return loaders

    def force_delete_all_loaders(self) -> None:
        """
        메모리에서 모든 SecureEnvLoader 인스턴스를 강제로 삭제합니다.
        1. 각 로더의 데이터를 지웁니다 (secure_wipe)
        2. del을 사용해 객체 자체를 메모리에서 제거합니다
        3. 가비지 컬렉션을 강제 실행합니다
        """
        # 현재 메모리에 있는 모든 로더 찾기
        loaders = self.get_all_loaders()

        # 각 로더의 secure_wipe 호출 후 삭제
        for loader in loaders:
            try:
                if hasattr(loader, "secure_wipe"):
                    loader.secure_wipe()
                    # 해당 객체에 대한 참조를 del로 제거
                    del loader
            except Exception:
                pass  # 개별 로더 정리 실패 시 계속 진행

        # 글로벌 참조 정리
        self._global_loader_ref = None

        # 리스트 자체를 비우고 삭제
        loaders.clear()
        del loaders

        # 가비지 컬렉션 강제 실행 (남은 객체들 정리)
        gc.collect()

    # =============================================================================
    # MAGIC METHODS - Pythonic Interface
    # =============================================================================

    def __len__(self) -> int:
        """Return number of SecureEnvLoader instances in memory"""
        return len(self.get_all_loaders())

    def __bool__(self) -> bool:
        """Return True if there's an active loader"""
        return bool(self.get_active_loader())

    def __iter__(self):
        """Iterate over all loaders in memory"""
        return iter(self.get_all_loaders())

    def __contains__(self, loader: SecureEnvLoader) -> bool:
        """Check if a specific loader is in memory"""
        return loader in self.get_all_loaders()

    def __getitem__(self, key: str) -> Optional[EnvValue]:
        """Get secure environment variable by key"""
        loader = self.get_active_loader()
        return loader.get_secure(key) if loader else None

    def __repr__(self) -> str:
        """String representation for debugging"""
        active = self.get_active_loader()
        total = len(self)
        return (
            f"SecureLoaderManager(active={active is not None}, total_loaders={total})"
        )
