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

# --- LOGIQUE D'ANALYSE (SYNCHRONISÉE AVEC AI ENGINE) ---

@login_required(login_url='login')
def upload_view(request):
    """
    Vue principale communiquant avec FastAPI (Port 8001).
    """
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
            # 2. APPEL AU MOTEUR IA
            url_ai_engine = "http://127.0.0.1:8001/api/v1/solve"
            
            with exam.image.open('rb') as f:
                files = {'file': (exam.image.name, f, 'image/jpeg')}
                # On garde un timeout large car le Llama 70B sur Groq + MCP 
                # peut prendre quelques secondes
                response = requests.post(url_ai_engine, files=files, timeout=120)
            
            # 3. TRAITEMENT DU RÉSULTAT
            if response.status_code == 200:
                data = response.json()
                
                # RÉCUPÉRATION DES DEUX INFOS (OCR + SOLUTION)
                # Il est intéressant de stocker aussi l'OCR brut si ton modèle le permet
                exam.result_text = data.get("solution", "Aucune solution reçue.")
                
                # Optionnel : Tu pourrais ajouter un champ ocr_text à ton modèle Exam
                # exam.ocr_text = data.get("ocr_extracted") 
                
                exam.status = "Completed"
            else:
                exam.status = "Error"
                exam.result_text = f"Erreur du moteur IA : {response.text}"
                
        except requests.exceptions.ConnectionError:
            exam.status = "Error"
            exam.result_text = "Connexion refusée. Vérifiez que 'main.py' et 'mcp_server.py' sont lancés."
        except Exception as e:
            exam.status = "Error"
            exam.result_text = f"Erreur système : {str(e)}"
        
        exam.save()
        return redirect('exam_detail', pk=exam.pk)
    
    return render(request, 'upload.html', {'exam_history': history})

# --- HISTORIQUE ---

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