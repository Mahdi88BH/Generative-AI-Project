import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ModernRegisterForm
from .models import Exam

# --- NAVIGATION & AUTH ---
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

# --- ENGINE LOGIC (MICROSERVICE SYNC) ---

@login_required(login_url='login')
def upload_view(request):
    """
    Vue principale : Gère l'envoi vers FastAPI et l'affichage contextuel.
    """
    # Récupération de l'historique (ordonné par le Meta du modèle ou manuellement ici)
    history = Exam.objects.filter(user=request.user).order_by('-uploaded_at')
    
    if request.method == "POST" and request.FILES.get("exam_image"):
        enonce = request.FILES.get("exam_image")
        copie = request.FILES.get("copie_file") # Peut être None (Mode étudiant)
        
        # 1. Détermination du mode avant création
        mode_detecte = 'grade' if copie else 'solve'
        
        # 2. Création de l'entrée initiale
        exam = Exam.objects.create(
            user=request.user,
            image=enonce,
            copie_file=copie,
            mode=mode_detecte,
            status="Processing"
        )
        
        try:
            # 3. APPEL AU MOTEUR IA (Port 8001)
            url_ai = "http://127.0.0.1:8001/api/v1/process"
            
            # Préparation des fichiers pour FastAPI
            # .read() récupère le flux binaire du fichier en mémoire
            files = {
                'enonce': (enonce.name, enonce.read(), enonce.content_type)
            }
            if copie:
                files['copie'] = (copie.name, copie.read(), copie.content_type)

            # Timeout de 180s pour laisser le temps au traitement multi-pages
            response = requests.post(url_ai, files=files, timeout=180)
            
            if response.status_code == 200:
                data = response.json()
                
                # Récupération contextuelle du résultat selon le mode
                # FastAPI renvoie soit 'solution' soit 'rapport'
                exam.result_text = data.get("rapport") or data.get("solution")
                exam.status = "Completed"
            else:
                exam.status = "Error"
                exam.result_text = f"Erreur Moteur IA : {response.text}"
                
        except requests.exceptions.Timeout:
            exam.status = "Error"
            exam.result_text = "Le délai de traitement a expiré (Analyse complexe)."
        except requests.exceptions.ConnectionError:
            exam.status = "Error"
            exam.result_text = "Connexion impossible avec le moteur IA (Port 8001 fermé)."
        except Exception as e:
            exam.status = "Error"
            exam.result_text = f"Erreur système : {str(e)}"
        
        exam.save()
        return redirect('exam_detail', pk=exam.pk)
    
    return render(request, 'upload.html', {'exam_history': history})

# --- GESTION DE L'HISTORIQUE CONTEXTUEL ---

@login_required(login_url='login')
def exam_detail_view(request, pk):
    """
    Affiche un examen spécifique tout en maintenant la barre latérale d'historique.
    """
    exam = get_object_or_404(Exam, pk=pk, user=request.user)
    history = Exam.objects.filter(user=request.user).order_by('-uploaded_at')
    
    return render(request, 'upload.html', {
        'exam': exam, 
        'exam_history': history
    })

@login_required(login_url='login')
def delete_exam_view(request, pk):
    """Suppression d'un enregistrement."""
    exam = get_object_or_404(Exam, pk=pk, user=request.user)
    if request.method == "POST":
        exam.delete()
    return redirect('upload')