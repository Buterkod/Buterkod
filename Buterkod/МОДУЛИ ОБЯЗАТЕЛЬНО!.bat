@echo off
chcp 65001 >nul
title Buterkod Launcher

echo ========================================
echo    Скачиватель модулей для Buterkod
echo ========================================
echo.

set /p choice="Хотите установить/обновить необходимые модули для Buterkod? (Y/N): "

if /i "%choice%"=="Y" (
    echo.
    echo [INFO] Скачивание и установка модулей...
    :: Вместо requests и pygame впиши свои модули, которые нужны твоему проекту
    pip install requests pygame 
    echo.
    echo [INFO] Установка завершена!
) else (
    echo.
    echo [INFO] Пропускаем установку модулей.
)

echo.
echo [INFO] Запуск Buterkod...
echo.

:: Замени main.py на имя твоего главного файла на Python (например, game.py или app.py)
python main.py

pause