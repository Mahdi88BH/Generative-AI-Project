import requests  # Indispensable pour communiquer avec le port 8001
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ModernRegisterForm
from .models import Exam

# --- NOUVELLE VUE : PAGE D'ACCUEIL (LANDING PAGE) ---
def index_view(request):
    """
    Affiche la page d'accueil moderne (Nexus AI).
    Si l'utilisateur est déjà connecté, on peut le rediriger vers le dashboard,
    mais laisser l'accès à la landing page est standard.
    """
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
            # Redirige vers le dashboard d'upload après connexion
            return redirect("upload")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('index') # Redirection vers l'accueil après déconnexion

# --- LOGIQUE D'ANALYSE (MICROSERVICE) ---

@login_required(login_url='login')
def upload_view(request):
    """
    Vue principale du Dashboard (Upload d'examen).
    Communique avec le service FastAPI sur le port 8001.
    """
    history = Exam.objects.filter(user=request.user).order_by('-uploaded_at')
    
    if request.method == "POST" and request.FILES.get("exam_image"):
        uploaded_file = request.FILES["exam_image"]
        
        # 1. Création de l'entrée en base (Statut initial : Processing)
        exam = Exam.objects.create(
            image=uploaded_file, 
            user=request.user, 
            status="Processing"
        )
        
        try:
            # 2. APPEL AU MOTEUR IA (FASTAPI)
            url_ai_engine = "http://127.0.0.1:8001/api/v1/solve"
            
            with exam.image.open('rb') as f:
                # Préparation du fichier pour l'envoi HTTP multipart
                files = {'file': (exam.image.name, f, 'image/jpeg')}
                # Timeout long (120s) car Ollama/Llama 3 peut être lent au premier jet
                response = requests.post(url_ai_engine, files=files, timeout=120)
            
            # 3. TRAITEMENT DU RÉSULTAT
            if response.status_code == 200:
                data = response.json()
                # On récupère la solution extraite par l'agent IA
                exam.result_text = data.get("solution", "Aucune solution reçue.")
                exam.status = "Completed"
            else:
                exam.status = "Error"
                exam.result_text = f"Erreur Moteur IA ({response.status_code})"
                
        except requests.exceptions.ConnectionError:
            exam.status = "Error"
            exam.result_text = "Moteur IA indisponible. Lancez 'main.py' dans ai_engine (Port 8001)."
        except Exception as e:
            exam.status = "Error"
            exam.result_text = f"Erreur système : {str(e)}"
        
        exam.save()
        return redirect('exam_detail', pk=exam.pk)
    
    return render(request, 'upload.html', {'exam_history': history})

# --- GESTION DE L'HISTORIQUE ---

@login_required(login_url='login')
def exam_detail_view(request, pk):
    """Affiche les détails d'un examen passé."""
    exam = get_object_or_404(Exam, pk=pk, user=request.user)
    history = Exam.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'upload.html', {'exam': exam, 'exam_history': history})

@login_required(login_url='login')
def delete_exam_view(request, pk):
    """Supprime un examen de la base de données."""
    exam = get_object_or_404(Exam, pk=pk, user=request.user)
    if request.method == "POST":
        exam.delete()
    return redirect('upload')