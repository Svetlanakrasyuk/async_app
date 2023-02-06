import pytest
import asyncio
from httpx import AsyncClient

from app import app

base_url = "http://127.0.0.1:8000"

@pytest.fixture(scope="module")
def event_loop():
    """A module-scoped event loop."""
    return asyncio.new_event_loop()


@pytest.mark.asyncio
async def get_id_menu():
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.get("/api/v1/menus")
        first_id = r.json()[0]['id']
        return first_id

@pytest.mark.asyncio
async def get_id_submenu():
    api_test_menu_id = await get_id_menu()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.get(
            f"/api/v1/menus/{api_test_menu_id}/submenus/",
        )
    id_submenu = r.json()[0]['id']
    return id_submenu

@pytest.mark.asyncio
async def get_id_dish():
    api_test_menu_id = await get_id_menu()
    id_submenu = await get_id_submenu()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.get(
            f"/api/v1/menus/{api_test_menu_id}/submenus/{id_submenu}/dishes",
        )
    id_dish = r.json()[0]['id']
    return id_dish

@pytest.mark.asyncio
async def test_get_menus() -> None:
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.get("/api/v1/menus")
    # content = response.json()
    assert response.status_code == 200, "Expected 200 code."


@pytest.mark.asyncio
async def test_create_menu():
    async with AsyncClient(app=app, base_url=base_url) as ac:
        payload = {"title": "menu1", "description": "menu1 description"}
        r = await ac.post("/api/v1/menus", json=payload)
    assert r.status_code == 201

@pytest.mark.asyncio
async def test_get_menu():
    id = await get_id_menu()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.get(f"/api/v1/menus/{id}")
        myjson = r.json()
    assert myjson['title'] == "menu1"
    assert myjson['description'] == "menu1 description"
    assert myjson['submenus_count'] == 0
    assert myjson['dishes_count'] == 0
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_update_menu():
    id = await get_id_menu()
    payload = {
        "title": "menu1 updated",
        "description": "menu1 description updated",
    }
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.patch(f"/api/v1/menus/{id}", json=payload)
        r = await ac.get(f"/api/v1/menus/{id}")
        myjson = r.json()
    assert myjson['title'] == "menu1 updated"
    assert myjson['description'] == "menu1 description updated"
    assert myjson['submenus_count'] == 0
    assert myjson['dishes_count'] == 0
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_delete_menu():
    id = await get_id_menu()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.delete(f"/api/v1/menus/{id}")
        myjson = r.json()
    assert myjson['status'] == True
    assert myjson['message'] == "The menu has been deleted"
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_get_submenus():
    await test_create_menu()
    api_test_menu_id = await get_id_menu()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.get(
            f"/api/v1/menus/{api_test_menu_id}/submenus/",
        )
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_create_submenu():
    api_test_menu_id = await get_id_menu()
    payload = {
        "title": "submenu1", "description": "submenu1 description",
        "main_menu_id": api_test_menu_id,
    }
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.post(
            f"/api/v1/menus/{api_test_menu_id}/submenus", json=payload,
        )
    myjson = r.json()
    assert myjson['title'] == "submenu1"
    assert r.status_code == 201

@pytest.mark.asyncio
async def test_get_submenu():
    api_test_menu_id = await get_id_menu()
    id_submenu = await get_id_submenu()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.get(
            f"/api/v1/menus/{api_test_menu_id}/submenus/{id_submenu}",
        )
        myjson = r.json()
    assert myjson['title'] == "submenu1"
    assert myjson['description'] == "submenu1 description"
    assert myjson['main_menu_id'] == api_test_menu_id
    assert myjson['dishes_count'] == 0
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_update_submenu():
    api_test_menu_id = await get_id_menu()
    id_submenu = await get_id_submenu()
    payload = {
        "title": "submenu1 updated",
        "description": "submenu1 description updated",
    }
    async with AsyncClient(app=app, base_url=base_url) as ac:
        await ac.patch(
            f"/api/v1/menus/{api_test_menu_id}/submenus/{id_submenu}", json=payload,
        )
        r = await ac.get(
            f"/api/v1/menus/{api_test_menu_id}/submenus/{id_submenu}",
        )
        myjson = r.json()
    assert myjson['title'] == "submenu1 updated"
    assert myjson['description'] == "submenu1 description updated"
    # assert myjson['main_menu_id'] == api_test_menu_id
    assert myjson['dishes_count'] == 0
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_delete_submenu():
    api_test_menu_id = await get_id_menu()
    id_submenu = await get_id_submenu()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.delete(
            f"/api/v1/menus/{api_test_menu_id}/submenus/{id_submenu}",
        )
        myjson = r.json()
    assert myjson['status'] == True
    assert myjson['message'] == "The submenu has been deleted"
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_get_dishes():
    await test_create_submenu()
    api_test_menu_id = await get_id_menu()
    id_submenu = await get_id_submenu()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.get(
            f"/api/v1/menus/{api_test_menu_id}/submenus/{id_submenu}/dishes",
        )
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_create_dish():
    api_test_menu_id = await get_id_menu()
    id_submenu = await get_id_submenu()
    payload = {
        "title": "dish1",
        "description": "dish1 description",
        "submenu_id": id_submenu,
        "price": "10.20",
    }
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.post(
            f"/api/v1/menus/{api_test_menu_id}/submenus/{id_submenu}/dishes", json=payload,
        )
        myjson = r.json()
    assert myjson['title'] == "dish1"
    assert myjson['description'] == "dish1 description"
    assert myjson['submenu_id'] == id_submenu
    assert myjson['price'] == "10.20"
    assert r.status_code == 201

@pytest.mark.asyncio
async def test_get_dish():
    api_test_menu_id = await get_id_menu()
    id_submenu = await get_id_submenu()
    id_dish = await get_id_dish()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.get(
            f"/api/v1/menus/{api_test_menu_id}/submenus/{id_submenu}/dishes/{id_dish}",
        )
        myjson = r.json()
    assert myjson['title'] == "dish1"
    assert myjson['description'] == "dish1 description"
    assert myjson['submenu_id'] == id_submenu
    assert myjson['price'] == "10.20"
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_update_dish():
    api_test_menu_id = await get_id_menu()
    id_submenu = await get_id_submenu()
    id_dish = await get_id_dish()
    payload = {
        "title": "dish1 updated",
        "description": "dish1 description updated",
        "price": "20.30",
    }
    async with AsyncClient(app=app, base_url=base_url) as ac:
        await ac.patch(
            f"/api/v1/menus/{api_test_menu_id}/submenus/{id_submenu}/dishes/{id_dish}", json=payload,
        )
        r = await ac.get(
            f"/api/v1/menus/{api_test_menu_id}/submenus/{id_submenu}/dishes/{id_dish}",
        )
        myjson = r.json()
    assert myjson['title'] == "dish1 updated"
    assert myjson['description'] == "dish1 description updated"
    assert myjson['price'] == "20.30"
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_delete_dish():
    api_test_menu_id = await get_id_menu()
    id_submenu = await get_id_submenu()
    id_dish = await get_id_dish()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        r = await ac.delete(
            f"/api/v1/menus/{api_test_menu_id}/submenus/{id_submenu}/dishes/{id_dish}",
        )
        myjson = r.json()
    assert myjson['status'] == True
    assert myjson['message'] == "The dish has been deleted"
    await test_delete_menu()
    assert r.status_code == 200
