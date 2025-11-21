#!/usr/bin/env python3
"""
Генератор иконок для курса "Мастерство архитектуры и паттернов проектирования"

Этот скрипт создает favicon файлы разных размеров из SVG иконки.
Требует: Pillow, cairosvg (или можно использовать онлайн конвертеры)
"""

from pathlib import Path
from PIL import Image, ImageDraw
from typing import Optional, Any
import sys

# Цвета темы курса
COLORS = {
    "primary": "#1e40af",  # Синий (архитектура)
    "secondary": "#3b82f6",  # Светло-синий
    "accent": "#fbbf24",  # Желтый (паттерны)
    "success": "#10b981",  # Зеленый
    "danger": "#ef4444",  # Красный
    "purple": "#8b5cf6",  # Фиолетовый (SOLID)
    "pink": "#ec4899",  # Розовый (микросервисы)
    "white": "#ffffff",
}


def create_favicon(size: int, output_path: Path):
    """Создает favicon заданного размера"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Фон с закругленными углами
    corner_radius = size // 8
    draw.rounded_rectangle(
        [(0, 0), (size, size)], radius=corner_radius, fill=COLORS["primary"]
    )

    # Масштабирование элементов
    scale = size / 256

    # Основной блок (архитектура)
    block_x = int(64 * scale)
    block_y = int(80 * scale)
    block_w = int(128 * scale)
    block_h = int(96 * scale)

    # Основной прямоугольник
    draw.rounded_rectangle(
        [
            (block_x, block_y + int(40 * scale)),
            (block_x + block_w, block_y + int(40 * scale) + block_h),
        ],
        radius=int(4 * scale),
        fill=COLORS["secondary"],
    )

    # Внутренние слои
    layer_margin = int(8 * scale)
    draw.rounded_rectangle(
        [
            (block_x + layer_margin, block_y + int(48 * scale)),
            (
                block_x + block_w - layer_margin,
                block_y + int(48 * scale) + int(80 * scale),
            ),
        ],
        radius=int(2 * scale),
        fill=COLORS["secondary"],
        outline=None,
    )

    # SOLID принципы (5 точек)
    solid_x = block_x + int(140 * scale)
    solid_y = block_y + int(20 * scale)
    dot_size = int(4 * scale)
    dot_positions = [(0, 0), (12, 0), (24, 0), (6, 8), (18, 8)]
    for dx, dy in dot_positions:
        x = solid_x + int(dx * scale)
        y = solid_y + int(dy * scale)
        draw.ellipse(
            [(x - dot_size, y - dot_size), (x + dot_size, y + dot_size)],
            fill=COLORS["purple"],
        )

    # Паттерны (круг, квадрат, треугольник)
    # Singleton (круг)
    circle_x = block_x + int(32 * scale)
    circle_y = block_y + int(32 * scale)
    circle_r = int(12 * scale)
    draw.ellipse(
        [
            (circle_x - circle_r, circle_y - circle_r),
            (circle_x + circle_r, circle_y + circle_r),
        ],
        fill=COLORS["accent"],
        outline=COLORS["accent"],
        width=int(2 * scale),
    )
    draw.ellipse(
        [
            (circle_x - int(6 * scale), circle_y - int(6 * scale)),
            (circle_x + int(6 * scale), circle_y + int(6 * scale)),
        ],
        fill=COLORS["white"],
    )

    # Factory (квадрат)
    square_x = block_x + int(64 * scale)
    square_y = block_y + int(20 * scale)
    square_size = int(24 * scale)
    draw.rounded_rectangle(
        [(square_x, square_y), (square_x + square_size, square_y + square_size)],
        radius=int(2 * scale),
        fill=COLORS["success"],
        outline=COLORS["success"],
        width=int(2 * scale),
    )

    # Микросервисы (маленькие блоки)
    micro_y = block_y + int(152 * scale)
    micro_h = int(16 * scale)
    for i, micro_x in enumerate(
        [block_x + int(8 * scale), block_x + int(48 * scale), block_x + int(88 * scale)]
    ):
        micro_w = int(32 * scale)
        draw.rounded_rectangle(
            [(micro_x, micro_y), (micro_x + micro_w, micro_y + micro_h)],
            radius=int(2 * scale),
            fill=COLORS["pink"],
        )

    # Буква "A" для Architecture
    if size >= 32:
        font_size = max(12, int(size * 0.2))
        font: Optional[Any] = None
        try:
            from PIL import ImageFont

            # Попробуем использовать системный шрифт
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except OSError:
                font = ImageFont.load_default()
        except (ImportError, ModuleNotFoundError):
            font = None

        text = "A"
        text_x = size // 2
        text_y = int(block_y + int(200 * scale))

        # Получаем размер текста
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width = font_size
            text_height = font_size

        draw.text(
            (text_x - text_width // 2, text_y - text_height // 2),
            text,
            fill=COLORS["white"],
            font=font,
        )

    # Сохраняем
    img.save(output_path, format="PNG", optimize=True)
    print(f"Created {output_path.name} ({size}x{size})")


def main():
    """Генерирует все размеры favicon"""
    import sys
    import io

    # Устанавливаем UTF-8 для вывода
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )

    assets_dir = Path(__file__).parent

    sizes = [16, 32, 48, 64, 128, 256]

    print("Generating favicon files...")
    print(f"Directory: {assets_dir}")

    for size in sizes:
        filename = f"favicon-{size}x{size}.png"

        output_path = assets_dir / filename
        create_favicon(size, output_path)

    print("\nAll favicon files created!")
    print("\nFor .ico file creation use online converter:")
    print("   https://convertio.co/png-ico/")
    print("   or install: uv add pillow")


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nInstall dependencies:")
        print("   uv add pillow")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
