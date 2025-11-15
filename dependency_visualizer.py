#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей для менеджера пакетов Alpine Linux.
Вариант №14
"""

import argparse
import sys
from typing import Optional


class DependencyVisualizer:
    """Основной класс для визуализации графа зависимостей пакетов."""
    
    def __init__(self, package_name: str, repo_url: str, test_mode: bool,
                 output_file: str, max_depth: int, filter_substring: Optional[str] = None):
        """
        Инициализация визуализатора зависимостей.
        
        Args:
            package_name: Имя анализируемого пакета
            repo_url: URL-адрес репозитория или путь к тестовому файлу
            test_mode: Режим работы с тестовым репозиторием
            output_file: Имя файла для сохранения графа
            max_depth: Максимальная глубина анализа зависимостей
            filter_substring: Подстрока для фильтрации пакетов
        """
        self.package_name = package_name
        self.repo_url = repo_url
        self.test_mode = test_mode
        self.output_file = output_file
        self.max_depth = max_depth
        self.filter_substring = filter_substring
    
    def print_config(self):
        """Вывод всех настроенных параметров."""
        print("=" * 60)
        print("КОНФИГУРАЦИЯ ВИЗУАЛИЗАТОРА ЗАВИСИМОСТЕЙ")
        print("=" * 60)
        print(f"Имя пакета: {self.package_name}")
        print(f"URL репозитория/путь к файлу: {self.repo_url}")
        print(f"Режим тестирования: {self.test_mode}")
        print(f"Выходной файл: {self.output_file}")
        print(f"Максимальная глубина анализа: {self.max_depth}")
        print(f"Подстрока для фильтрации: {self.filter_substring if self.filter_substring else 'не задана'}")
        print("=" * 60)


def validate_arguments(args):
    """
    Валидация аргументов командной строки.
    
    Args:
        args: Распарсенные аргументы
        
    Raises:
        ValueError: При некорректных значениях параметров
    """
    # Проверка имени пакета
    if not args.package:
        raise ValueError("Имя пакета не может быть пустым")
    
    if not args.package.strip():
        raise ValueError("Имя пакета содержит только пробелы")
    
    # Проверка URL репозитория
    if not args.repo_url:
        raise ValueError("URL репозитория или путь к файлу не может быть пустым")
    
    if not args.repo_url.strip():
        raise ValueError("URL репозитория содержит только пробелы")
    
    # Проверка имени выходного файла
    if not args.output:
        raise ValueError("Имя выходного файла не может быть пустым")
    
    if not args.output.strip():
        raise ValueError("Имя выходного файла содержит только пробелы")
    
    # Проверка расширения файла
    if not args.output.lower().endswith('.svg'):
        raise ValueError("Выходной файл должен иметь расширение .svg")
    
    # Проверка максимальной глубины
    if args.max_depth <= 0:
        raise ValueError(f"Максимальная глубина должна быть положительным числом (указано: {args.max_depth})")
    
    if args.max_depth > 100:
        raise ValueError(f"Максимальная глубина слишком велика (указано: {args.max_depth}, максимум: 100)")
    
    # Проверка подстроки фильтрации (опциональный параметр)
    if args.filter and not args.filter.strip():
        raise ValueError("Подстрока для фильтрации содержит только пробелы")


def parse_arguments():
    """
    Парсинг аргументов командной строки.
    
    Returns:
        Распарсенные аргументы командной строки
    """
    parser = argparse.ArgumentParser(
        description='Инструмент визуализации графа зависимостей для менеджера пакетов Alpine Linux',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s --package busybox --repo-url https://dl-cdn.alpinelinux.org/alpine/v3.18/main/x86_64 --output graph.svg
  %(prog)s --package A --repo-url test_repo.txt --test-mode --output test_graph.svg --max-depth 3
  %(prog)s --package musl --repo-url https://dl-cdn.alpinelinux.org/alpine/v3.18/main/x86_64 --output musl.svg --filter dev
        """
    )
    
    parser.add_argument(
        '--package',
        type=str,
        required=True,
        help='Имя анализируемого пакета'
    )
    
    parser.add_argument(
        '--repo-url',
        type=str,
        required=True,
        help='URL-адрес репозитория Alpine Linux или путь к файлу тестового репозитория'
    )
    
    parser.add_argument(
        '--test-mode',
        action='store_true',
        default=False,
        help='Режим работы с тестовым репозиторием (пакеты названы большими латинскими буквами)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='dependency_graph.svg',
        help='Имя сгенерированного файла с изображением графа (по умолчанию: dependency_graph.svg)'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=10,
        help='Максимальная глубина анализа зависимостей (по умолчанию: 10)'
    )
    
    parser.add_argument(
        '--filter',
        type=str,
        default=None,
        help='Подстрока для фильтрации пакетов (пакеты, содержащие эту подстроку, будут исключены из анализа)'
    )
    
    return parser.parse_args()


def main():
    """Главная функция приложения."""
    try:
        # Парсинг аргументов командной строки
        args = parse_arguments()
        
        # Валидация аргументов
        validate_arguments(args)
        
        # Создание визуализатора
        visualizer = DependencyVisualizer(
            package_name=args.package,
            repo_url=args.repo_url,
            test_mode=args.test_mode,
            output_file=args.output,
            max_depth=args.max_depth,
            filter_substring=args.filter
        )
        
        # Вывод конфигурации (только для этапа 1)
        visualizer.print_config()
        
        return 0
        
    except ValueError as e:
        print(f"Ошибка валидации: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
