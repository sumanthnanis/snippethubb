from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Snippet
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from openai import OpenAI
from django.http import JsonResponse
from django.conf import settings
import json

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')  
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, email=email, password=password)
                messages.success(request, "Account created successfully!")
                return redirect('login')
            else:
                messages.error(request, "Username already exists")
        else:
            messages.error(request, "Passwords do not match")
    return render(request, 'accounts/register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def home(request):
    # Get query parameters
    query = request.GET.get('search', '')
    language_filter = request.GET.get('language', '')
    recent = request.GET.get('recent', False)
    my_snippets = request.GET.get('my_snippets', False)

    # Base query for public snippets
    snippets = Snippet.objects.filter(visibility='public')

    # Apply search filter
    if query:
        snippets = snippets.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(language__icontains=query) |
            Q(tags__icontains=query)
        )

    # Apply language filter
    if language_filter:
        snippets = snippets.filter(language__iexact=language_filter)

    # Handle recent snippets
    if recent:
        snippets = snippets.order_by('-created_at')[:10]  # Fetch the 10 most recent snippets

    # Handle my snippets (if user is logged in)
    if my_snippets and request.user.is_authenticated:
        snippets = Snippet.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'accounts/home.html', {
        'snippets': snippets,
        'query': query,
        'language_filter': language_filter,
    })


@login_required
def add_snippet(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        language = request.POST['language']
        tags = request.POST['tags']
        code = request.POST['code']
        visibility = request.POST['visibility']

        snippet = Snippet(
            user=request.user,
            title=title,
            description=description,
            language=language,
            tags=tags,
            code=code,
            visibility=visibility,
        )
        snippet.save()
        messages.success(request, "Snippet added successfully!")
        return redirect('home')
    return render(request, 'accounts/add_snippet.html')


def ai_view(request):
    if request.method == 'POST':
        data = json.loads(request.body).get('message', '')

        client = OpenAI(api_key=settings.API_KEY)

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. "},
                {"role": "user", "content": f"{data}"}
            ]
        )

        result = completion.choices[0].message
        text = result.content
        final = text.replace("*","")

        return JsonResponse({'response': final})

    return JsonResponse({'error': 'Invalid request'}, status=400)