# Real Estate Marketplace (Django + HTML)

Ijara xonadonlari e'lonlarini jamlaydigan platforma.

Loyiha `Django` backend + template frontend bilan ishlaydi va production chiqish oqimi `PythonAnywhere` uchun tayyorlangan.

## Imkoniyatlar
- E'lonlar ro'yxati, qidiruv va filter
- E'lon tafsiloti (ko'rishlar soni bilan)
- Login/registratsiya
- Login qilingan foydalanuvchi uchun e'lon qo'shish
- Django admin panel
- DRF API (`/api/v1/`)

## Lokal ishga tushirish
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements\base.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Sayt: `http://127.0.0.1:8000/`

## Default e'lonlarni avtomatik qo'shish
Quyidagi komanda rasmli default e'lonlarni yaratadi.

```bash
cd backend
python manage.py seed_default_listings --clear --count 24 --images-per-property 3
```

Asosiy parametrlar:
- `--clear`: eski e'lonlarni o'chirib, yangidan boshlaydi
- `--count`: nechta e'lon yaratilishi
- `--images-per-property`: har bir e'lon uchun rasm soni (`1..3`)
- `--owner <username>`: e'lon egasini aniq userga biriktirish

Misol:
```bash
python manage.py seed_default_listings --clear --count 30 --owner Boburjon
```

## Production cheklovi (PythonAnywhere only)
`DJANGO_DEBUG=False` bo'lganda loyiha quyidagilarni talab qiladi:
- `PYTHONANYWHERE_DOMAIN` majburiy
- domen `*.pythonanywhere.com` formatida bo'lishi shart

Bu orqali production muhit faqat PythonAnywhere oqimiga bog'langan.

## PythonAnywhere deploy (production)
Quyidagi misolda username: `<username>`, loyiha papkasi: `/home/<username>/real-estate-marketplace/backend`

1. Kodni serverga yuklang.
```bash
cd /home/<username>
git clone <your-repo-url> real-estate-marketplace
```

2. Virtualenv yarating va dependency o'rnating.
```bash
mkvirtualenv --python=/usr/bin/python3.12 rentora
pip install -r /home/<username>/real-estate-marketplace/backend/requirements/base.txt
```

3. `.env` tayyorlang.
```bash
cp /home/<username>/real-estate-marketplace/backend/.env.pythonanywhere.example /home/<username>/real-estate-marketplace/backend/.env
```
Keyin `.env` ichida faqat `<username>` ni o'zgartiring.

4. Migratsiya va static.
```bash
cd /home/<username>/real-estate-marketplace/backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

5. PythonAnywhere `Web` tab sozlamalari.
- `Source code`: `/home/<username>/real-estate-marketplace/backend`
- `Working directory`: `/home/<username>/real-estate-marketplace/backend`
- `Virtualenv`: `/home/<username>/.virtualenvs/rentora`

6. WSGI config (`/var/www/<username>_pythonanywhere_com_wsgi.py`) ichiga quyidagini qo'ying:
```python
import os
import sys

project_path = "/home/<username>/real-estate-marketplace/backend"
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("PYTHONANYWHERE_PROJECT_PATH", project_path)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

7. Static mapping:
- URL: `/static/` -> `/home/<username>/real-estate-marketplace/backend/staticfiles`
- URL: `/media/` -> `/home/<username>/real-estate-marketplace/backend/media`

8. `Reload` bosing.

## URLlar
- `/` - bosh sahifa
- `/properties/` - e'lonlar
- `/properties/<id>/` - e'lon tafsiloti
- `/properties/new/` - e'lon qo'shish
- `/login/`, `/register/`, `/logout/`
- `/admin/`
