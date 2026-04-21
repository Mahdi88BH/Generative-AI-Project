import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ModernRegisterForm
from .models import Exam

def index_view(request): return render(request, "index.html")

def register_view(request):
    if request.method == "POST":
        form = ModernRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("upload")
    else: form = ModernRegisterForm()
    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("upload")
    else: form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required(login_url='login')
def upload_view(request):
    history = Exam.objects.filter(user=request.user).order_by('-uploaded_at')
    
    if request.method == "POST" and request.FILES.getlist("exam_image"):
        enonces = request.FILES.getlist("exam_image")
        copies = request.FILES.getlist("copie_file") 

        # Si 'copies' n'est pas vide, on passe en mode prof
        mode_detecte = 'grade' if copies else 'solve'
        
        # On sauvegarde le premier énoncé pour l'aperçu dans l'historique
        exam = Exam.objects.create(
            user=request.user,
            image=enonces[0],
            mode=mode_detecte,
            status="Processing"
        )
        
        try:
            url_ai = "http://127.0.0.1:8001/api/v1/process"
            
            # Préparation des fichiers en liste de tuples (clé_fastapi, (nom, binaire, type))
            files = []
            for img in enonces:
                files.append(('enonce', (img.name, img.read(), img.content_type)))
            
            for img in copies:
                files.append(('copie', (img.name, img.read(), img.content_type)))

            # Timeout long pour laisser l'OCR traiter de nombreuses images
            response = requests.post(url_ai, files=files, timeout=240)
            
            if response.status_code == 200:
                data = response.json()
                exam.result_text = data.get("rapport") or data.get("solution")
                exam.status = "Completed"
            else:
                exam.status = "Error"
                exam.result_text = f"Erreur Moteur IA : {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            exam.status = "Error"
            exam.result_text = "Le délai de traitement a expiré (trop d'images)."
        except Exception as e:
            exam.status = "Error"
            exam.result_text = f"Erreur de connexion : {str(e)}"
        
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