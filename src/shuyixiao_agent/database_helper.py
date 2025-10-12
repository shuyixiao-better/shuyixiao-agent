"""
数据库辅助工具

自动处理 ChromaDB 数据库权限问题和持久化
"""

import os
import stat
from pathlib import Path


class DatabaseHelper:
    """数据库辅助类，用于管理数据库权限和持久化"""
    
    @staticmethod
    def ensure_database_directory(db_path: str) -> bool:
        """
        确保数据库目录存在且权限正确
        
        Args:
            db_path: 数据库路径
            
        Returns:
            是否成功
        """
        try:
            db_dir = Path(db_path)
            
            # 创建目录
            db_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ 数据库目录已创建: {db_dir}")
            
            # 设置目录权限为 755 (rwxr-xr-x)
            os.chmod(db_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            print(f"  ✓ 数据库目录权限已设置: 755")
            
            return True
        except Exception as e:
            print(f"  ✗ 创建数据库目录失败: {e}")
            return False
    
    @staticmethod
    def fix_database_permissions(db_path: str) -> bool:
        """
        修复数据库文件和目录的权限
        
        Args:
            db_path: 数据库路径
            
        Returns:
            是否成功
        """
        try:
            db_dir = Path(db_path)
            
            if not db_dir.exists():
                print(f"  ⚠️  数据库目录不存在，正在创建...")
                return DatabaseHelper.ensure_database_directory(db_path)
            
            # 修复根目录权限
            os.chmod(db_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            
            fixed_count = 0
            # 递归修复所有子目录和文件的权限
            for root, dirs, files in os.walk(db_dir):
                # 修复目录权限 (755)
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name
                    try:
                        os.chmod(dir_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                        fixed_count += 1
                    except Exception:
                        pass
                
                # 修复文件权限 (644)
                for file_name in files:
                    file_path = Path(root) / file_name
                    try:
                        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
                        fixed_count += 1
                    except Exception:
                        pass
            
            print(f"  ✓ 数据库权限修复完成 (修复了 {fixed_count} 个项目)")
            return True
        except Exception as e:
            print(f"  ✗ 修复数据库权限失败: {e}")
            return False
    
    @staticmethod
    def cleanup_temp_files(db_path: str) -> bool:
        """
        清理数据库临时文件（如 WAL、SHM 等）
        
        Args:
            db_path: 数据库路径
            
        Returns:
            是否成功
        """
        try:
            db_dir = Path(db_path)
            
            if not db_dir.exists():
                return True
            
            temp_patterns = ['*.tmp', '*-shm', '*-wal']
            cleaned_count = 0
            
            for pattern in temp_patterns:
                for temp_file in db_dir.rglob(pattern):
                    try:
                        temp_file.unlink()
                        cleaned_count += 1
                    except Exception:
                        pass
            
            if cleaned_count > 0:
                print(f"  ✓ 已清理 {cleaned_count} 个临时文件")
            
            return True
        except Exception as e:
            print(f"  ✗ 清理临时文件失败: {e}")
            return False
    
    @staticmethod
    def initialize_database(db_path: str, cleanup_temp: bool = True) -> bool:
        """
        初始化数据库（在应用启动时调用）
        
        Args:
            db_path: 数据库路径
            cleanup_temp: 是否清理临时文件
            
        Returns:
            是否成功
        """
        print("🔧 正在初始化数据库...")
        
        # 1. 确保目录存在
        if not DatabaseHelper.ensure_database_directory(db_path):
            return False
        
        # 2. 清理临时文件
        if cleanup_temp:
            DatabaseHelper.cleanup_temp_files(db_path)
        
        # 3. 修复权限
        if not DatabaseHelper.fix_database_permissions(db_path):
            return False
        
        print(f"  ✅ 数据库初始化完成")
        
        return True
    
    @staticmethod
    def check_database_health(db_path: str) -> dict:
        """
        检查数据库健康状态
        
        Args:
            db_path: 数据库路径
            
        Returns:
            健康状态信息
        """
        db_dir = Path(db_path)
        
        health = {
            "exists": db_dir.exists(),
            "readable": False,
            "writable": False,
            "size_mb": 0,
            "file_count": 0
        }
        
        if health["exists"]:
            try:
                health["readable"] = os.access(db_dir, os.R_OK)
                health["writable"] = os.access(db_dir, os.W_OK)
                
                # 计算总大小和文件数
                total_size = 0
                file_count = 0
                for root, dirs, files in os.walk(db_dir):
                    for file in files:
                        file_path = Path(root) / file
                        try:
                            total_size += file_path.stat().st_size
                            file_count += 1
                        except:
                            pass
                
                health["size_mb"] = round(total_size / (1024 * 1024), 2)
                health["file_count"] = file_count
            except Exception:
                pass
        
        return health

