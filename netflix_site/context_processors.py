
from core.models import Movie


def genres_processor(request):
    genres = Movie.GENRE_CHOICES
    return {
        'genres': genres
    }
