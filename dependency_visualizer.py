#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей для менеджера пакетов Alpine Linux.
Вариант №14
"""

import argparse
import sys
import gzip
import io
import re
from typing import Optional, List, Dict, Set
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


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
        self.package_cache: Dict[str, List[str]] = {}  # Кеш зависимостей пакетов
    
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
    
    def _fetch_apkindex(self) -> str:
        """
        Загрузка и распаковка APKINDEX из репозитория Alpine Linux.
        
        Returns:
            Содержимое APKINDEX в виде строки
            
        Raises:
            Exception: При ошибке загрузки или распаковки
        """
        apkindex_url = f"{self.repo_url}/APKINDEX.tar.gz"
        
        try:
            # Создание запроса с User-Agent
            request = Request(apkindex_url, headers={'User-Agent': 'DependencyVisualizer/1.0'})
            
            # Загрузка файла
            with urlopen(request, timeout=30) as response:
                tar_gz_data = response.read()
            
            # Распаковка gzip
            with gzip.GzipFile(fileobj=io.BytesIO(tar_gz_data)) as gz:
                tar_data = gz.read()
            
            # В tar-архиве APKINDEX обычно находится как первый файл
            # Пропускаем заголовок tar (512 байт) и читаем содержимое
            # Простой парсинг tar без использования tarfile
            apkindex_content = self._extract_apkindex_from_tar(tar_data)
            
            return apkindex_content.decode('utf-8')
            
        except (URLError, HTTPError) as e:
            raise Exception(f"Ошибка загрузки APKINDEX: {e}")
        except Exception as e:
            raise Exception(f"Ошибка обработки APKINDEX: {e}")
    
    def _extract_apkindex_from_tar(self, tar_data: bytes) -> bytes:
        """
        Простой парсер tar-архива для извлечения содержимого APKINDEX.
        
        Args:
            tar_data: Данные tar-архива
            
        Returns:
            Содержимое файла APKINDEX
        """
        offset = 0
        
        while offset < len(tar_data):
            # Чтение заголовка (512 байт)
            header = tar_data[offset:offset + 512]
            
            if len(header) < 512 or header[0:1] == b'\x00':
                break
            
            # Имя файла находится в первых 100 байтах
            filename = header[0:100].split(b'\x00')[0].decode('utf-8', errors='ignore')
            
            # Размер файла находится в байтах 124-135 (в восьмеричном формате)
            size_str = header[124:136].split(b'\x00')[0].decode('utf-8', errors='ignore').strip()
            try:
                file_size = int(size_str, 8) if size_str else 0
            except ValueError:
                file_size = 0
            
            offset += 512  # Пропускаем заголовок
            
            # Если это файл APKINDEX, возвращаем его содержимое
            if 'APKINDEX' in filename:
                return tar_data[offset:offset + file_size]
            
            # Переходим к следующему файлу (размер выравнивается по 512 байт)
            offset += ((file_size + 511) // 512) * 512
        
        raise Exception("APKINDEX не найден в архиве")
    
    def _parse_apkindex(self, apkindex_content: str) -> Dict[str, List[str]]:
        """
        Парсинг содержимого APKINDEX для получения зависимостей пакетов.
        
        Args:
            apkindex_content: Содержимое APKINDEX
            
        Returns:
            Словарь {имя_пакета: [список_зависимостей]}
        """
        packages = {}
        current_package = None
        current_deps = []
        
        for line in apkindex_content.split('\n'):
            line = line.strip()
            
            if line.startswith('P:'):
                # Новый пакет
                if current_package:
                    packages[current_package] = current_deps
                current_package = line[2:].strip()
                current_deps = []
            
            elif line.startswith('D:'):
                # Зависимости пакета
                deps_line = line[2:].strip()
                if deps_line:
                    # Разделяем зависимости по пробелам
                    for dep in deps_line.split():
                        # Удаляем версионные требования (например, >=1.0, <2.0)
                        dep_name = re.split(r'[<>=!]', dep)[0].strip()
                        if dep_name and dep_name not in current_deps:
                            current_deps.append(dep_name)
        
        # Добавляем последний пакет
        if current_package:
            packages[current_package] = current_deps
        
        return packages
    
    def get_direct_dependencies(self, package_name: str) -> List[str]:
        """
        Получение прямых зависимостей пакета.
        
        Args:
            package_name: Имя пакета
            
        Returns:
            Список имен прямых зависимостей
        """
        # Проверяем кеш
        if package_name in self.package_cache:
            return self.package_cache[package_name]
        
        # Если кеш пуст, загружаем APKINDEX
        if not self.package_cache:
            print(f"Загрузка APKINDEX из {self.repo_url}...")
            apkindex_content = self._fetch_apkindex()
            self.package_cache = self._parse_apkindex(apkindex_content)
            print(f"Загружено информации о {len(self.package_cache)} пакетах")
        
        # Возвращаем зависимости пакета
        return self.package_cache.get(package_name, [])


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
        
        # Вывод конфигурации
        visualizer.print_config()
        
        # Этап 2: Получение и вывод прямых зависимостей
        print("\n" + "=" * 60)
        print(f"ПРЯМЫЕ ЗАВИСИМОСТИ ПАКЕТА '{args.package}'")
        print("=" * 60)
        
        try:
            dependencies = visualizer.get_direct_dependencies(args.package)
            
            if dependencies:
                print(f"Найдено зависимостей: {len(dependencies)}")
                for i, dep in enumerate(dependencies, 1):
                    print(f"  {i}. {dep}")
            else:
                print(f"Пакет '{args.package}' не имеет зависимостей или не найден в репозитории")
        
        except Exception as e:
            print(f"Ошибка при получении зависимостей: {e}", file=sys.stderr)
            return 3
        
        print("=" * 60)
        
        return 0
        
    except ValueError as e:
        print(f"Ошибка валидации: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
