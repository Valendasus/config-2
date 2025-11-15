#!/usr/bin/env zsh
# Этап 4: Обратные зависимости
# Демонстрация поиска пакетов, которые зависят от данного

echo "========================================"
echo "ЭТАП 4: Обратные зависимости"
echo "========================================"
echo ""

# Пример 1: Базовая зависимость
echo ">>> Тест 1: Пакет G - базовая зависимость (много обратных зависимостей)"
python3 dependency_visualizer.py \
  --package G \
  --repo-url test_repo.txt \
  --test-mode \
  --output test.svg \
  --reverse-deps \
  --max-depth 10

echo ""
echo "----------------------------------------"
echo ""

# Пример 2: Популярная зависимость
echo ">>> Тест 2: Пакет I - популярная зависимость"
python3 dependency_visualizer.py \
  --package I \
  --repo-url test_repo.txt \
  --test-mode \
  --output test.svg \
  --reverse-deps \
  --max-depth 10

echo ""
echo "----------------------------------------"
echo ""

# Пример 3: Пакет в цикле
echo ">>> Тест 3: Пакет A - участвует в цикле зависимостей"
python3 dependency_visualizer.py \
  --package A \
  --repo-url test_repo.txt \
  --test-mode \
  --output test.svg \
  --reverse-deps \
  --max-depth 10

echo ""
echo "----------------------------------------"
echo ""

# Пример 4: С фильтрацией
echo ">>> Тест 4: Пакет Z - с фильтрацией (исключить X)"
python3 dependency_visualizer.py \
  --package Z \
  --repo-url test_repo.txt \
  --test-mode \
  --output test.svg \
  --reverse-deps \
  --max-depth 10 \
  --filter X

echo ""
echo "----------------------------------------"
echo ""

# Пример 5: Пакет без обратных зависимостей
echo ">>> Тест 5: Пакет P - нет обратных зависимостей"
python3 dependency_visualizer.py \
  --package P \
  --repo-url test_repo.txt \
  --test-mode \
  --output test.svg \
  --reverse-deps \
  --max-depth 10

echo ""
echo "========================================"
echo "ЭТАП 4 завершен"
echo "========================================"
