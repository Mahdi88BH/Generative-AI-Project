from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ModernRegisterForm
from .models import Exam
from .ocr_engine import extract_text_from_exam 
from .agent import exam_agent  # Importation de l'agent IA conçu précédemment

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

# --- CRUD EXAMENS (AVEC INTELLIGENCE AGENTIQUE) ---

@login_required(login_url='login')
def upload_view(request):
    history = Exam.objects.filter(user=request.user).order_by('-uploaded_at')
    
    if request.method == "POST" and request.FILES.get("exam_image"):
        uploaded_file = request.FILES["exam_image"]
        
        # 1. Création de l'entrée en base (Statut : En cours)
        exam = Exam.objects.create(
            image=uploaded_file, 
            user=request.user, 
            status="Processing"
        )
        
        try:
            # 2. VISION : Extraction du texte brut via Tesseract/OpenCV
            raw_text = extract_text_from_exam(exam.image.path)
            
            # 3. AGENT IA : Résolution via LangGraph
            # On envoie le texte brut à l'agent qui va nettoyer et résoudre
            inputs = {"raw_text": raw_text}
            result = exam_agent.invoke(inputs)
            
            # 4. SAUVEGARDE : On stocke la solution finale générée par l'agent
            exam.result_text = result["solution"]
            exam.status = "Completed"
            exam.save()
            
        except Exception as e:
            exam.result_text = f"Désolé, une erreur est survenue lors de l'analyse : {str(e)}"
            exam.status = "Error"
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