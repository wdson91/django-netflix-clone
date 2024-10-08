from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Movie, MovieList
from django.contrib.auth.decorators import login_required,permission_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import re

# Create your views here.
#@login_required(login_url='login')
def index(request):
    movies = Movie.objects.all()
    featured_movie = movies[len(movies)-1]

    #genre_keys = [genre[0] for genre in Movie.GENRE_CHOICES]
    #genres=Movie.GENRE_CHOICES
    context = {
        'movies': movies,
        'featured_movie': featured_movie,

    }
    return render(request, 'movies.html', context)


@login_required(login_url='login')
def movie(request, pk):
    movie_uuid = pk
    movie_details = Movie.objects.get(uu_id=movie_uuid)

    context = {
        'movie_details': movie_details
    }

    return render(request, 'movie.html', context)

@login_required(login_url='login')
def genre(request, genre_key):
    print(genre_key)
    movies = Movie.objects.filter(genre=genre_key)

    context = {
         'movies': movies,
         'movie_genre': genre_key,
    }

    return render(request, 'genre.html', context)
# def genre(request, pk):
#     movie_genre = pk
#     movies = Movie.objects.filter(genre=movie_genre)

#     context = {
#         'movies': movies,
#         'movie_genre': movie_genre,
#     }
#     return render(request, 'genre.html', context)

@login_required(login_url='login')
def search(request):
    if request.method == 'POST':
        search_term = request.POST['search_term']
        movies = Movie.objects.filter(title__icontains=search_term)

        context = {
            'movies': movies,
            'search_term': search_term,
        }
        return render(request, 'search.html', context)
    else:
        return redirect('/')

#@permission_required('is_superuser',login_url='index')
@login_required(login_url='login')
def my_list(request):
    print(request.user.is_superuser)
    movie_list = MovieList.objects.filter(owner_user=request.user)
    user_movie_list = []

    for movie in movie_list:
        user_movie_list.append(movie.movie)

    context = {
        'movies': user_movie_list
    }
    return render(request, 'my_list.html', context)

@login_required(login_url='login')
def add_to_list(request):
    if request.method == 'POST':
        movie_url_id = request.POST.get('movie_id')
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern, movie_url_id)
        movie_id = match.group() if match else None

        movie = get_object_or_404(Movie, uu_id=movie_id)
        movie_list, created = MovieList.objects.get_or_create(owner_user=request.user, movie=movie)

        if created:
            response_data = {'status': 'success', 'message': 'Added ✓'}
        else:
            response_data = {'status': 'info', 'message': 'Movie already in list'}

        return JsonResponse(response_data)
    else:
        # return error
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('login')

    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # log user in
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                return redirect('/')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)

    response = redirect('login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'



    return redirect('login')



@login_required(login_url='login')
def user_profile(request,pk):
    user = request.user

        # Criar um dicionário com os campos desejados
    user_fields = {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }

    context = {
        'user': user_fields
    }

    return render(request, 'user_profile.html', context)


def atualizar_usuario(request):
    if request.method == 'POST':
        novo_email = request.POST.get('email')
        novo_username = request.POST.get('username')

        if User.objects.filter(email=novo_email).exists():
            messages.error(request, 'O email já está em uso.')
        elif User.objects.filter(username=novo_username).exists():
            messages.error(request, 'O nome de usuário já está em uso.')
        else:
            usuario = request.user
            usuario.email = novo_email
            usuario.username = novo_username
            usuario.save()
            messages.success(request, 'Dados atualizados com sucesso!')
            #return redirect('user_profile', pk=usuario.id)
            return redirect(f'user-profile/{usuario.id}', pk=usuario.id)

    return render(request, 'user_profile.html', {'user': request.user})
