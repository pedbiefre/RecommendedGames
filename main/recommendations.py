from main.models import Juego, Puntuacion, Genero
from collections import Counter
import shelve

def carga_similaridades():
    shelf= shelve.open('dataRS.dat')
    caracteristicas_juegos = caracterizar_juegos()
    caracteristicas_usuario = caracterizar_usuarios(caracteristicas_juegos)
    shelf['similarities'] = computar_similaridades(caracteristicas_juegos,caracteristicas_usuario)
    shelf.close

def recommend_games(user):
    shelf = shelve.open("dataRS.dat")
    res = []
    for game_id, score in shelf['similarities'][user]:
        game_title = Juego.objects.get(id=game_id).titulo
        res.append([game_title, 100 * score])
    shelf.close()
    return res

def computar_similaridades(juego_tags, usuario_tags):
    print("Computando la matriz de similaridad usuario-juegos")
    res = {}
    for u in usuario_tags:
        top_juegos = {}
        for j in juego_tags:
            top_juegos[j] = coeficiente_dice(usuario_tags[u],juego_tags[j])
        res[u] = Counter(top_juegos).most_common(8)
    return res

def caracterizar_juegos():
    print("Computando las caracteristicas de cada juego de la lista de juegos")
    juegos = {}
    #crear un diccionario de {juego_id: generos}
    for juego in Juego.objects.all():
        juego_id = juego.id
        
        generos = []
        aux = juego.generos.all()
        for gen in aux:
            genero=Genero.objects.get(id=gen.id).nombre
            generos.append(genero)

        juegos[juego_id] = generos
    return juegos

def caracterizar_usuarios(caracteristicas_juegos):
    print("Computando las caracteristicas de los juegos votados de cada usuario")
    usuarios={}
    #crear diccionario de {usuario_id: juego}
    for puntuacion in Puntuacion.objects.all():
        usuario = puntuacion.user.id
        juego_id = puntuacion.juego.id
        if juego_id in caracteristicas_juegos:
            usuarios.setdefault(usuario,{})
            usuarios[usuario][juego_id] = puntuacion.rating
    #me quedo con las mejores puntuaciones
    for u in usuarios:
        for juego, rating in Counter(usuarios[u]).most_common(5):
            usuarios[u] = [juego]
    #transformarlo en un dicionario de {usuario_id: generos}
    for u in usuarios:
        for juego in usuarios[u]:
            generos = []
            for genero in caracteristicas_juegos[juego]:
                generos.append(genero)
                usuarios[u]=set(generos)
    return usuarios

def coeficiente_dice(set1,set2):
    return 2 * len(set1.intersection(set2)) / (len(set1) + len(set2))