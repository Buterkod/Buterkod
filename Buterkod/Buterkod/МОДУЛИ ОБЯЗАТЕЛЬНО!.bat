@echo off
:: Устанавливаем кодировку UTF-8 и красивую цветовую схему (темный фон, ярко-зеленый текст)
chcp 65001 >nul
color 0A
title Buterkod Launcher - Custom Edition

echo           =============================================
echo                      МОДУЛИ ДЛЯ BUTERKOD 
echo             Мы сообщим вам, когда загрузка завершится
echo           =============================================
echo.

set /p choice="  [?] Установить необходимые модули для Buterkod? (Y/N): "

if /i "%choice%"=="Y" (
    echo.
    echo   [INFO] Подготовка к загрузке модулей...
    echo   [INFO] Пожалуйста, подождите, идет установка...
    echo.
    
    :: Установка библиотек (включая ursina для будущей 3D игры)
    pip install PyQt6 PyQt6-QtMultimedia requests ursina
    
    echo.
    echo   ====================================================
    echo   [УСПЕХ] Загрузка и установка полностью завершена!
    echo   ====================================================
    echo.
) else (
    echo.
    echo   [INFO] Установка модулей пропущена пользователем.
    echo.
)

echo   [INFO] Запуск главного интерфейса Buterkod...
echo.

:: Запуск лаунчера
if exist "Buterkod.pyw" (
    start pythonw Buterkod.pyw
) else (
    echo   [ОШИБКА] Файл Buterkod.pyw не найден в этой папке!
    pause
)