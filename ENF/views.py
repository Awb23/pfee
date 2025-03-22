from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
import speech_recognition as sr
from difflib import SequenceMatcher
from .models import Category, Word, UserProgress, UserCategoryScore, UserProgressHistory, Paragraph
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)

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
    audio_feedback = None
    text_feedback = None
    similarity_score = None

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
            time_taken = float(request.POST.get('time_taken', '0.0'))
            
            # Handle text input
            text_input = request.POST.get('user_answer', '').strip().lower()
            text_similarity = calculate_text_similarity(text_input, current_word.name.lower())
            text_feedback = generate_text_feedback(text_input, current_word.name.lower(), text_similarity)
            
            # Handle audio input if available
            audio_similarity = 0
            if 'audio_data' in request.FILES:
                try:
                    logger.info("Audio data received in request.FILES")
                    audio_file = request.FILES['audio_data']
                    file_path = handle_uploaded_audio(audio_file)
                    audio_text = transcribe_audio(file_path)
                    logger.info(f"Transcribed audio text: {audio_text}")
                    audio_similarity = calculate_text_similarity(audio_text, current_word.name.lower())
                    audio_feedback = generate_audio_feedback(audio_text, current_word.name.lower(), audio_similarity)
                except Exception as e:
                    error_message = f"Erreur lors du traitement audio : {str(e)}"
                    logger.error(error_message)
                    audio_feedback = error_message  # Pass the error to the template
                finally:
                    if 'file_path' in locals() and os.path.exists(file_path):
                        os.remove(file_path)
            else:
                logger.info("No audio data found in request.FILES")
                audio_feedback = "Aucun audio détecté. Veuillez enregistrer votre prononciation et réessayer."
            
            # Determine if the answer is correct based on the highest similarity score
            similarity_score = max(text_similarity, audio_similarity)
            is_correct = similarity_score > 0.8

            if is_correct:
                progress.is_correct = True
                progress.attempts = 0
                progress.time_taken = time_taken
                progress.save()
                
                # Ajouter à l'historique
                UserProgress.objects.create(
                    user=request.user,
                    word=current_word,
                    time_taken=time_taken
                )
                
                user_score.score += 10
                user_score.save()
                message = "Correct ! 🎉 Passe au mot suivant."
            else:
                progress.attempts += 1
                progress.save()
                attempts = progress.attempts

                if progress.attempts >= 3:
                    # Réinitialiser tous les progrès pour cette catégorie et ce niveau
                    UserProgress.objects.filter(
                        user=request.user,
                        word__category=category,
                        word__level=level
                    ).delete()
                    
                    message = "Trop d'erreurs ! 😔 Tu dois recommencer cette catégorie."
                    return redirect('level_view', category_name=category.name, level=level)
                else:
                    message = f"Incorrect ! 😔 Il te reste {3 - progress.attempts} tentative(s)."

            completed_words = UserProgress.objects.filter(
                user=request.user,
                is_correct=True,
                word__in=words
            ).values_list('word_id', flat=True)

            current_word = next((word for word in words if word.id not in completed_words), None) if (is_correct or progress.attempts >= 3) else current_word

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
        'text_feedback': text_feedback,
        'audio_feedback': audio_feedback,
        'similarity_score': similarity_score,
        'audio_enabled': True,
    })

def handle_uploaded_audio(audio_file):
    """Save the uploaded audio file and convert it to WAV if necessary."""
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'audio_uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    temp_file_path = os.path.join(upload_dir, f"temp_{audio_file.name}")
    with open(temp_file_path, 'wb+') as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)

    try:
        audio = AudioSegment.from_file(temp_file_path)
        wav_file_path = os.path.join(upload_dir, f"{os.path.splitext(audio_file.name)[0]}.wav")
        audio.export(wav_file_path, format="wav")
        os.remove(temp_file_path)
        return wav_file_path
    except Exception as e:
        logger.error(f"Error during audio conversion: {e}")
        raise e  # Re-raise the exception to be caught in the calling function

def transcribe_audio(file_path):
    """Transcribe the audio file to text."""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language='ar-MA')
        return text.lower()
    except sr.UnknownValueError:
        logger.error("Speech could not be recognized.")
        raise Exception("Speech could not be recognized.")
    except sr.RequestError as e:
        logger.error(f"Error with the speech recognition API: {e}")
        raise Exception(f"Error with the speech recognition API: {e}")
    except Exception as e:
        logger.error(f"Audio transcription error: {e}")
        raise e

def calculate_text_similarity(text1, text2):
    """Calculate the similarity between two texts using SequenceMatcher."""
    if not text1 or not text2:
        return 0
    matcher = SequenceMatcher(None, text1, text2)
    return matcher.ratio()

def generate_text_feedback(user_input, target_word, similarity):
    """Generate detailed feedback on the user's text response."""
    if similarity > 0.9:
        return "Texte parfait ! Vous avez écrit le mot exactement comme demandé."
    elif similarity > 0.7:
        return f"Presque correct ! Vous avez écrit '{user_input}' au lieu de '{target_word}'. Vérifiez l'orthographe."
    elif similarity > 0.5:
        return f"Vous êtes sur la bonne voie. Vous avez écrit '{user_input}' mais le mot correct est '{target_word}'."
    else:
        return f"Votre réponse '{user_input}' est très différente du mot demandé '{target_word}'."

def generate_audio_feedback(transcribed_text, target_word, similarity):
    """Generate detailed feedback on the user's spoken response."""
    if not transcribed_text:
        return "Désolé, je n'ai pas pu comprendre votre prononciation. Veuillez réessayer."
    if similarity > 0.9:
        return f"Excellente prononciation ! J'ai entendu '{transcribed_text}'."
    elif similarity > 0.7:
        return f"Bonne prononciation ! J'ai entendu '{transcribed_text}' qui est proche de '{target_word}'."
    elif similarity > 0.5:
        return f"J'ai entendu '{transcribed_text}'. Essayez de prononcer '{target_word}' plus clairement."
    else:
        return f"J'ai entendu '{transcribed_text}' qui est différent de '{target_word}'. Veuillez réessayer."