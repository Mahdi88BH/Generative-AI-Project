import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ModernRegisterForm
from .models import Exam

# --- NAVIGATION & AUTH ---
def index_view(request): return render(request, "index.html")

def register_view(request):
    if request.method == "POST":
        form = ModernRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(); login(request, user)
            return redirect("upload")
    else: form = ModernRegisterForm()
    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user(); login(request, user)
            return redirect("upload")
    else: form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request); return redirect('index')

# --- LOGIQUE D'ANALYSE & CHAT INTERACTIF ---

@login_required(login_url='login')
def upload_view(request, pk=None):
    """
    Vue centrale gérant le flux :
    1. Scan Initial (Image/PDF + Message)
    2. Discussion de correction (Message seul)
    """
    history = Exam.objects.filter(user=request.user).order_by('-uploaded_at')
    exam = get_object_or_404(Exam, pk=pk, user=request.user) if pk else None

    if request.method == "POST":
        user_message = request.POST.get("user_message", "")
        uploaded_file = request.FILES.get("exam_image")

        # CAS 1 : NOUVEL EXAMEN
        if uploaded_file:
            exam = Exam.objects.create(
                image=uploaded_file, user=request.user, status="Processing"
            )
            data_payload = {"user_context": user_message}
            files = {'file': (exam.image.name, exam.image.open('rb'))}
        
        # CAS 2 : CHAT SUR EXAMEN EXISTANT
        elif exam:
            exam.status = "Processing"; exam.save()
            data_payload = {
                "user_context": user_message,
                "existing_solution": exam.result_text # Mémoire pour l'IA
            }
            files = None # Pas de nouvelle image

        else: return redirect('upload')

        # Appel FastAPI
        try:
            url_ai_engine = "http://127.0.0.1:8001/api/v1/solve"
            if files:
                response = requests.post(url_ai_engine, files=files, data=data_payload, timeout=90)
            else:
                response = requests.post(url_ai_engine, data=data_payload, timeout=90)

            if response.status_code == 200:
                data = response.json()
                exam.result_text = data.get("solution", "Erreur moteur.")
                exam.status = "Completed"
            else:
                exam.status = "Error"
                exam.result_text = f"Erreur IA (Code {response.status_code})"
                
        except Exception as e:
            exam.status = "Error"
            exam.result_text = f"Erreur système : {str(e)}"
        
        exam.save()
        return redirect('exam_detail', pk=exam.pk)
    
    return render(request, 'upload.html', {'exam': exam, 'exam_history': history})

@login_required(login_url='login')
def exam_detail_view(request, pk):
    # Redirige vers la vue upload avec le contexte de l'examen chargé
    return upload_view(request, pk=pk)

@login_required(login_url='login')
def delete_exam_view(request, pk):
    exam = get_object_or_404(Exam, pk=pk, user=request.user)
    if request.method == "POST": exam.delete()
    return redirect('upload')