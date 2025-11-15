# Визуализатор графа зависимостей для Alpine Linux (apk)

Инструмент визуализации графа зависимостей для менеджера пакетов Alpine Linux. Вариант №14.

## Описание

Данный инструмент позволяет анализировать и визуализировать граф зависимостей пакетов Alpine Linux (apk) без использования готовых менеджеров пакетов или библиотек для получения информации о зависимостях.

## Возможности

- Анализ прямых и транзитивных зависимостей пакетов
- Построение графа зависимостей с помощью алгоритма DFS без рекурсии
- Поддержка максимальной глубины анализа
- Фильтрация пакетов по подстроке
- Обработка циклических зависимостей
- Режим тестирования с локальными файлами
- Визуализация графа в формате Mermaid и экспорт в SVG
- Анализ обратных зависимостей

## Установка

```bash
# Клонирование репозитория
git clone <repository-url>
cd config-valia

# Создание виртуального окружения (опционально)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Установка зависимостей (если будут добавлены позже)
# pip install -r requirements.txt
```

## Использование

### Быстрый старт (Shell-скрипты)

Для быстрой демонстрации всех этапов используйте готовые shell-скрипты:

```bash
# Запуск всех этапов последовательно
chmod +x run_all_stages.sh
./run_all_stages.sh

# Или запуск отдельного этапа
chmod +x run_stage1.sh
./run_stage1.sh
```

Подробнее см. [SCRIPTS_README.md](SCRIPTS_README.md)

### Базовое использование

```bash
python dependency_visualizer.py --package <имя_пакета> --repo-url <URL_репозитория> --output <имя_файла.svg>
```

### Примеры

#### Анализ пакета busybox
```bash
python dependency_visualizer.py --package busybox --repo-url https://dl-cdn.alpinelinux.org/alpine/v3.18/main/x86_64 --output busybox_deps.svg
```

#### Использование тестового режима
```bash
python dependency_visualizer.py --package A --repo-url test_repo.txt --test-mode --output test_graph.svg --max-depth 3
```

#### Фильтрация пакетов
```bash
python dependency_visualizer.py --package musl --repo-url https://dl-cdn.alpinelinux.org/alpine/v3.18/main/x86_64 --output musl.svg --filter dev
```

### Параметры командной строки

- `--package` (обязательный): Имя анализируемого пакета
- `--repo-url` (обязательный): URL-адрес репозитория Alpine Linux или путь к файлу тестового репозитория
- `--test-mode`: Включить режим работы с тестовым репозиторием (пакеты названы большими латинскими буквами)
- `--output`: Имя файла для сохранения графа (по умолчанию: dependency_graph.svg)
- `--max-depth`: Максимальная глубина анализа зависимостей (по умолчанию: 10)
- `--filter`: Подстрока для фильтрации пакетов (пакеты, содержащие эту подстроку, будут исключены)
- `--reverse-deps`: Включить режим вывода обратных зависимостей

## Примеры визуализации

Подробные примеры визуализации и сравнение со штатными инструментами Alpine Linux см. в [VISUALIZATION_EXAMPLES.md](VISUALIZATION_EXAMPLES.md)

### Пример 1: Простой граф
```bash
python dependency_visualizer.py --package A --repo-url test_repo.txt --test-mode --output graph_A.svg --max-depth 3
```

### Пример 2: Граф с циклическими зависимостями
```bash
python dependency_visualizer.py --package L --repo-url test_repo.txt --test-mode --output graph_L.svg --max-depth 5
```

### Пример 3: Обратные зависимости
```bash
python dependency_visualizer.py --package G --repo-url test_repo.txt --test-mode --output test.svg --reverse-deps
```

## Этапы разработки

- [x] **Этап 1**: Минимальный прототип с конфигурацией ✅
- [x] **Этап 2**: Сбор данных о зависимостях ✅
- [x] **Этап 3**: Построение графа зависимостей (DFS без рекурсии) ✅
- [x] **Этап 4**: Анализ обратных зависимостей ✅
- [x] **Этап 5**: Визуализация в Mermaid и экспорт в SVG ✅

**Все этапы успешно завершены!**

## Требования

- Python 3.7+
- Стандартная библиотека Python (не требуются сторонние пакеты для этапа 1)

## Лицензия

MIT License

## Автор

Разработано в рамках выполнения задания по конфигурационному управлению.
