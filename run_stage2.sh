#!/usr/bin/env zsh
# Этап 2: Сбор данных о зависимостях
# Демонстрация получения прямых зависимостей из репозитория Alpine Linux

echo "========================================"
echo "ЭТАП 2: Сбор данных о зависимостях"
echo "========================================"
echo ""

# Пример 1: Пакет busybox
echo ">>> Тест 1: Пакет busybox (минимальные зависимости)"
python3 dependency_visualizer.py \
  --package busybox \
  --repo-url https://dl-cdn.alpinelinux.org/alpine/v3.18/main/x86_64 \
  --output busybox.svg

echo ""
echo "----------------------------------------"
echo ""

# Пример 2: Пакет alpine-base
echo ">>> Тест 2: Пакет alpine-base (множество зависимостей)"
python3 dependency_visualizer.py \
  --package alpine-base \
  --repo-url https://dl-cdn.alpinelinux.org/alpine/v3.18/main/x86_64 \
  --output alpine-base.svg

echo ""
echo "----------------------------------------"
echo ""

# Пример 3: Пакет musl
echo ">>> Тест 3: Пакет musl (базовая библиотека без зависимостей)"
python3 dependency_visualizer.py \
  --package musl \
  --repo-url https://dl-cdn.alpinelinux.org/alpine/v3.18/main/x86_64 \
  --output musl.svg

echo ""
echo "----------------------------------------"
echo ""

# Пример 4: Тестовый репозиторий
echo ">>> Тест 4: Тестовый репозиторий - пакет A"
python3 dependency_visualizer.py \
  --package A \
  --repo-url test_repo.txt \
  --test-mode \
  --output test_a.svg

echo ""
echo "========================================"
echo "ЭТАП 2 завершен"
echo "========================================"
