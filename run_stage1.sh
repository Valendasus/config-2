#!/usr/bin/env zsh
# Этап 1: Минимальный прототип с конфигурацией
# Демонстрация парсинга аргументов, валидации и вывода конфигурации

echo "========================================"
echo "ЭТАП 1: Минимальный прототип"
echo "========================================"
echo ""

# Пример 1: Корректные параметры
echo ">>> Тест 1: Корректные параметры"
python3 dependency_visualizer.py \
  --package busybox \
  --repo-url https://dl-cdn.alpinelinux.org/alpine/v3.18/main/x86_64 \
  --output test_graph.svg \
  --max-depth 5

echo ""
echo "----------------------------------------"
echo ""

# Пример 2: Тестовый режим с фильтром
echo ">>> Тест 2: Тестовый режим с фильтром"
python3 dependency_visualizer.py \
  --package A \
  --repo-url test_repo.txt \
  --test-mode \
  --output deps.svg \
  --max-depth 3 \
  --filter dev

echo ""
echo "----------------------------------------"
echo ""

# Пример 3: Демонстрация обработки ошибок
echo ">>> Тест 3: Обработка ошибок - отрицательная глубина"
python3 dependency_visualizer.py \
  --package busybox \
  --repo-url https://example.com \
  --output test.svg \
  --max-depth -1

echo ""
echo "----------------------------------------"
echo ""

echo ">>> Тест 4: Обработка ошибок - неверное расширение"
python3 dependency_visualizer.py \
  --package busybox \
  --repo-url https://example.com \
  --output test.png

echo ""
echo "----------------------------------------"
echo ""

echo ">>> Тест 5: Справка"
python3 dependency_visualizer.py --help

echo ""
echo "========================================"
echo "ЭТАП 1 завершен"
echo "========================================"
