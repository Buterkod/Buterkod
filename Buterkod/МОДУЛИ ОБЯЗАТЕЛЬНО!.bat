@echo off
chcp 65001 >nul
title Buterkod Launcher

echo =========================================
echo      Загрузка модулей для Buterkod
echo Мы сообщим вам когда загрузка завершится
echo =========================================
echo.

set /p choice="Хотите установить/обновить необходимые модули для Buterkod? (Y/N): "

if /i "%choice%"=="Y" (
    echo.
    echo [INFO] Начинаем скачивание и установку модулей...
    echo [INFO] Пожалуйста, подождите, это может занять несколько секунд.
    echo.
    
    :: Устанавливаем PyQt6 (вместе с мультимедиа) и requests, которые нужны для Buterkod.pyw
    pip install PyQt6 PyQt6-QtMultimedia requests
    
    echo.
    echo ========================================
    echo [УСПЕХ] Загрузка и установка завершена!
    echo ========================================
    echo.
) else (
    echo.
    echo [INFO] Установка модулей пропущена пользователем.
    echo.
)

echo [INFO] Запуск Buterkod...
echo.

:: Запускаем правильный файл с графическим интерфейсом
python Buterkod.pyw

pause