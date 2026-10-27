from fastapi.testclient import TestClient
from app_final import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_contains_docs_link():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "/docs" in response.text
    assert "bootstrap@5.3.3" in response.text
    assert "In the Wake of Rhapsody" in response.text


def test_version_has_name_and_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert "app" in response.json() and "version" in response.json()


def test_projects_returns_seventeen_items():
    response = client.get("/projects")
    assert response.status_code == 200
    assert response.json()["count"] == 17


def test_search_finds_polarization():
    response = client.get("/projects/search", params={"tag": "нейросети"})
    assert response.status_code == 200
    assert any(p["title"] == "Поляризация" for p in response.json()["items"])


def test_zone_has_user_provided_image():
    response = client.get("/projects/7")
    assert response.status_code == 200
    assert response.json()["image_url"] == "/static/images/project-07.jpg"
    image_response = client.get(response.json()["image_url"])
    assert image_response.status_code == 200
    assert image_response.headers["content-type"].startswith("image/")


def test_unknown_project_returns_404():
    response = client.get("/projects/9999")
    assert response.status_code == 404



def test_wake_of_rhapsody_has_updated_metadata():
    response = client.get("/projects/1")
    assert response.status_code == 200
    project = response.json()
    assert project["year"] == 2026
    assert project["duration_minutes"] == 10
    assert project["venue"] == "Дом культуры «ГЭС-2»"
    assert len(project["gallery"]) == 4
    assert "не является реконструкцией" in project["description"]


def test_precedent_has_source_description_and_images():
    response = client.get("/projects/9")
    assert response.status_code == 200
    project = response.json()
    assert project["year"] == 2017
    assert project["medium"] == "черно-белая печать (40 × 50 см), видео"
    assert project["source_url"] == "https://ellinagennadievna.com/ru-precedent"
    assert project["gallery"] == ["/static/images/project-09.jpg"]
    assert "неореальность" in project["description"]


def test_catalog_includes_projects_from_portfolio():
    response = client.get("/projects")
    titles = {project["title"] for project in response.json()["items"]}
    assert {"Gela", "Merge", "Drag", "Furrminator (Rainforest IV)", "Stalk", "Transform", "Fiction"}.issubset(titles)


def test_roots_is_interactive_installation_not_music_release():
    response = client.get("/projects/10")
    assert response.status_code == 200
    project = response.json()
    assert project["year"] == 2019
    assert "Arduino" in project["medium"]
    assert project["source_url"] == "https://ellinagennadievna.com/ru-roots"


def test_andy_has_eight_channel_period():
    response = client.get("/projects/6")
    assert response.status_code == 200
    project = response.json()
    assert project["year"] == 2021
    assert project["year_end"] == 2023
    assert "восьмиканальная" in project["medium"]


def test_all_projects_have_local_cover_images():
    response = client.get("/projects")
    assert response.status_code == 200
    for project in response.json()["items"]:
        image_url = project["image_url"]
        assert image_url.startswith("/static/images/")
        image_response = client.get(image_url)
        assert image_response.status_code == 200
        assert image_response.headers["content-type"].startswith("image/")
