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
    
    def _load_test_repository(self) -> Dict[str, List[str]]:
        """
        Загрузка тестового репозитория из файла.
        
        Returns:
            Словарь {имя_пакета: [список_зависимостей]}
        """
        packages = {}
        
        try:
            with open(self.repo_url, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Пропускаем комментарии и пустые строки
                    if not line or line.startswith('#'):
                        continue
                    
                    # Парсим формат: PACKAGE: DEP1 DEP2 DEP3
                    if ':' in line:
                        parts = line.split(':', 1)
                        package = parts[0].strip()
                        deps_str = parts[1].strip() if len(parts) > 1 else ''
                        
                        # Разделяем зависимости по пробелам
                        deps = [d.strip() for d in deps_str.split() if d.strip()]
                        packages[package] = deps
        
        except FileNotFoundError:
            raise Exception(f"Файл тестового репозитория не найден: {self.repo_url}")
        except Exception as e:
            raise Exception(f"Ошибка чтения тестового репозитория: {e}")
        
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
        
        # Если кеш пуст, загружаем данные
        if not self.package_cache:
            if self.test_mode:
                print(f"Загрузка тестового репозитория из {self.repo_url}...")
                self.package_cache = self._load_test_repository()
            else:
                print(f"Загрузка APKINDEX из {self.repo_url}...")
                apkindex_content = self._fetch_apkindex()
                self.package_cache = self._parse_apkindex(apkindex_content)
            
            print(f"Загружено информации о {len(self.package_cache)} пакетах")
        
        # Возвращаем зависимости пакета
        return self.package_cache.get(package_name, [])
    
    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """
        Построение полного графа зависимостей с использованием DFS без рекурсии.
        Учитывает максимальную глубину, фильтрацию и циклические зависимости.
        
        Returns:
            Словарь {пакет: множество_зависимостей}
        """
        graph = {}
        visited = set()  # Посещенные пакеты (для обнаружения циклов)
        
        # Стек для DFS: (пакет, глубина)
        stack = [(self.package_name, 0)]
        
        # Дополнительный набор для отслеживания пакетов в текущем пути (обнаружение циклов)
        path_set = set()
        
        print(f"\nПостроение графа зависимостей для пакета '{self.package_name}'...")
        print(f"Максимальная глубина: {self.max_depth}")
        if self.filter_substring:
            print(f"Фильтрация пакетов с подстрокой: '{self.filter_substring}'")
        
        while stack:
            package, depth = stack.pop()
            
            # Проверяем максимальную глубину
            if depth > self.max_depth:
                continue
            
            # Проверяем фильтр
            if self.filter_substring and self.filter_substring in package:
                print(f"  Пропуск пакета '{package}' (содержит подстроку '{self.filter_substring}')")
                continue
            
            # Проверяем, не посещали ли мы уже этот пакет
            if package in visited:
                # Если пакет в текущем пути - цикл
                if package in path_set:
                    print(f"  Обнаружен цикл: пакет '{package}' уже в пути обхода")
                continue
            
            visited.add(package)
            path_set.add(package)
            
            # Получаем прямые зависимости
            try:
                dependencies = self.get_direct_dependencies(package)
            except Exception as e:
                print(f"  Ошибка получения зависимостей для '{package}': {e}")
                dependencies = []
            
            # Добавляем в граф
            if package not in graph:
                graph[package] = set()
            
            # Добавляем зависимости в граф и стек для обхода
            for dep in dependencies:
                # Проверяем фильтр для зависимости
                if self.filter_substring and self.filter_substring in dep:
                    continue
                
                graph[package].add(dep)
                
                # Добавляем в стек только если еще не посещали
                if dep not in visited:
                    stack.append((dep, depth + 1))
            
            # Убираем из текущего пути при возврате
            # (в реальности это происходит автоматически из-за обхода в ширину стека)
        
        print(f"Построен граф с {len(graph)} узлами")
        
        # Вывод статистики циклов
        cycles_detected = False
        for package in graph:
            if package in graph[package]:
                print(f"  Самозависимость: {package} -> {package}")
                cycles_detected = True
        
        if cycles_detected:
            print("  Обнаружены циклические зависимости")
        
        return graph
    
    def find_reverse_dependencies(self, target_package: str) -> Set[str]:
        """
        Поиск обратных зависимостей для заданного пакета.
        Обратные зависимости - это пакеты, которые зависят от данного пакета.
        
        Args:
            target_package: Пакет, для которого ищем обратные зависимости
            
        Returns:
            Множество пакетов, которые зависят от target_package
        """
        reverse_deps = set()
        
        # Загружаем все пакеты, если еще не загружены
        if not self.package_cache:
            if self.test_mode:
                print(f"Загрузка тестового репозитория из {self.repo_url}...")
                self.package_cache = self._load_test_repository()
            else:
                print(f"Загрузка APKINDEX из {self.repo_url}...")
                apkindex_content = self._fetch_apkindex()
                self.package_cache = self._parse_apkindex(apkindex_content)
            
            print(f"Загружено информации о {len(self.package_cache)} пакетах")
        
        print(f"\nПоиск обратных зависимостей для пакета '{target_package}'...")
        
        # Обходим все пакеты и проверяем, зависят ли они от целевого
        # Используем DFS без рекурсии для каждого пакета
        for package in self.package_cache:
            # Пропускаем сам целевой пакет
            if package == target_package:
                continue
            
            # Проверяем фильтр
            if self.filter_substring and self.filter_substring in package:
                continue
            
            # Ищем target_package в зависимостях этого пакета (с учетом транзитивности)
            visited = set()
            stack = [(package, 0)]
            found = False
            
            while stack and not found:
                current, depth = stack.pop()
                
                # Проверяем максимальную глубину
                if depth > self.max_depth:
                    continue
                
                if current in visited:
                    continue
                
                visited.add(current)
                
                # Получаем зависимости
                deps = self.package_cache.get(current, [])
                
                for dep in deps:
                    # Проверяем фильтр
                    if self.filter_substring and self.filter_substring in dep:
                        continue
                    
                    # Если нашли целевой пакет - добавляем исходный пакет в результат
                    if dep == target_package:
                        reverse_deps.add(package)
                        found = True
                        break
                    
                    # Добавляем в стек для дальнейшего поиска
                    if dep not in visited:
                        stack.append((dep, depth + 1))
        
        print(f"Найдено {len(reverse_deps)} пакетов, зависящих от '{target_package}'")
        
        return reverse_deps
    
    def generate_mermaid(self, graph: Dict[str, Set[str]]) -> str:
        """
        Генерация текстового представления графа в формате Mermaid.
        
        Args:
            graph: Граф зависимостей {пакет: множество_зависимостей}
            
        Returns:
            Строка с кодом Mermaid
        """
        lines = ["graph TD"]
        
        # Добавляем узлы и рёбра
        for package in sorted(graph.keys()):
            # Экранируем специальные символы для Mermaid
            safe_package = package.replace("-", "_").replace(".", "_").replace(":", "_")
            
            # Добавляем узел с меткой
            lines.append(f'    {safe_package}["{package}"]')
            
            # Добавляем рёбра к зависимостям
            for dep in sorted(graph[package]):
                safe_dep = dep.replace("-", "_").replace(".", "_").replace(":", "_")
                lines.append(f'    {safe_package} --> {safe_dep}')
        
        # Если граф пустой, добавляем заглушку
        if len(graph) == 0:
            lines.append('    Empty["Граф пуст"]')
        elif len(graph) == 1 and not any(graph.values()):
            # Если один узел без зависимостей
            package = list(graph.keys())[0]
            safe_package = package.replace("-", "_").replace(".", "_").replace(":", "_")
            lines.append(f'    {safe_package}["{package}"]')
        
        return '\n'.join(lines)
    
    def save_mermaid_to_svg(self, mermaid_code: str) -> str:
        """
        Сохранение графа Mermaid в файл SVG.
        Использует Mermaid CLI (mmdc) если доступен, иначе создает SVG с кодом Mermaid.
        
        Args:
            mermaid_code: Код графа в формате Mermaid
            
        Returns:
            Путь к сохраненному файлу
        """
        import subprocess
        import tempfile
        import os
        
        # Сначала сохраняем Mermaid код в текстовый файл
        mermaid_file = self.output_file.replace('.svg', '.mmd')
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(mermaid_code)
        
        print(f"Mermaid код сохранен в: {mermaid_file}")
        
        # Проверяем, доступен ли mmdc (Mermaid CLI)
        try:
            result = subprocess.run(['mmdc', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            mmdc_available = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            mmdc_available = False
        
        if mmdc_available:
            # Используем mmdc для конвертации
            try:
                print(f"Генерация SVG с помощью Mermaid CLI...")
                result = subprocess.run(
                    ['mmdc', '-i', mermaid_file, '-o', self.output_file, '-t', 'neutral'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"SVG успешно сохранен в: {self.output_file}")
                    return self.output_file
                else:
                    print(f"Ошибка mmdc: {result.stderr}")
                    print("Создание простого SVG с текстом Mermaid...")
            except subprocess.TimeoutExpired:
                print("Таймаут при выполнении mmdc")
                print("Создание простого SVG с текстом Mermaid...")
        else:
            print("Mermaid CLI (mmdc) не найден.")
            print("Установите: npm install -g @mermaid-js/mermaid-cli")
            print("Создание простого SVG с текстом Mermaid...")
        
        # Создаем простой SVG с кодом Mermaid и инструкцией
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
  <rect width="800" height="600" fill="#f9f9f9"/>
  <text x="400" y="50" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#333">
    Граф зависимостей: {self.package_name}
  </text>
  <text x="400" y="80" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#666">
    Для визуализации используйте файл {mermaid_file}
  </text>
  <text x="400" y="110" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#999">
    Просмотр: https://mermaid.live или установите mmdc
  </text>
  <rect x="50" y="130" width="700" height="430" fill="white" stroke="#ccc" stroke-width="2" rx="5"/>
  <text x="60" y="160" font-family="Courier New, monospace" font-size="11" fill="#333">
    <tspan x="60" dy="0">{mermaid_code.split(chr(10))[0]}</tspan>
'''
        
        # Добавляем строки кода Mermaid (ограничиваем количество)
        lines = mermaid_code.split('\n')
        y_offset = 175
        for i, line in enumerate(lines[1:35]):  # Первые 34 строки после заголовка
            svg_content += f'    <tspan x="60" dy="15">{line[:80]}</tspan>\n'
            y_offset += 15
        
        if len(lines) > 35:
            svg_content += f'    <tspan x="60" dy="20">... ({len(lines) - 35} строк скрыто) ...</tspan>\n'
        
        svg_content += '''  </text>
</svg>'''
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"SVG с предварительным просмотром сохранен в: {self.output_file}")
        return self.output_file


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
    
    parser.add_argument(
        '--reverse-deps',
        action='store_true',
        default=False,
        help='Режим вывода обратных зависимостей (пакеты, которые зависят от данного пакета)'
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
        
        # Этап 3: Построение графа зависимостей
        print("\n" + "=" * 60)
        print("ГРАФ ЗАВИСИМОСТЕЙ (транзитивный)")
        print("=" * 60)
        
        try:
            graph = visualizer.build_dependency_graph()
            
            if graph:
                print(f"\nГраф содержит {len(graph)} пакетов:")
                for package in sorted(graph.keys()):
                    deps = sorted(graph[package])
                    if deps:
                        print(f"\n  {package}:")
                        for dep in deps:
                            print(f"    -> {dep}")
                    else:
                        print(f"\n  {package}: (нет зависимостей)")
            else:
                print("Граф пуст")
        
        except Exception as e:
            print(f"Ошибка при построении графа: {e}", file=sys.stderr)
            return 4
        
        print("\n" + "=" * 60)
        
        # Этап 4: Обратные зависимости (если включен режим)
        if args.reverse_deps:
            print("\n" + "=" * 60)
            print(f"ОБРАТНЫЕ ЗАВИСИМОСТИ ДЛЯ ПАКЕТА '{args.package}'")
            print("=" * 60)
            
            try:
                reverse_deps = visualizer.find_reverse_dependencies(args.package)
                
                if reverse_deps:
                    print(f"\nПакеты, зависящие от '{args.package}':")
                    for i, pkg in enumerate(sorted(reverse_deps), 1):
                        print(f"  {i}. {pkg}")
                else:
                    print(f"\nНет пакетов, зависящих от '{args.package}'")
            
            except Exception as e:
                print(f"Ошибка при поиске обратных зависимостей: {e}", file=sys.stderr)
                return 5
            
            print("\n" + "=" * 60)
        
        # Этап 5: Визуализация
        print("\n" + "=" * 60)
        print("ВИЗУАЛИЗАЦИЯ ГРАФА")
        print("=" * 60)
        
        try:
            # Генерируем Mermaid код
            mermaid_code = visualizer.generate_mermaid(graph)
            print("\nГенерация Mermaid кода...")
            print(f"Размер графа: {len(mermaid_code.split(chr(10)))} строк\n")
            
            # Сохраняем в SVG
            output_path = visualizer.save_mermaid_to_svg(mermaid_code)
            print(f"\n✓ Визуализация завершена")
            print(f"  Mermaid: {output_path.replace('.svg', '.mmd')}")
            print(f"  SVG: {output_path}")
        
        except Exception as e:
            print(f"Ошибка при визуализации: {e}", file=sys.stderr)
            return 6
        
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
