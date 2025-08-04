echo @echo off
echo chcp 65001 ^>nul
echo.
echo echo 💾 Iniciando backup diário do Dashboard Baker...
echo echo 🕐 %%date%% %%time%%
echo.
echo set PGPASSWORD=senha123
echo set BACKUP_DIR=%%~dp0backups\daily
echo set TIMESTAMP=%%date:~6,4%%%%date:~3,2%%%%date:~0,2%%_%%time:~0,2%%%%time:~3,2%%%%time:~6,2%%
echo set TIMESTAMP=%%TIMESTAMP: =0%%
echo.
echo echo 📦 Criando backup: dashboard_baker_%%TIMESTAMP%%.sql
echo.
echo "%POSTGRES_PATH%\pg_dump" -h localhost -U postgres -d dashboard_baker ^> "%%BACKUP_DIR%%\dashboard_baker_%%TIMESTAMP%%.sql"
echo.
echo if %%errorlevel%% equ 0 (
echo     echo ✅ Backup criado com sucesso!
echo     echo 📁 Arquivo: %%BACKUP_DIR%%\dashboard_baker_%%TIMESTAMP%%.sql
echo ^) else (
echo     echo ❌ Erro ao criar backup
echo ^)
echo.
echo echo 🧹 Limpando backups antigos (mantendo últimos 7 dias^)...
echo forfiles /p "%%BACKUP_DIR%%" /s /m *.sql /d -7 /c "cmd /c del @path" ^>nul 2^>^&1
echo.
echo echo ✅ Backup diário concluído!
) > "backup_daily.bat"