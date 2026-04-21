import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ModernRegisterForm
from .models import Exam

# --- NAVIGATION ---
def index_view(request):
    return render(request, "index.html")

# --- AUTHENTIFICATION ---
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
    return redirect('index')

# --- LOGIQUE D'ANALYSE (SYNERGIE IMAGE + TEXTE) ---

@login_required(login_url='login')
def upload_view(request):
    """
    Vue principale : Envoie l'image ET le contexte utilisateur à FastAPI.
    """
    history = Exam.objects.filter(user=request.user).order_by('-uploaded_at')
    
    if request.method == "POST" and request.FILES.get("exam_image"):
        uploaded_file = request.FILES["exam_image"]
        # Récupération du message de contexte saisi par l'utilisateur
        user_message = request.POST.get("user_message", "") 
        
        # 1. Sauvegarde en DB (On stocke aussi le prompt utilisateur pour l'historique)
        exam = Exam.objects.create(
            image=uploaded_file, 
            user=request.user, 
            status="Processing"
        )
        
        try:
            # 2. PRÉPARATION DE L'APPEL FASTAPI
            url_ai_engine = "http://127.0.0.1:8001/api/v1/solve"
            
            # Données textuelles (contexte)
            data_payload = {"user_context": user_message}
            
            with exam.image.open('rb') as f:
                files = {'file': (exam.image.name, f, 'image/jpeg')}
                
                # Envoi multipart : files pour l'image, data pour le texte
                response = requests.post(
                    url_ai_engine, 
                    files=files, 
                    data=data_payload, 
                    timeout=90
                )
            
            # 3. RÉCUPÉRATION DU RÉSULTAT
            if response.status_code == 200:
                data = response.json()
                exam.result_text = data.get("solution", "Aucune réponse générée.")
                exam.status = "Completed"
            else:
                exam.status = "Error"
                exam.result_text = f"Erreur Moteur IA (Code {response.status_code})"
                
        except requests.exceptions.ConnectionError:
            exam.status = "Error"
            exam.result_text = "Le service IA (Port 8001) est hors ligne."
        except Exception as e:
            exam.status = "Error"
            exam.result_text = f"Erreur système : {str(e)}"
        
        exam.save()
        return redirect('exam_detail', pk=exam.pk)
    
    return render(request, 'upload.html', {'exam_history': history})

# --- GESTION DE L'HISTORIQUE ---

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