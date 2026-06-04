from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Game, HighScore
import json

def index(request):
    games = Game.objects.filter(is_published=True)
    return render(request, 'games/index.html', {'games': games})

def play_game(request, slug):
    game = get_object_or_404(Game, slug=slug, is_published=True)
    scores = game.scores.all()[:10]
    return render(request, 'games/play.html', {'game': game, 'scores': scores})

@login_required
def upload_game(request):
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
    try:
        data = json.loads(request.body)
        score = data.get('score', 0)
        game = get_object_or_404(Game, pk=game_id)
        
        HighScore.objects.create(
            game=game,
            user=request.user,
            score=score
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
