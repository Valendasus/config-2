# 🚀 Быстрый старт

## Запуск демонстрации проекта

### Linux / macOS / WSL

```bash
# 1. Перейдите в директорию проекта
cd config-valia

# 2. Сделайте скрипты исполняемыми
chmod +x run_*.sh

# 3. Запустите полную демонстрацию
./run_all_stages.sh
```

### Windows (Git Bash)

```bash
# 1. Перейдите в директорию проекта
cd config-valia

# 2. Запустите демонстрацию
bash run_all_stages.sh
```

### Windows (PowerShell)

```powershell
# 1. Перейдите в директорию проекта
cd config-valia

# 2. Запустите Python напрямую (пример для этапа 1)
python dependency_visualizer.py --package A --repo-url test_repo.txt --test-mode --output test.svg --max-depth 3
```

## Запуск отдельных этапов

```bash
./run_stage1.sh  # Этап 1: Конфигурация
./run_stage2.sh  # Этап 2: Сбор данных
./run_stage3.sh  # Этап 3: Построение графа
./run_stage4.sh  # Этап 4: Обратные зависимости
./run_stage5.sh  # Этап 5: Визуализация
```

## Примеры команд

### Простой запуск

```bash
python3 dependency_visualizer.py \
  --package A \
  --repo-url test_repo.txt \
  --test-mode \
  --output graph.svg
```

### С фильтрацией

```bash
python3 dependency_visualizer.py \
  --package W \
  --repo-url test_repo.txt \
  --test-mode \
  --output graph_filtered.svg \
  --filter Y
```

### Обратные зависимости

```bash
python3 dependency_visualizer.py \
  --package G \
  --repo-url test_repo.txt \
  --test-mode \
  --output graph.svg \
  --reverse-deps
```

### Реальный репозиторий Alpine

```bash
python3 dependency_visualizer.py \
  --package busybox \
  --repo-url https://dl-cdn.alpinelinux.org/alpine/v3.18/main/x86_64 \
  --output busybox_deps.svg \
  --max-depth 5
```

## Просмотр результатов

### Mermaid файлы

```bash
# Просмотр в терминале
cat graph_A.mmd

# Или откройте в браузере
# https://mermaid.live
# и вставьте содержимое .mmd файла
```

### SVG файлы

Откройте в любом браузере или просмотрщике изображений:

```bash
# Linux
xdg-open graph_A.svg

# macOS
open graph_A.svg

# Windows
start graph_A.svg
```

## Документация

- **README.md** - Основная документация проекта
- **SCRIPTS_README.md** - Подробная информация о скриптах
- **VISUALIZATION_EXAMPLES.md** - Примеры визуализации и сравнение
- **SUMMARY.md** - Полный итоговый отчет
- **QUICKSTART.md** - Этот файл

## Требования

- Python 3.7+
- Bash/Zsh (для shell-скриптов)
- Интернет (опционально, для работы с реальными репозиториями)

## Помощь

```bash
python3 dependency_visualizer.py --help
```

---

**Время выполнения полной демонстрации:** ~10-20 секунд

**Создаваемые файлы:** graph_A.svg, graph_L.svg, graph_P.svg + соответствующие .mmd файлы
