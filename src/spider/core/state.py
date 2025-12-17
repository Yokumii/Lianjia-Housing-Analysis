import json
import os
import shutil
import tempfile
from typing import Dict, List, Tuple


class StateManager:
    """
    进度状态管理器

    状态文件格式：
    {
        "bj|dongcheng": 1,
        "bj|xicheng": 3,
        "bj|chaoyang": -1,  # -1 表示完成
        ...
    }
    """

    def __init__(self, state_file: str):
        """
        初始化状态管理器

        Args:
            state_file: 进度文件路径
        """
        self.state_file = state_file
        self.state_data = self._load()

    def _load(self) -> Dict[str, int]:
        """加载进度文件"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[警告] 无法加载进度文件 {self.state_file}: {e}")
                return {}
        else:
            return {}

    def init_tasks(self, task_keys: Dict[str, int], csv_filename: str = None):
        """
        初始化任务列表

        Args:
            task_keys: {task_key: initial_page} 格式
                      例：{'bj|dongcheng': 1, 'bj|xicheng': 1, ...}
            csv_filename: 输出 CSV 文件名（保存但不使用）
        """
        # 为新发现的任务添加到状态中
        for key in task_keys:
            if key not in self.state_data:
                self.state_data[key] = task_keys[key]

        self.save()

    def get_pending_tasks(self) -> List[Tuple[str, int]]:
        """
        获取待处理的任务

        Returns:
            List[Tuple[str, int]]: [(task_key, page_num), ...]
        """
        return [(key, page) for key, page in self.state_data.items() if page != -1]

    def update_page(self, task_key: str, next_page: int):
        """
        更新任务的页码（继续爬取下一页）

        Args:
            task_key: city|district 格式的任务键
            next_page: 下一页的页码
        """
        self.state_data[task_key] = next_page
        self.save()

    def mark_done(self, task_key: str):
        """
        标记任务完成（已爬取所有页面）

        Args:
            task_key: city|district 格式的任务键
        """
        self.state_data[task_key] = -1
        self.save()

    def get_progress(self) -> Dict:
        """获取进度信息"""
        total = len(self.state_data)
        completed = len([p for p in self.state_data.values() if p == -1])
        pending = total - completed

        progress_pct = (completed / total * 100) if total > 0 else 0

        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'progress_pct': round(progress_pct, 2),
        }

    def is_complete(self) -> bool:
        """检查所有任务是否已完成"""
        return all(page == -1 for page in self.state_data.values())

    def save(self):
        """
        原子写操作保存状态到文件（防止数据损坏）
        """
        try:
            # 先写入临时文件
            fd, tmp_path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(self.state_data, f, indent=0, ensure_ascii=False)
            # 再移动替换
            shutil.move(tmp_path, self.state_file)
        except Exception as e:
            print(f"[错误] 保存进度文件失败: {e}")

    def cleanup(self):
        """清理进度文件（任务全部完成时调用）"""
        if os.path.exists(self.state_file):
            try:
                os.remove(self.state_file)
                print(f"✓ 已清理进度文件: {self.state_file}")
            except Exception as e:
                print(f"[警告] 清理进度文件失败: {e}")

    def __repr__(self) -> str:
        progress = self.get_progress()
        return (
            f"StateManager(completed={progress['completed']}/{progress['total']}, "
            f"pending={progress['pending']})"
        )
