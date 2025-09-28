# svg_icon.py
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QIcon
from PyQt5.QtCore import QByteArray, Qt

import re

class SvgIconProvider:
    """
    动态 SVG 图标着色工具
    支持替换 fill/stroke 颜色，返回 QIcon
    """

    @staticmethod
    def get_icon(icon_path: str, color, size=24) -> QIcon:
        if isinstance(color, str):
            color = QColor(color)
        elif isinstance(color, (tuple, list)):
            color = QColor(*color)
        if not color.isValid():
            raise ValueError(f"Invalid color: {color}")

        try:
            with open(icon_path, 'r', encoding='utf-8') as f:
                svg_data = f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read SVG file {icon_path}: {e}")

        # 移除根节点 fill/stroke
        svg_data = re.sub(r'(<svg[^>]*?)(fill|stroke)="[^"]*"', r'\1', svg_data)

        # 替换所有 fill/stroke
        svg_data = re.sub(r'fill="[^"]*"', f'fill="{color.name()}"', svg_data)
        svg_data = re.sub(r"fill='[^']*'", f"fill='{color.name()}'", svg_data)
        svg_data = re.sub(r'stroke="[^"]*"', f'stroke="{color.name()}"', svg_data)

        # 强制替换 currentColor
        svg_data = svg_data.replace('fill="currentColor"', f'fill="{color.name()}"')
        svg_data = svg_data.replace("fill='currentColor'", f"fill='{color.name()}'")

        # 补充无 fill 的路径
        svg_data = re.sub(r'(<path[^>]*?)>', r'\1 fill="{}">'.format(color.name()), svg_data)

        # 移除注释
        svg_data = re.sub(r'<!--.*?-->', '', svg_data, flags=re.DOTALL)

        # 渲染
        renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    @staticmethod
    def black_icon(icon_path: str, size=24) -> QIcon:
        """返回黑色图标（默认颜色）"""
        return SvgIconProvider.get_icon(icon_path, "#2C3E50", size)

    @staticmethod
    def white_icon(icon_path: str, size=24) -> QIcon:
        """返回白色图标"""
        return SvgIconProvider.get_icon(icon_path, "white", size)

    @staticmethod
    def colored_icon(icon_path: str, r, g, b, size=24) -> QIcon:
        """返回 RGB 颜色图标"""
        return SvgIconProvider.get_icon(icon_path, QColor(r, g, b), size)