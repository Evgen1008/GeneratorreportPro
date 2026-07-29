@echo off
chcp 65001 > nul

cd /d %~dp0

echo ===============================
echo GeneratorReportPro BUILD v1.0
echo ===============================

echo.

echo Очистка старой сборки...

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q GeneratorReportPro.spec 2>nul


echo.

echo Проверка PyInstaller...

pyinstaller --version

if errorlevel 1 (
    echo Установка PyInstaller...
    pip install pyinstaller
)


echo.

echo Сборка EXE...


python -m PyInstaller ^
--noconsole ^
--onedir ^
--name GeneratorReportPro ^
main.py


echo.

echo Создание структуры данных...


mkdir dist\GeneratorReportPro\data
mkdir dist\GeneratorReportPro\data\reports
mkdir dist\GeneratorReportPro\data\templates


echo.

echo Копирование базы...


copy data\generator_report.db dist\GeneratorReportPro\data\generator_report.db


echo.

echo Копирование шаблонов...


xcopy data\templates dist\GeneratorReportPro\data\templates /E /I /Y


echo.

echo ГОТОВО

echo.
echo Папка:
echo dist\GeneratorReportPro

pause