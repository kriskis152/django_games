# 🎮 Django Game Portal

Платформа мини-игр на Django. Пользователи могут играть в игры и загружать свои собственные.

## Что реализовано

- **Змейка** — классическая игра на Canvas
- **Динозаврик** — прыжки через кактусы
- **Загрузка игр** — пользователи могут загружать свои JS-игры через форму
- **Таблица рекордов** — топ-10 для каждой игры
- **Авторизация** — только залогиненные могут загружать игры и сохранять рекорды

---

## Пошаговый гайд: создание проекта с нуля

### Шаг 1. Структура проекта

```
django_games/
├── game_portal/          # Главная директория проекта
│   ├── games/            # Приложение с играми
│   │   ├── migrations/   # Миграции базы данных
│   │   ├── templates/    # Шаблоны
│   │   │   └── games/    # Шаблоны игр
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py     # Модели Game и HighScore
│   │   ├── urls.py       # Маршруты приложения
│   │   └── views.py      # Представления
│   ├── static/           # Статические файлы
│   │   └── js/           # JS-файлы игр
│   ├── templates/        # Общие шаблоны
│   │   └── base.html     # Базовый шаблон
│   ├── settings.py       # Настройки Django
│   ├── urls.py           # Главные маршруты
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
├── requirements.txt
└── .gitignore
```

### Шаг 2. Создание Django-проекта и приложения

```bash
cd game_portal
python manage.py startproject game_portal .
python manage.py startapp games
```

### Шаг 3. Настройка settings.py

Ключевые моменты:

```python
# game_portal/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'games',  # Подключаем наше приложение
]

# Маршруты к шаблонам
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Папка с общими шаблонами
        'APP_DIRS': True,  # Django ищет шаблоны в apps/*/templates/
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Статические файлы (CSS, JS)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

### Шаг 4. Создание моделей

```python
# games/models.py

from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    """Модель игры. Хранит данные и JS-код."""
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    js_code = models.TextField(help_text="JavaScript код игры")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class HighScore(models.Model):
    """Модель для хранения рекордов."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='scores')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.IntegerField(default=0)
    achieved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return f"{self.user}: {self.score} in {self.game}"
```

Применяем миграции:

```bash
python manage.py makemigrations games
python manage.py migrate
```

### Шаг 5. Создание представлений (views)

```python
# games/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Game, HighScore
import json

def index(request):
    """Главная страница — список всех игр."""
    games = Game.objects.filter(is_published=True)
    return render(request, 'games/index.html', {'games': games})

def play_game(request, slug):
    """Страница игры с канвасом и отправкой рекордов."""
    game = get_object_or_404(Game, slug=slug, is_published=True)
    scores = game.scores.all()[:10]
    return render(request, 'games/play.html', {'game': game, 'scores': scores})

@login_required
def upload_game(request):
    """Форма загрузки новой игры."""
    if request.method == 'POST':
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        js_code = request.POST.get('js_code')
        
        if title and slug and js_code:
            Game.objects.create(
                title=title,
                slug=slug,
                js_code=js_code,
                author=request.user,
                is_published=True
            )
            return redirect('index')
    return render(request, 'games/upload.html')

@require_POST
@login_required
def submit_score(request, game_id):
    """API для отправки результата."""
    try:
        data = json.loads(request.body)
        score = data.get('score', 0)
        game = get_object_or_404(Game, pk=game_id)
        HighScore.objects.create(game=game, user=request.user, score=score)
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
```

### Шаг 6. Настройка маршрутов (urls)

```python
# game_portal/urls.py — главный файл

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='games/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('games.urls')),
]
```

```python
# games/urls.py — маршруты приложения

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('game/<slug:slug>/', views.play_game, name='play_game'),
    path('upload/', views.upload_game, name='upload_game'),
    path('api/score/<int:game_id>/', views.submit_score, name='submit_score'),
]
```

### Шаг 7. Создание шаблонов

Базовый шаблон:

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Game Portal{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #1a1a2e; color: #ffffff; }
        h1, h2, h3, h4, h5, h6 { color: #e94560; }
        .card { background-color: #16213e; border: 1px solid #e94560; }
        .card-title { color: #e94560; }
        .btn-primary { background-color: #e94560; border-color: #e94560; color: white; }
        .list-group-item { color: white; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #0f3460;">
        <div class="container">
            <a class="navbar-brand" href="{% url 'index' %}">🎮 Game Portal</a>
            <div class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                    <span class="nav-link text-light">Привет, {{ user.username }}!</span>
                    <a class="nav-link" href="{% url 'upload_game' %}">Загрузить игру</a>
                {% else %}
                    <a class="nav-link" href="{% url 'login' %}">Войти</a>
                {% endif %}
            </div>
        </div>
    </nav>
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

Список игр:

```html
<!-- games/templates/games/index.html -->
{% extends 'base.html' %}

{% block content %}
<h1 class="text-center mb-4">Добро пожаловать в Game Portal!</h1>
<div class="row">
    {% for game in games %}
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <div class="card-body d-flex flex-column">
                <h5 class="card-title">{{ game.title }}</h5>
                <p class="card-text flex-grow-1" style="color: #cccccc;">{{ game.description }}</p>
                <a href="{% url 'play_game' game.slug %}" class="btn btn-primary mt-auto">Играть</a>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
```

Страница игры:

```html
<!-- games/templates/games/play.html -->
{% extends 'base.html' %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <h2>{{ game.title }}</h2>
        <p>{{ game.description }}</p>
        <div id="game-container" style="border: 2px solid #e94560;">
            <canvas id="game-canvas"></canvas>
        </div>
        <button onclick="initGame()">🔄 Играть снова</button>
    </div>
    <div class="col-md-4">
        <h3>Топ 10</h3>
        <ul class="list-group">
            {% for score in scores %}
            <li class="list-group-item">{{ score.user|default:"Гость" }}: {{ score.score }}</li>
            {% empty %}
            <li class="list-group-item">Пока нет рекордов</li>
            {% endfor %}
        </ul>
    </div>
</div>

<script id="game-logic" type="text/plain">{{ game.js_code|safe }}</script>
<script>
function submitScore(finalScore) {
    {% if user.is_authenticated %}
    fetch('/api/score/{{ game.id }}/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': '{{ csrf_token }}'},
        body: JSON.stringify({score: finalScore})
    }).then(r => r.json()).then(d => location.reload());
    {% endif %}
}
function initGame() {
    const canvas = document.getElementById('game-canvas');
    const ctx = canvas.getContext('2d');
    const code = document.getElementById('game-logic').textContent;
    new Function('canvas', 'ctx', 'submitScore', code)(canvas, ctx, submitScore);
}
</script>
{% endblock %}
```

### Шаг 8. Написание JS-игр

Каждая игра — это JavaScript-код, который:
1. Использует переданные `canvas`, `ctx`, `submitScore`
2. Рисует на канвасе
3. Вызывает `submitScore(score)` при окончании

Пример простой игры:

```javascript
// Используем переданный canvas
canvas.width = 400;
canvas.height = 300;

let score = 0;

function gameLoop() {
    // Очистка
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Рисуем
    ctx.fillStyle = 'red';
    ctx.fillRect(score, 100, 50, 50);
    
    score += 5;
    
    if (score > canvas.width) {
        submitScore(score);
        return;
    }
    requestAnimationFrame(gameLoop);
}
gameLoop();
```

### Шаг 9. Запуск и тестирование

```bash
# Создаём суперпользователя
python manage.py createsuperuser

# Запускаем сервер
python manage.py runserver
```

Открываем http://127.0.0.1:8000/

---

## Как добавить новую игру

1. Заходим в админку `/admin/`
2. Нажимаем "Добавить Game"
3. Заполняем:
   - **title** — название
   - **slug** — уникальный идентификатор (латиница)
   - **description** — описание
   - **js_code** — JavaScript код игры
   - **is_published** — опубликовать
4. Сохраняем

Игра появится на главной странице!
