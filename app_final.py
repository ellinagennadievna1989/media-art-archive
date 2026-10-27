import logging
import os
import html
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Настройки можно менять через переменные окружения.
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_NAME = os.getenv("APP_NAME", "Архив медиаарта")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Записываем время, уровень, имя логгера и сообщение.
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("media_art_archive")

# Учебный каталог хранится в памяти; база данных для задания не требуется.
# Источники и ссылки на изображения хранятся вместе с описанием проекта.
PROJECTS: list[dict[str, Any]] = [
    {
        "id": 1,
        "title": "In the Wake of Rhapsody",
        "year": 2026,
        "author": "Эллина Геннадьевна",
        "medium": "девятиканальная пространственная звуковая композиция, 10 минут",
        "venue": "Дом культуры «ГЭС-2»",
        "exhibition": "«Натюрморт. Портрет. Пейзаж. После жанра»",
        "city": "Москва",
        "exhibited_year": 2026,
        "duration_minutes": 10,
        "description": "Девятиканальная пространственная звуковая композиция, художественно представляющая возможный звуковой мир белух подо льдом. Работа обращается к истории белух, оказавшихся в ледовом плену зимой 1984–1985 годов, и спасательной операции с участием ледокола «Москва», использовавшего музыку, чтобы направить животных к выходу из ледового поля. Композиция объединяет природные и индустриальные шумы, музыкальные фрагменты и звуки, созданные с помощью генеративного искусственного интеллекта. Работа вступает в диалог с картиной Клода Моне «Мост Ватерлоо»: как очертания моста растворяются в тумане и дымке над водой, так в звуковом ландшафте смешиваются голоса животных, шум техники и музыка. Девятый звуковой канал намеренно не обозначен; его обнаружение становится частью телесного и пространственного опыта слушателя. Работа не является реконструкцией исторической звукозаписи спасательной операции, а предлагает художественную интерпретацию возможной подводной звуковой среды.",
        "tags": [
            "звук",
            "пространственный-звук",
            "белухи",
            "генеративный-ии",
            "полевые-записи",
            "экология",
            "память",
            "телесное-восприятие",
            "девять-каналов"
        ],
        "source_url": "https://ellinagennadievna.com/",
        "related_links": [],
        "image_url": "/static/images/in-the-wake-of-rhapsody-01.jpg",
        "gallery": [
            "/static/images/in-the-wake-of-rhapsody-01.jpg",
            "/static/images/in-the-wake-of-rhapsody-02.jpg",
            "/static/images/in-the-wake-of-rhapsody-03.jpg",
            "/static/images/in-the-wake-of-rhapsody-04.jpg"
        ],
        "status": "exhibited",
        "technical_details": "Не указаны",
        "credits": "Не указаны"
    },
    {
        "id": 2,
        "title": "Поляризация",
        "year": 2024,
        "medium": "инсталляция, нейросети, камеры, видео",
        "description": "Проект связывает художественные практики Эллины Геннадьевны и Алигьеро Боэтти и исследует, как сознание и память формируют, хранят и воспроизводят системы знания и опыта. Головоломки Боэтти становятся промптами для рекурсивной игры с нейросетями; созданные изображения превращаются в новые стимулы для воображения зрителя. Инсталляция исследует реконсолидaцию памяти, ложные воспоминания и искажение образа зрителя алгоритмами.",
        "tags": [
            "нейросети",
            "память",
            "инсталляция",
            "alighiero-boetti",
            "искусственный-интеллект"
        ],
        "source_url": "https://ellinagennadievna.com/ru-polarization",
        "image_url": "/static/images/project-02.jpg"
    },
    {
        "id": 3,
        "title": "10 : 10",
        "year": 2025,
        "medium": "мультимедийная инсталляция с ИИ и генеративным звуком",
        "description": "Работа исследует то, что сопротивляется цифровой интерпретации. Образ часов, показывающих 10:10, часто возникает в изображениях, созданных нейросетями. В инсталляции случайно выбранный квадрат пространства описывается нейросетью и превращается в почти идентичные, но слегка искажённые изображения. Текст становится ритмическим речитативом, передаваемым через вибродинамик; дым, пересекающий лазерную сетку, создаёт неповторимые узоры.",
        "tags": [
            "нейросети",
            "генеративный-звук",
            "инсталляция",
            "случайность",
            "цифровая-реальность"
        ],
        "source_url": "https://ellinagennadievna.com/1010",
        "related_links": [{"label": "Презентация проекта", "url": "https://lolagrhm.wfolio.pro/disk/10-10"}],
        "image_url": "/static/images/project-03.jpg"
    },
    {
        "id": 4,
        "title": "ESC",
        "year": 2021,
        "medium": "мультимедийная интерактивная инсталляция, VRChat",
        "description": "Зрителям предлагается принять участие в воссоздании перформанса коллективного бега. Работа отсылает к проекту группы Escape «Исчезновение» (2000) и акции Иржи Кованды (1978). Используя VRChat, художница исследует ограничения виртуального мира и перенос социальных проблем в цифровое пространство.",
        "tags": [
            "vr",
            "виртуальная-реальность",
            "инсталляция",
            "перформанс"
        ],
        "source_url": "https://ellinagennadievna.com/ESC_RU",
        "image_url": "/static/images/project-04.jpg"
    },
    {
        "id": 5,
        "title": "56.656901, 44.663716",
        "year": 2024,
        "medium": "тафтинг, QR-код, полевые записи, 140 × 200 см",
        "description": "Тафтинговый ковёр создан по паттерну сонограммы пения иволги. Частота звуковых волн определяет цвет и длину шерстяной нити, а QR-код ведёт к оригинальной полевой записи пения птицы, сделанной художницей.",
        "tags": [
            "звук",
            "природа",
            "полевые-записи",
            "тафтинг"
        ],
        "source_url": "https://ellinagennadievna.com/ru-5611",
        "related_links": [{"label": "Запись пения иволги", "url": "https://468249.cargo.site/"}],
        "image_url": "/static/images/project-05.jpg"
    },
    {
        "id": 6,
        "title": "Andy",
        "year": 2021,
        "year_end": 2023,
        "medium": "восьмиканальная звуковая инсталляция, 3D-печать",
        "description": "В композиции использованы полевые записи леса в период активного пения соловьёв, записи домашних волнистых попугаев, гранулярный синтез и звуки искусственного интеллекта, созданные на основе анализа соловьиных песен.",
        "tags": [
            "звук",
            "полевые-записи",
            "искусственный-интеллект",
            "многоканальный-звук"
        ],
        "source_url": "https://ellinagennadievna.com/AndyRu",
        "related_links": [{"label": "Видео", "url": "https://youtube.com/shorts/8ya4aPWT0kQ?si=At5tElcNZLQYP7tV"}],
        "image_url": "/static/images/project-06.jpg"
    },
    {
        "id": 7,
        "title": "Зона",
        "year": 2019,
        "medium": "VRChat world, performance; интерактивная инсталляция",
        "description": "«Зона» — игра добровольного заключения. Свободное пространство комнаты очерчивается виртуальными границами; игра заканчивается, если игрок снимает VR-очки или выходит за границы. Посетители могут встретиться с игроком в комнате посещений, а виртуальное и физическое пространство транслируются онлайн.",
        "tags": [
            "vr",
            "vrchat",
            "свобода",
            "цифровые-границы",
            "игра",
            "инсталляция"
        ],
        "source_url": "https://ellinagennadievna.com/ru-ZONE",
        "image_url": "/static/images/project-07.jpg"
    },
    {
        "id": 8,
        "title": "Стабильность",
        "year": 2017,
        "year_end": 2020,
        "medium": "акриловый куб 10 × 10 × 10 см, Arduino; интерактивная инсталляция с квадрофоническим звуком (версия 2020)",
        "description": "Проект обращается к понятию постправды через непрекращающуюся подмену одного порядка другим. Подмена кажется паразитом, манипулирующим системой, но одновременно оказывается её собственным механизмом. Предсказуемость убивает элемент случайности.",
        "tags": [
            "arduino",
            "случайность",
            "система",
            "постправда"
        ],
        "source_url": "https://ellinagennadievna.com/stability",
        "related_links": [{"label": "Видео", "url": "https://youtu.be/cPvatCXunkc"}],
        "image_url": "/static/images/project-08.jpg"
    },
    {
        "id": 9,
        "title": "Прецедент",
        "year": 2017,
        "medium": "черно-белая печать (40 × 50 см), видео",
        "description": "Постоянная вовлеченность в информационный поток требует всё большей скорости реакции на события и одновременно вызывает потребность в защите от информационной перегрузки. Клиповое мышление решает эти проблемы, вызывая другие: изображение с экрана заменяет собственное представление, а голос диктора и мнения экспертов — собственное размышление. Зрелищная драматизация облагораживает пассивность зрителя. Потребность в головокружении от действительности и истории формирует «неореальность», не имеющую категорий истинности и ложности.",
        "tags": ["информационный-поток", "информационная-перегрузка", "клиповое-мышление", "медиа", "неореальность", "видео"],
        "source_url": "https://ellinagennadievna.com/ru-precedent",
        "image_url": "/static/images/project-09.jpg",
        "gallery": ["/static/images/project-09.jpg"]
    },
    {
        "id": 10,
        "title": "Roots",
        "year": 2019,
        "medium": "интерактивная игра / инсталляция, Unity3D, Arduino, датчик углекислого газа",
        "description": "Интерактивная работа о сети корней деревьев и природной коммуникации. Игрок восстанавливает связь между корнями с помощью дыхания: датчик углекислого газа в маске-контроллере отслеживает дыхание и влияет на рост корней и громкость звукового ландшафта. Саундтрек основан на треске ветвей и подводных записях.",
        "tags": [
            "звук",
            "игра",
            "музыка",
            "bio-future"
        ],
        "source_url": "https://ellinagennadievna.com/ru-roots",
        "related_links": [{"label": "Видео", "url": "https://youtu.be/xixd17BtcyY"}],
        "credits": ["Мария Свиридова", "Дмитрий Кузнецов"],
        "image_url": "/static/images/project-10.jpg"
    },
    {
        "id": 11, "title": "Gela", "year": 2024, "medium": "AR-ковёр, дополненная реальность, QR-код",
        "description": "Ковёр исследует превращение способов кодирования информации — от узоров, вплетённых в ковры, до QR-кодов. QR-код открывает дополненную реальность, в которой появляется цифровой образ собаки Гелы. Проект обращается к алгоритмическому кодированию, истории Ады Лавлейс и способам сохранения личных историй с помощью цифровых технологий.",
        "tags": ["ковёр", "дополненная-реальность", "qr-код", "память", "ада-лавлейс"],
        "source_url": "https://ellinagennadievna.com/gela", "image_url": "/static/images/project-11.jpg", "related_links": []
    },
    {
        "id": 12, "title": "Merge", "year": 2023, "medium": "интерактивный ковёр, нейросети, QR-коды, AR, оптоволокно",
        "description": "Интерактивный проект, вдохновлённый работой Ады Лавлейс. Нейросети используются для создания узора ковра со встроенными QR-кодами, которые открывают отдельные истории в дополненной реальности. В ткань вплетены оптоволоконные кабели, отсылающие к сетевым связям цифрового мира. Ковёр становится интерфейсом для обмена историями и впечатлениями.",
        "tags": ["ковёр", "нейросети", "дополненная-реальность", "qr-код", "оптоволокно"],
        "source_url": "https://ellinagennadievna.com/merge", "related_links": [{"label": "Видео", "url": "https://youtube.com/shorts/-78BPv4oABM?si=lT207UUk5sK32T6p"}], "image_url": "/static/images/project-12.jpg"
    },
    {
        "id": 13, "title": "Drag", "year": 2022, "medium": "интерактивная аудиоинсталляция, веб-сайт, игровая механика",
        "description": "Интерактивная аудиоработа в формате сайта и игры. Пользователь находит камень и перетаскивает его, чтобы услышать музыку. Работа предлагает простой жест как способ взаимодействия со звуком и цифровым пространством.",
        "tags": ["звук", "игра", "веб", "интерактивность"],
        "source_url": "https://doshikbezkipyatka.github.io/drag/", "image_url": "/static/images/project-13.jpg", "related_links": []
    },
    {
        "id": 14, "title": "Furrminator (Rainforest IV)", "year": 2020, "medium": "вибродинамики, матрас, запись кошачьего мурлыканья",
        "description": "Объект создан в рамках лаборатории пространственного звука, посвящённой реконструкции Rainforest IV Дэвида Тюдора. Матрас, покрытый искусственным мехом, работает как динамик: вибродинамики передают низкочастотные колебания записи кошачьего мурлыканья через металлические пружины. Звук предлагается воспринимать всем телом, лёжа на объекте.",
        "tags": ["звук", "телесность", "инсталляция", "вибрация", "Rainforest-IV"],
        "source_url": "https://ellinagennadievna.com/furrminator", "related_links": [{"label": "Видео", "url": "https://youtu.be/y5NjYoHR11o"}], "image_url": "/static/images/project-14.jpg"
    },
    {
        "id": 15, "title": "Stalk", "year": 2018, "medium": "VR-видеоигра",
        "description": "VR-проект об обществе наблюдения и цифровом контроле. Участники добровольно передают GPS-координаты, которые зритель может отслеживать в виртуальной реальности, перемещаясь по городской карте. Работа исследует связь наблюдения, дисциплины, страха и власти в цифровом обществе.",
        "tags": ["vr", "наблюдение", "gps", "контроль", "цифровая-реальность"],
        "source_url": "https://ellinagennadievna.com/stalk", "related_links": [{"label": "Видео", "url": "https://youtu.be/-j4uYOZLJ8A"}], "image_url": "/static/images/project-15.jpg"
    },
    {
        "id": 16, "title": "Transform", "year": 2018, "medium": "интерактивная инсталляция, дополненная реальность, 3D-печать, эпоксидная смола",
        "description": "Полупрозрачный куб из эпоксидной смолы содержит напечатанную трёхмерную траекторию. Она создана виртуальной симуляцией движения несуществующего шара, которому в программе моделирования задавались искусственные физические силы. Проект связывает цифровую симуляцию с реальным объектом и образует цикл переходов между виртуальным и физическим.",
        "tags": ["3d-печать", "дополненная-реальность", "симуляция", "эпоксидная-смола"],
        "source_url": "https://ellinagennadievna.com/transform", "related_links": [{"label": "Видео", "url": "https://youtu.be/vXw3ZyyMwAQ"}], "image_url": "/static/images/project-16.jpg"
    },
    {
        "id": 17, "title": "Fiction", "year": 2018, "medium": "объект, дополненная реальность",
        "description": "Ранняя версия проекта Transform. Физического объекта ещё нет: его изображения и проекции создают образ несуществующего объекта. В реальном пространстве проекция появляется на кубе, а в виртуальном позволяет заглянуть внутрь его стен.",
        "tags": ["дополненная-реальность", "виртуальность", "проекция", "объект"],
        "source_url": "https://ellinagennadievna.com/fiction", "related_links": [{"label": "Видео", "url": "https://youtu.be/tTFjRIPtuco"}], "image_url": "/static/images/project-17.jpg"
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Логируем запуск и остановку приложения.
    logger.info("Запуск приложения «%s», версия %s", APP_NAME, APP_VERSION)
    yield
    logger.info("Приложение «%s» остановлено", APP_NAME)


app = FastAPI(title=APP_NAME, version=APP_VERSION,
              description="API-каталог проектов мультимедиа-арта.", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Middleware записывает метод, путь и HTTP-код каждого запроса.
    response = await call_next(request)
    logger.info("Запрос %s %s завершён с кодом %s",
                request.method, request.url.path, response.status_code)
    return response



@app.get("/", response_class=HTMLResponse)
def root():
    cards = []

    for project in PROJECTS:
        title = project.get("title", "Без названия")
        year = project.get("year", "")
        medium = project.get("medium", "")
        description = project.get("description", "")
        image_url = project.get("image_url", "")
        project_id = project.get("id", "")

        cards.append(f"""
        <div class="col">
          <article class="card h-100 border-0 shadow-sm">
            <a href="/projects/{project_id}/page" class="text-decoration-none">
              <img src="{image_url}"
                   class="card-img-top project-cover"
                   alt="{title}"
                   loading="lazy">
            </a>
            <div class="card-body d-flex flex-column">
              <div class="text-secondary small mb-2">{year}</div>
              <h2 class="h5 card-title">{title}</h2>
              <p class="text-secondary small">{medium}</p>
              <p class="card-text">{description}</p>
              <a href="/projects/{project_id}/page"
                   class="btn btn-outline-dark mt-auto align-self-start">
                Подробнее
              </a>
            </div>
          </article>
        </div>
        """)

    project_cards = "\n".join(cards)

    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Архив медиаарта</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
        rel="stylesheet">
  <style>
    body {{
      background: #f6f5f2;
      color: #222;
    }}
    .site-header {{
      background: #fff;
      border-bottom: 1px solid #e5e3df;
    }}
    .project-cover {{
      width: 100%;
      height: 240px;
      object-fit: cover;
      background: #e8e6e1;
    }}
    .card {{
      border-radius: 0.75rem;
      overflow: hidden;
    }}
    .card-text {{
      display: -webkit-box;
      -webkit-line-clamp: 5;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}
  </style>
</head>
<body>
  <header class="site-header py-4 mb-5">
    <div class="container">
      <div class="d-flex flex-wrap justify-content-between align-items-center gap-3">
        <a class="navbar-brand fs-4 fw-semibold" href="/">Архив медиаарта</a>
        <nav class="d-flex gap-3">
          <a class="link-dark" href="/docs">API документация</a>
          <a class="link-dark" href="/health">Статус</a>
        </nav>
      </div>
      <p class="text-secondary mt-3 mb-0">
        Проекты на пересечении искусства, технологий и исследования медиа.
      </p>
    </div>
  </header>

  <main class="container pb-5">
    <div class="d-flex flex-wrap justify-content-between align-items-end mb-4 gap-2">
      <div>
        <p class="text-uppercase small text-secondary mb-2">Каталог проектов</p>
        <h1 class="display-5">Медиаарт и технологии</h1>
      </div>
      <span class="text-secondary">{len(PROJECTS)} проектов</span>
    </div>

    <div class="row row-cols-1 row-cols-md-2 row-cols-xl-3 g-4">
      {project_cards}
    </div>
  </main>

  <footer class="container border-top py-4 text-secondary small">
    Архив медиаарта · FastAPI · Bootstrap 5.3
  </footer>
</body>
</html>"""



@app.get("/health")
def health():
    # Простой маршрут для проверки доступности сервиса.
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"app": APP_NAME, "version": APP_VERSION}


@app.get("/projects")
def list_projects():
    """Вернуть все проекты."""
    return {"count": len(PROJECTS), "items": PROJECTS}


@app.get("/projects/search")
def search_projects(tag: str = Query(..., min_length=1, description="Тег для поиска")):
    """Найти проекты по тегу без учёта регистра."""
    normalized_tag = tag.strip().lower()
    matches = [p for p in PROJECTS if normalized_tag in [t.lower() for t in p["tags"]]]
    logger.info("Поиск по тегу %r: найдено %d проектов", normalized_tag, len(matches))
    return {"query": normalized_tag, "count": len(matches), "items": matches}


@app.get("/projects/{project_id}")
def get_project(project_id: int):
    for project in PROJECTS:
        if project["id"] == project_id:
            return project

    raise HTTPException(
        status_code=404,
        detail=f"Проект с ID {project_id} не найден",
    )


@app.get("/projects/{project_id}/page", response_class=HTMLResponse)
def project_page(project_id: int):
    project = next(
        (p for p in PROJECTS if p["id"] == project_id),
        None,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail=f"Проект с ID {project_id} не найден",
        )

    title = project.get("title", "Без названия")
    year = project.get("year", "")
    medium = project.get("medium", "")
    description = project.get("description", "")
    image_url = project.get("image_url", "")
    venue = project.get("venue", "")
    tags = project.get("tags", [])

    tags_html = "".join(
        f'<span class="badge text-bg-light border me-1 mb-1">{tag}</span>'
        for tag in tags
    )

    return f"""
    <!doctype html>
    <html lang="ru">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{title} — Архив медиаарта</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
              rel="stylesheet">
    </head>
    <body class="bg-light">
        <main class="container py-5">
            <a href="/" class="btn btn-outline-dark mb-4">
                ← Назад к каталогу
            </a>
            <article class="card border-0 shadow-sm overflow-hidden">
                <div class="row g-0">
                    <div class="col-lg-7">
                        <img src="{image_url}"
                             class="img-fluid w-100 h-100"
                             style="object-fit: cover; min-height: 300px;"
                             alt="{title}">
                    </div>
                    <div class="col-lg-5">
                        <div class="card-body p-4 p-lg-5">
                            <p class="text-secondary">{year} · {medium}</p>
                            <h1 class="h2 mb-3">{title}</h1>
                            <p>{description}</p>
                            <p class="text-secondary">{venue}</p>
                            <div class="mt-3">{tags_html}</div>
                        </div>
                    </div>
                </div>
            </article>
        </main>
    </body>
    </html>
    """
