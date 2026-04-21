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

# --- ENGINE LOGIC (MULTI-IMAGE SYNC) ---

@login_required(login_url='login')
def upload_view(request):
    """
    Gère l'envoi d'un énoncé et de plusieurs images de copies vers FastAPI.
    """
    history = Exam.objects.filter(user=request.user).order_by('-uploaded_at')
    
    if request.method == "POST" and request.FILES.get("exam_image"):
        enonce = request.FILES.get("exam_image")
        # On récupère une liste de fichiers pour 'copie_file'
        copies = request.FILES.getlist("copie_file") 

        # 1. Détermination du mode
        mode_detecte = 'grade' if copies else 'solve'
        
        # 2. Création de l'objet (On ne stocke qu'une image de référence en DB pour l'aperçu)
        exam = Exam.objects.create(
            user=request.user,
            image=enonce,
            mode=mode_detecte,
            status="Processing"
        )
        
        try:
            url_ai = "http://127.0.0.1:8001/api/v1/process"
            
            # 3. PRÉPARATION MULTI-PART AVEC PLUSIEURS IMAGES
            # FastAPI attend une liste pour le champ 'copie'
            files = [
                ('enonce', (enonce.name, enonce.read(), enonce.content_type))
            ]
            
            # Ajout de chaque image de copie à la liste des fichiers
            for img in copies:
                # On remet le pointeur au début si nécessaire, ou on utilise .read() directement
                files.append(('copie', (img.name, img.read(), img.content_type)))

            # Timeout de 180s pour laisser le temps à l'OCR de traiter chaque image
            response = requests.post(url_ai, files=files, timeout=180)
            
            if response.status_code == 200:
                data = response.json()
                exam.result_text = data.get("rapport") or data.get("solution")
                exam.status = "Completed"
            else:
                exam.status = "Error"
                exam.result_text = f"Erreur Moteur IA : {response.text}"
                
        except requests.exceptions.Timeout:
            exam.status = "Error"
            exam.result_text = "Délai expiré : l'analyse multi-images prend du temps."
        except Exception as e:
            exam.status = "Error"
            exam.result_text = f"Erreur système : {str(e)}"
        
        exam.save()
        return redirect('exam_detail', pk=exam.pk)
    
    return render(request, 'upload.html', {'exam_history': history})

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