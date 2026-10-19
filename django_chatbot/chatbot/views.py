import json
import os
import threading
import time
import numpy as np
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from .models import Chat
from tensorflow.keras.models import load_model
import cv2
from google import genai
from gtts import gTTS

# ---------------- Gemini API ----------------
GEMINI_KEY = "AIzaSyA-0dC73c__QsOEe3gBollLmnzZlBcKDyM"
DEFAULT_MODEL = "gemini-1.5"
client = genai.Client(api_key=GEMINI_KEY)
available_models = [m.name for m in client.models.list()]

JSON_PATH = os.path.join(os.path.dirname(__file__), "data", "fils.json")
AUDIO_PATH = os.path.join(os.path.dirname(__file__), "media", "audio")

# ---------------- Gemini Query ----------------
def ask_openai(message: str) -> str:
    try:
        model_name = DEFAULT_MODEL
        if DEFAULT_MODEL not in available_models and available_models:
            model_name = available_models[0]

        response = client.models.generate_content(
            model=model_name,
            contents=[{"role": "user", "parts": [{"text": message}]}]
        )
        if hasattr(response, "candidates") and response.candidates:
            return response.candidates[0].content.parts[0].text
        return str(response)
    except Exception as e:
        print("Gemini API Error:", e)
        return f"⚠️ Erreur API Gemini: {e}"

# ---------------- JSON Utils ----------------
def load_json():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(data):
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ---------------- Text-to-Speech ----------------
def text_to_speech(text, filename=None):
    if not filename:
        filename = f"response_{int(time.time())}.mp3"
    os.makedirs(AUDIO_PATH, exist_ok=True)
    audio_file = os.path.join(AUDIO_PATH, filename)
    tts = gTTS(text=text, lang='ar')
    tts.save(audio_file)
    return f"/media/audio/{filename}"  # frontend

# ---------------- Chatbot Pages ----------------
@login_required(login_url='login')
def chatbot_page(request):
    chats = request.session.get('chat_history', [])
    return render(request, 'chatbot.html', {'chats': chats})

@login_required(login_url='login')
def chatbot_json(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)
    
    data = json.loads(request.body)
    question = data.get("message", "").strip()
    qna = load_json()
    answer = qna.get(question) or ask_openai(question)
    if question not in qna:
        qna[question] = answer
        save_json(qna)

    chat_entry = {
        'user': {'username': request.user.username},
        'message': question,
        'response': answer,
        'created_at': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    chat_history = request.session.get('chat_history', [])
    chat_history.append(chat_entry)
    request.session['chat_history'] = chat_history

    Chat.objects.create(user=request.user, message=question, response=answer, created_at=timezone.now())
    return JsonResponse({"message": question, "response": answer})

@login_required(login_url='login')
def new_chat(request):
  
    request.session['chat_history'] = []
    return redirect('chatbot_page')

# ---------------- Chat History ----------------
@login_required(login_url='login')
def chat_history(request):
    query = request.GET.get('q', '')
    chats = Chat.objects.filter(user=request.user).order_by('-created_at')
    if query:
        chats = chats.filter(Q(message__icontains=query) | Q(response__icontains=query))

    chats_grouped = {}
    for chat in chats:
        day = chat.created_at.date()
        chats_grouped.setdefault(day, []).append(chat)

    days_list = [
        {'date': day, 'summary': getattr(day_chats[0], 'summary_name', None) or day_chats[0].message, 'chats': day_chats}
        for day, day_chats in chats_grouped.items()
    ]
    return render(request, 'history.html', {'days_list': days_list, 'query': query})

@login_required(login_url='login')
def delete_day(request, day_date):
    if request.method == "POST":
        date_obj = parse_date(day_date)
        Chat.objects.filter(user=request.user, created_at__date=date_obj).delete()
        messages.success(request, f"تم حذف رسائل يوم {day_date}")
    return redirect('chat_history')

@login_required(login_url='login')
def rename_day(request, day_date):
    if request.method == "POST":
        new_name = request.POST.get('new_name', '').strip()
        if new_name:
            date_obj = parse_date(day_date)
            chats = Chat.objects.filter(user=request.user, created_at__date=date_obj).order_by('created_at')
            if chats.exists():
                first_chat = chats.first()
                first_chat.summary_name = new_name
                first_chat.save()
            messages.success(request, f"تم إعادة تسمية يوم {day_date} إلى {new_name}")
    return redirect('chat_history')

# ---------------- Auth ----------------
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def login_view(request):
    error_message = None

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)

            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )

            if user is not None:
                login(request, user)
                return redirect('welcome')
            else:
                error_message = "Email ou mot de passe incorrect"

        except User.DoesNotExist:
            error_message = "Email ou mot de passe incorrect"

    return render(request, 'login.html', {
        'error_message': error_message
    })
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

       
        if password1 != password2:
            return render(request, 'register.html', {'error_message': 'Les mots de passe ne correspondent pas'})

       
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error_message': 'Nom d\'utilisateur déjà utilisé'})

        
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error_message': 'Email déjà utilisé'})

      
        user = User.objects.create_user(username=username, email=email, password=password1)
        auth.login(request, user)

        return redirect('aa')

    return render(request, 'register.html')
def profile_view(request):
    user = request.user

    if request.method == 'POST':

        # ✅ Change username
        if 'update_name' in request.POST:
            new_username = request.POST.get('username')
            user.username = new_username
            user.save()
            messages.success(request, "Nom modifié avec succès")
            return redirect('profile')

        # ✅ Change password
        elif 'update_password' in request.POST:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')

            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                auth.login(request, user)  
                messages.success(request, "Mot de passe changé")
            else:
                messages.error(request, "Ancien mot de passe incorrect")

            return redirect('profile')

        # ❌ Delete account
        elif 'delete_account' in request.POST:
            user.delete()
            return redirect('home')

    return render(request, 'profile.html')
def aa_view(request):
    return render(request, 'aa.html') 
def welcome_view(request):
    return render(request, 'welcome.html')  #
def logout_view(request):
    auth.logout(request)
    return render(request, 'bye.html')
def bye_view(request):
    return render(request, 'bye.html')
@login_required(login_url='login')
def account_page(request):
    return render(request, 'account.html')

def home(request):
    return render(request, 'home.html')

# ---------------- Sign Language ----------------
SIGN_MODEL_PATH = os.path.join(os.path.dirname(__file__), "sign_model", "model.keras")
if os.path.exists(SIGN_MODEL_PATH):
    sign_model = load_model(SIGN_MODEL_PATH)
    GESTURES = ["hello", "help", "yes", "no", "thanks"]
else:
    sign_model = None
    GESTURES = []

@csrf_exempt
@login_required(login_url='login')
def predict_sign(request):
    if not sign_model:
        return JsonResponse({"error": "Model not found"}, status=404)
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=405)

    data = json.loads(request.body)
    landmarks = data.get("landmarks", [])
    if not landmarks:
        return JsonResponse({"error": "لم يتم استلام المعالم"}, status=400)

    coords = np.array(landmarks).reshape(1, -1)
    prediction = sign_model.predict(coords)
    gesture = GESTURES[prediction.argmax()]

    qna = load_json()
    answer = qna.get(gesture) or ask_openai(gesture)
    if gesture not in qna:
        qna[gesture] = answer
        save_json(qna)

    audio_url = text_to_speech(answer)
    chat_entry = {
        'user': {'username': request.user.username},
        'message': gesture,
        'response': answer,
        'created_at': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    chat_history = request.session.get('chat_history', [])
    chat_history.append(chat_entry)
    request.session['chat_history'] = chat_history

    Chat.objects.create(user=request.user, message=gesture, response=answer, created_at=timezone.now())
    return JsonResponse({"gesture": gesture, "response": answer, "audio": audio_url})

@csrf_exempt
@login_required(login_url='login')
def live_gesture(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=405)

    data = json.loads(request.body)
    gesture = data.get("gesture", "")
    if not gesture:
        return JsonResponse({"error": "لم يتم استلام الإشارة"}, status=400)

    qna = load_json()
    answer = qna.get(gesture) or ask_openai(gesture)
    if gesture not in qna:
        qna[gesture] = answer
        save_json(qna)

    audio_url = text_to_speech(answer)
    chat_entry = {
        'user': {'username': request.user.username},
        'message': gesture,
        'response': answer,
        'created_at': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    chat_history = request.session.get('chat_history', [])
    chat_history.append(chat_entry)
    request.session['chat_history'] = chat_history

    Chat.objects.create(user=request.user, message=gesture, response=answer, created_at=timezone.now())
    return JsonResponse({"gesture": gesture, "response": answer, "audio": audio_url})

# ---------------- Live Camera ----------------
def start_live_camera(user):
    if not sign_model:
        return
    cap = cv2.VideoCapture(0)
    prev_gesture = None
    qna = load_json()
    while True:
        ret, frame = cap.read()
        if not ret: continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_resized = cv2.resize(gray, (63, 1))
        data = gray_resized.reshape(1, 63, 1) / 255.0
        pred = sign_model.predict(data, verbose=0)
        gesture = GESTURES[pred.argmax()]
        if gesture != prev_gesture:
            answer = qna.get(gesture) or ask_openai(gesture)
            if gesture not in qna:
                qna[gesture] = answer
                save_json(qna)
            Chat.objects.create(user=user, message=gesture, response=answer, created_at=timezone.now())
            prev_gesture = gesture
        time.sleep(0.1)
    cap.release()
from django.shortcuts import render

def password_reset_view(request):
    return render(request, 'motdepasse_oublie.html')
@login_required(login_url='login')
def start_live_camera_view(request):
    threading.Thread(target=start_live_camera, args=(request.user,), daemon=True).start()
    messages.success(request, "تم بدء التعرف على الإشارات الحية!")
    return redirect('chatbot_page')