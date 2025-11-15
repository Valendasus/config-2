#!/usr/bin/env zsh
# Этап 3: Построение графа зависимостей
# Демонстрация DFS без рекурсии, обработки циклов, фильтрации

echo "========================================"
echo "ЭТАП 3: Построение графа зависимостей"
echo "========================================"
echo ""

# Пример 1: Простой иерархический граф
echo ">>> Тест 1: Простой граф - пакет A (max-depth=3)"
python3 dependency_visualizer.py \
  --package A \
  --repo-url test_repo.txt \
  --test-mode \
  --output test_a.svg \
  --max-depth 3

echo ""
echo "----------------------------------------"
echo ""

# Пример 2: Граф с циклическими зависимостями
echo ">>> Тест 2: Циклические зависимости - пакет L (max-depth=5)"
python3 dependency_visualizer.py \
  --package L \
  --repo-url test_repo.txt \
  --test-mode \
  --output test_l.svg \
  --max-depth 5

echo ""
echo "----------------------------------------"
echo ""

# Пример 3: Фильтрация пакетов
echo ">>> Тест 3: Фильтрация - пакет W, исключить пакеты с 'Y'"
python3 dependency_visualizer.py \
  --package W \
  --repo-url test_repo.txt \
  --test-mode \
  --output test_w.svg \
  --max-depth 5 \
  --filter Y

echo ""
echo "----------------------------------------"
echo ""

# Пример 4: Ограничение глубины
echo ">>> Тест 4: Ограничение глубины - пакет P (max-depth=1)"
python3 dependency_visualizer.py \
  --package P \
  --repo-url test_repo.txt \
  --test-mode \
  --output test_p.svg \
  --max-depth 1

echo ""
echo "----------------------------------------"
echo ""

# Пример 5: Граф с циклом W-X-Y-Z
echo ">>> Тест 5: Сложный цикл - пакет W (max-depth=10)"
python3 dependency_visualizer.py \
  --package W \
  --repo-url test_repo.txt \
  --test-mode \
  --output test_w_full.svg \
  --max-depth 10

echo ""
echo "========================================"
echo "ЭТАП 3 завершен"
echo "========================================"
