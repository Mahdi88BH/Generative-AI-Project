import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ModernRegisterForm
from .models import Exam

# --- ACCUEIL & AUTH ---
def index_view(request):
    return render(request, "index.html")

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

# --- LOGIQUE D'ANALYSE HYBRIDE ---

@login_required(login_url='login')
def upload_view(request):
    history = Exam.objects.filter(user=request.user) # Le Meta ordering du modèle gère le tri
    
    if request.method == "POST" and request.FILES.get("exam_image"):
        # 1. RÉCUPÉRATION DES FICHIERS
        enonce = request.FILES.get("exam_image")
        corrige = request.FILES.get("corrige_file") # Optionnel
        copie = request.FILES.get("copie_file")     # Optionnel
        
        # 2. CRÉATION DE L'OBJET EN BASE
        # On détermine le mode avant l'envoi
        current_mode = 'grade' if (corrige and copie) else 'solve'
        
        exam = Exam.objects.create(
            user=request.user,
            image=enonce,
            corrige_file=corrige,
            copie_file=copie,
            mode=current_mode,
            status="Processing"
        )
        
        try:
            # 3. PRÉPARATION DE L'ENVOI À FASTAPI
            url_ai_engine = "http://127.0.0.1:8001/api/v1/process"
            
            # Construction dynamique du dictionnaire de fichiers
            files = {
                'enonce': (enonce.name, enonce.read(), enonce.content_type)
            }
            if corrige:
                files['corrige'] = (corrige.name, corrige.read(), corrige.content_type)
            if copie:
                files['copie'] = (copie.name, copie.read(), copie.content_type)
            
            # Appel API (Timeout de 180s pour laisser le temps au PDF multi-pages)
            response = requests.post(url_ai_engine, files=files, timeout=180)
            
            if response.status_code == 200:
                data = response.json()
                
                # On récupère soit le rapport (mode grade), soit la solution (mode solve)
                exam.result_text = data.get("rapport") or data.get("solution") or "Analyse terminée sans texte."
                exam.status = "Completed"
            else:
                exam.status = "Error"
                exam.result_text = f"Erreur Moteur IA : {response.text}"
                
        except requests.exceptions.Timeout:
            exam.status = "Error"
            exam.result_text = "Le traitement prend trop de temps (PDF volumineux ?)."
        except requests.exceptions.ConnectionError:
            exam.status = "Error"
            exam.result_text = "Moteur IA indisponible (Vérifiez main.py et mcp_server.py)."
        except Exception as e:
            exam.status = "Error"
            exam.result_text = f"Erreur système : {str(e)}"
        
        exam.save()
        return redirect('exam_detail', pk=exam.pk)
    
    return render(request, 'upload.html', {'exam_history': history})

# --- HISTORIQUE & DÉTAILS ---

@login_required(login_url='login')
def exam_detail_view(request, pk):
    exam = get_object_or_404(Exam, pk=pk, user=request.user)
    history = Exam.objects.filter(user=request.user)
    return render(request, 'upload.html', {'exam': exam, 'exam_history': history})

@login_required(login_url='login')
def delete_exam_view(request, pk):
    exam = get_object_or_404(Exam, pk=pk, user=request.user)
    if request.method == "POST":
        exam.delete()
    return redirect('upload')