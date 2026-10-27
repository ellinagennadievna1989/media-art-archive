# API «Архив медиаарта»

Учебное API на FastAPI с каталогом из 17 выбранных проектов Эллины Геннадьевны. Описания основаны на страницах сайта художницы; для неуточнённых сведений оставлены пустые поля, а не выдуманные данные. Обложки проектов извлечены из предоставленного портфолио PDF и сохранены локально в `static/images/`; для первой работы также включена галерея из четырёх предоставленных фотографий.

## Маршруты
- `GET /` — главная страница.
- `GET /health` — проверка состояния.
- `GET /version` — имя и версия приложения.
- `GET /projects` — каталог.
- `GET /projects/{project_id}` — проект по ID.
- `GET /projects/search?tag=нейросети` — поиск по тегу.
- `GET /docs` — документация Swagger.

## Установка (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```
Если PowerShell блокирует активацию, выполни:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## Запуск
```powershell
uvicorn app_final:app
```
Открой http://127.0.0.1:8000/docs. Для обычного запуска не добавляй `--reload`.

## Тесты
```powershell
python -m pytest -v
```

## Настройки
`APP_NAME`, `APP_VERSION`, `LOG_LEVEL` задаются через переменные окружения. Пример — `.env.example`; настоящий `.env` не добавляй в Git.

## CI/CD
GitHub Actions запускает тесты на `push` и `pull_request`. Артефакт публикуется только после успешного прохождения тестов.

## Проекты и источники

Каталог содержит 17 проектов, выбранных из портфолио. Описания и ссылки на источники указаны в данных `app_final.py`; изображения обложек сохранены локально в `static/images/`. Для `In the Wake of Rhapsody` дополнительно включена галерея из четырёх предоставленных фотографий.

Проекты каталога:
1. In the Wake of Rhapsody
2. Поляризация
3. 10 : 10
4. ESC
5. 56.656901, 44.663716
6. Andy
7. Зона / ZONE
8. Стабильность
9. Прецедент
10. ROOTS
11. Gela
12. Merge
13. Drag
14. Furrminator (Rainforest IV)
15. Stalk
16. Transform
17. Fiction

Чтобы посмотреть полный каталог, запусти приложение и открой `/projects` или `/docs`. Фотографии отдаются локально по адресам вида `/static/images/project-02.jpg`; при запуске сервиса подключение к сайту-портфолио для отображения обложек не требуется.
