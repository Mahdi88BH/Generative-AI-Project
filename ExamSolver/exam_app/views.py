import requests  # CRUCIAL : à installer via 'pip install requests'
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ModernRegisterForm
from .models import Exam

# --- SUPPRESSION DES ANCIENS IMPORTS LOCAUX ---
# Plus besoin de extract_text_from_exam ni de exam_agent ici !

# --- AUTHENTIFICATION (Identique) ---
def register_view(request):
    if request.method == "POST":
        form = ModernRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("upload")
    else:
        form = ModernRegisterForm()
    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("upload")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- LOGIQUE DÉCOUPLÉE (VIA API REST) ---

@login_required(login_url='login')
def upload_view(request):
    history = Exam.objects.filter(user=request.user).order_by('-uploaded_at')
    
    if request.method == "POST" and request.FILES.get("exam_image"):
        uploaded_file = request.FILES["exam_image"]
        
        # 1. Création de l'entrée en base
        exam = Exam.objects.create(
            image=uploaded_file, 
            user=request.user, 
            status="Processing"
        )
        
        try:
            # 2. APPEL AU MOTEUR IA (MICROSERVICE FASTAPI)
            # On envoie le fichier ouvert directement au service tournant sur le port 8001
            url_ai_engine = "http://127.0.0.1:8001/api/v1/solve"
            
            with exam.image.open('rb') as f:
                files = {'file': (exam.image.name, f, 'image/jpeg')}
                response = requests.post(url_ai_engine, files=files, timeout=120) # Timeout long pour Ollama
            
            # 3. TRAITEMENT DE LA RÉPONSE JSON
            if response.status_code == 200:
                data = response.json()
                exam.result_text = data.get("solution", "Aucune solution reçue.")
                exam.status = "Completed"
            else:
                exam.status = "Error"
                exam.result_text = f"Erreur API ({response.status_code}): {response.text}"
                
        except requests.exceptions.ConnectionError:
            exam.status = "Error"
            exam.result_text = "Erreur : Impossible de contacter le moteur IA. Vérifiez que le service ai_engine est lancé sur le port 8001."
        except Exception as e:
            exam.status = "Error"
            exam.result_text = f"Erreur inattendue : {str(e)}"
        
        exam.save()
        return redirect('exam_detail', pk=exam.pk)
    
    return render(request, 'upload.html', {'exam_history': history})

# --- VUES DE DÉTAIL ET SUPPRESSION (Identiques) ---

@login_required(login_url='login')
def exam_detail_view(request, pk):
    exam = get_object_or_404(Exam, pk=pk, user=request.user)
    history = Exam.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'upload.html', {'exam': exam, 'exam_history': history})

@login_required(login_url='login')
def delete_exam_view(request, pk):
    exam = get_object_or_404(Exam, pk=pk, user=request.user)
    if request.method == "POST":
        exam.delete()
    return redirect('upload')