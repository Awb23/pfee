from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from .models import Category, Word, Paragraph, UserProgress, UserCategoryScore

@login_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    user_scores = UserCategoryScore.objects.filter(user=request.user)

    completed_category_ids = UserProgress.objects.filter(user=request.user, is_correct=True).values_list('word__category', flat=True).distinct()
    completed_categories = Category.objects.filter(id__in=completed_category_ids)

    context = {
        'categories': categories,
        'user_scores': user_scores,
        'completed_categories': completed_categories,
    }
    return render(request, 'category.html', context)

@login_required
def next_word(request, category_name, level):
    category = get_object_or_404(Category, name=category_name)
    items = Word.objects.filter(category=category, level=level).order_by('id') if level in [1, 2] else Paragraph.objects.filter(category=category, level=level).order_by('id')

    completed_items = UserProgress.objects.filter(user=request.user, is_correct=True).values_list('word_id' if level in [1, 2] else 'paragraph_id', flat=True)

    remaining_items = items.exclude(id__in=completed_items)
    current_item = remaining_items.first()
    next_item = remaining_items[1] if remaining_items.count() > 1 else None

    return JsonResponse({
        'current': {
            'id': current_item.id if current_item else None,
            'text': getattr(current_item, 'name', None) if level in [1, 2] else getattr(current_item, 'text', None)
        },
        'next': {
            'id': next_item.id if next_item else None,
            'text': getattr(next_item, 'name', None) if level in [1, 2] else getattr(next_item, 'text', None)
        }
    })

from transformers import T5ForConditionalGeneration, T5Tokenizer

# Charger le modèle pré-entraîné T5 pour la correction orthographique






@login_required
def level_view(request, category_name, level=1):
    category = get_object_or_404(Category, name=category_name)

    if category.is_locked:
        return redirect('cat')

    words = Word.objects.filter(category=category, level=level).order_by('id')

    if not words.exists():
        return render(request, 'category_prod.html', {
            'category': category,
            'level': level,
            'user_score': 0,
            'total_words': 0,
            'completed_words': 0,
            'success_percentage': 0,
            'message': "Ma kaynch klamat hna."
        })

    completed_words = UserProgress.objects.filter(
        user=request.user,
        is_correct=True,
        word__in=words
    ).values_list('word_id', flat=True)

    current_word = next((word for word in words if word.id not in completed_words), None)
    attempts = 0
    message = None
    prediction = None
    completion = None

    if current_word:
        progress, _ = UserProgress.objects.get_or_create(
            user=request.user,
            word=current_word,
            defaults={'attempts': 0, 'is_correct': False}
        )
        attempts = progress.attempts

    if request.method == "POST":
        user_score, _ = UserCategoryScore.objects.get_or_create(user=request.user, category=category)

        if 'next_input' in request.POST and current_word:
            user_answer = request.POST.get('user_answer', '').strip().lower()
            time_taken = float(request.POST.get('time_taken', '0.0'))

            # Add prediction and completion
            

            is_correct = user_answer == current_word.name.lower()

            if is_correct:
                progress.is_correct = True
                progress.attempts = 0
                progress.time_taken = time_taken
                progress.save()
                user_score.score += 10
                user_score.save()
                message = "Correct ! 🎉 Passe au mot suivant."
            else:
                progress.attempts += 1
                progress.save()
                attempts = progress.attempts

                if progress.attempts >= 3:
                    progress.attempts = 0
                    progress.save()
                    message = "Trop d'erreurs ! 😔 On passe au mot suivant."
                else:
                    message = f"Incorrect ! 😔 Il te reste {3 - progress.attempts} tentative(s)."

            completed_words = UserProgress.objects.filter(
                user=request.user,
                is_correct=True,
                word__in=words
            ).values_list('word_id', flat=True)

            current_word = next((word for word in words if word.id not in completed_words), None) if (is_correct or progress.attempts >= 3) else current_word

        elif 'next_category' in request.POST and not current_word:
            total_words_count = words.count()
            correct_words_count = len(completed_words)
            success_percentage = (correct_words_count / total_words_count) * 100 if total_words_count > 0 else 0

            next_category = Category.objects.filter(name__gt=category_name).order_by('name').first()
            if next_category and next_category.is_locked:
                next_category.is_locked = False
                next_category.save()

            if success_percentage >= 80:
                return redirect('cat')
            else:
                message = f"Tu n'as atteint que {success_percentage:.0f}% de succès ! 😔 Tu dois avoir au moins 80% pour passer."

    user_score = UserCategoryScore.objects.filter(user=request.user, category=category).first()
    user_score_value = user_score.score if user_score else 0
    success_percentage = (len(completed_words) / words.count()) * 100 if words.count() > 0 else 0

    return render(request, 'category_prod.html', {
        'category': category,
        'level': level,
        'current_word': current_word,
        'user_score': user_score_value,
        'total_words': words.count(),
        'completed_words': len(completed_words),
        'success_percentage': success_percentage,
        'message': message,
        'attempts': attempts,
        'prediction': prediction,
        'completion': completion,
    })


