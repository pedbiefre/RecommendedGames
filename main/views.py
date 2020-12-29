#encoding:utf-8
from main.models import Genero,Juego
from django.shortcuts import render,redirect
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime
import locale

#aqui hacemos el scraping web y cargamos datos a la bd
def populateDB():
    #contadores de registros
    num_generos = 0
    num_juegos = 0

    #vaciamos BD
    Genero.objects.all().delete()
    Juego.objects.all().delete()

    url="https://www.instant-gaming.com/es/juegos/steam/"
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url,headers=hdr)
    page = urlopen(req)
    s = BeautifulSoup(page,"lxml")
    
    all_link_juegos = s.find("div", class_= "search-wrapper").find("div",class_="search").findAll("div",class_="item")
    
    for juego in all_link_juegos:
        
        titulo = juego.find("div",class_="name").text    

        cover = juego.find("img",class_="picture")['src']
        
        price = juego.find("div",class_="price").text
        price= price.strip("\n").strip("€")

        link_juego= juego.find("a",class_="cover")['href']
        req=Request(link_juego,headers=hdr)
        page_juego=urlopen(req)
        s = BeautifulSoup(page_juego,"lxml")
        
        tags = s.find("div",class_="tags").find_all("a")
        tags = [tag.text for tag in tags]

        description= s.find("div",class_ ="description").text
        if(len(description)>=500):
            description = description[:495]+"[...]"

        release = s.find("div",class_="release").find("span").text
        # Idioma "es-ES" (código para el español de España)
        locale.setlocale(locale.LC_ALL, '') 
        release = datetime.strptime(release,'%d %B %Y')
        
        #almacenamos en BD
        lista_generos_obj = []
        for genero in tags:
            genero_obj,creado = Genero.objects.get_or_create(nombre=genero)
            lista_generos_obj.append(genero_obj)
            if creado:
                num_generos = num_generos+1
        
        j = Juego.objects.create(titulo=titulo,cover_path=cover,description=description,release=release,precio=price)
        
        for g in lista_generos_obj:
            j.generos.add(g)
        num_juegos = num_juegos + 1

        
    return ((num_juegos,num_generos))

#carga los datos desde la web en BD
def carga(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:
            num_juegos, num_generos = populateDB()
            mensaje = "Se han almacenado: " +str(num_juegos) + " juegos y " +str(num_generos)+ " géneros."
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")

    return render(request, 'confirmacion.html')

#muestra el número de juegos que hay en BD
def inicio(request):
    num_juegos = Juego.objects.all().count()
    return render(request,'inicio.html',{'num_juegos': num_juegos})

#devuelve la lista de juegos
def lista_juegos(request):
    juegos = Juego.objects.all()
    return render(request,'juegos.html',{'juegos':juegos})