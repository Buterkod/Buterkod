@echo off
chcp 65001 >nul
title Buterkod Launcher

echo =========================================
echo      Загрузка модулей для Buterkod
echo Мы сообщим вам когда загрузке завершиться
echo =========================================
echo.

set /p choice="Хотите установить/обновить необходимые модули для Buterkod? (Y/N): "

if /i "%choice%"=="Y" (
    echo.
    echo [INFO] Начинаем скачивание и установку модулей...
    echo [INFO] Пожалуйста, подождите, это может занять несколько секунд.
    echo.
    
    :: Перечисли здесь через пробел все модули, которые нужны для Buterkod (например: requests pygame colorama)
    pip install requests pygame
    
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

:: Замени Buterkod.py на точное имя вашего главного файла (например, Buterkod.pyw или main.py)
python Buterkod.py

pause