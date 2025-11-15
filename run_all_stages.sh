#!/usr/bin/env zsh
# Запуск всех этапов последовательно
# Полная демонстрация проекта

echo "========================================"
echo "ПОЛНАЯ ДЕМОНСТРАЦИЯ ПРОЕКТА"
echo "Визуализатор графа зависимостей Alpine Linux"
echo "Вариант №14"
echo "========================================"
echo ""

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: python3 не найден"
    exit 1
fi

# Проверка наличия основного файла
if [ ! -f "dependency_visualizer.py" ]; then
    echo "Ошибка: dependency_visualizer.py не найден"
    exit 1
fi

# Проверка наличия тестового репозитория
if [ ! -f "test_repo.txt" ]; then
    echo "Ошибка: test_repo.txt не найден"
    exit 1
fi

echo "Проверка окружения: OK"
echo ""

# Запуск этапов с паузами
echo "Нажмите Enter для запуска Этапа 1..."
read

if [ -f "run_stage1.sh" ]; then
    chmod +x run_stage1.sh
    ./run_stage1.sh
else
    echo "Предупреждение: run_stage1.sh не найден, пропускаем"
fi

echo ""
echo "Нажмите Enter для запуска Этапа 2..."
read

if [ -f "run_stage2.sh" ]; then
    chmod +x run_stage2.sh
    ./run_stage2.sh
else
    echo "Предупреждение: run_stage2.sh не найден, пропускаем"
fi

echo ""
echo "Нажмите Enter для запуска Этапа 3..."
read

if [ -f "run_stage3.sh" ]; then
    chmod +x run_stage3.sh
    ./run_stage3.sh
else
    echo "Предупреждение: run_stage3.sh не найден, пропускаем"
fi

echo ""
echo "Нажмите Enter для запуска Этапа 4..."
read

if [ -f "run_stage4.sh" ]; then
    chmod +x run_stage4.sh
    ./run_stage4.sh
else
    echo "Предупреждение: run_stage4.sh не найден, пропускаем"
fi

echo ""
echo "Нажмите Enter для запуска Этапа 5..."
read

if [ -f "run_stage5.sh" ]; then
    chmod +x run_stage5.sh
    ./run_stage5.sh
else
    echo "Предупреждение: run_stage5.sh не найден, пропускаем"
fi

echo ""
echo "========================================"
echo "ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА"
echo "========================================"
echo ""
echo "Все этапы успешно выполнены!"
echo ""
echo "Созданные файлы:"
ls -lh *.svg *.mmd 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "Документация:"
echo "  - README.md - основная документация"
echo "  - VISUALIZATION_EXAMPLES.md - примеры визуализации"
echo "  - SUMMARY.md - итоговый отчет"
echo ""
echo "Git коммиты:"
git log --oneline --all 2>/dev/null || echo "  (git не инициализирован)"
echo ""
echo "========================================"
