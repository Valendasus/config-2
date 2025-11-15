#!/usr/bin/env zsh
# Этап 5: Визуализация графа
# Демонстрация генерации Mermaid и SVG для трех различных пакетов

echo "========================================"
echo "ЭТАП 5: Визуализация графа"
echo "========================================"
echo ""

# Пример 1: Простой иерархический граф
echo ">>> Пример 1: Пакет A - простой иерархический граф"
python3 dependency_visualizer.py \
  --package A \
  --repo-url test_repo.txt \
  --test-mode \
  --output graph_A.svg \
  --max-depth 3

echo ""
echo "Созданы файлы:"
echo "  - graph_A.mmd (Mermaid код)"
echo "  - graph_A.svg (SVG визуализация)"
echo ""
echo "Просмотр Mermaid: https://mermaid.live"
echo ""
echo "----------------------------------------"
echo ""

# Пример 2: Граф с циклическими зависимостями
echo ">>> Пример 2: Пакет L - граф с циклическими зависимостями"
python3 dependency_visualizer.py \
  --package L \
  --repo-url test_repo.txt \
  --test-mode \
  --output graph_L.svg \
  --max-depth 5

echo ""
echo "Созданы файлы:"
echo "  - graph_L.mmd (Mermaid код)"
echo "  - graph_L.svg (SVG визуализация)"
echo ""
echo "----------------------------------------"
echo ""

# Пример 3: Линейная цепочка зависимостей
echo ">>> Пример 3: Пакет P - линейная цепочка зависимостей"
python3 dependency_visualizer.py \
  --package P \
  --repo-url test_repo.txt \
  --test-mode \
  --output graph_P.svg \
  --max-depth 10

echo ""
echo "Созданы файлы:"
echo "  - graph_P.mmd (Mermaid код)"
echo "  - graph_P.svg (SVG визуализация)"
echo ""
echo "----------------------------------------"
echo ""

# Вывод содержимого Mermaid файлов
echo ">>> Содержимое graph_A.mmd:"
echo ""
cat graph_A.mmd
echo ""
echo "----------------------------------------"
echo ""

echo ">>> Содержимое graph_L.mmd (первые 20 строк):"
echo ""
head -n 20 graph_L.mmd
echo "..."
echo ""
echo "----------------------------------------"
echo ""

echo ">>> Содержимое graph_P.mmd:"
echo ""
cat graph_P.mmd
echo ""
echo "========================================"
echo "ЭТАП 5 завершен"
echo ""
echo "Созданы визуализации для:"
echo "  1. Пакет A - простой граф (9 узлов)"
echo "  2. Пакет L - с циклами (13 узлов)"
echo "  3. Пакет P - линейная цепь (7 узлов)"
echo ""
echo "Для просмотра Mermaid графов:"
echo "  - Откройте https://mermaid.live"
echo "  - Вставьте содержимое .mmd файла"
echo "  - Или установите: npm install -g @mermaid-js/mermaid-cli"
echo "========================================"
