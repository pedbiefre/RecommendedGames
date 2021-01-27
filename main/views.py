#encoding:utf-8
from main.models import Genero,Juego
from django.shortcuts import render,redirect
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime
import locale, os, shutil
from whoosh.index import create_in,open_dir
from whoosh.fields import KEYWORD, Schema, TEXT, DATETIME, NUMERIC
from whoosh.qparser import QueryParser, SingleQuotePlugin
from whoosh import qparser
from main.forms import BusquedaPorTituloForm, BusquedaPorGeneroForm, BusquedaPorFechaForm

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
    juegos=[]
    for juego in all_link_juegos:
        
        title = juego.find("div",class_="name").text    

        cover = juego.find("img",class_="picture")['src']
        
        price = juego.find("div",class_="price").text
        price= price.strip("\n").strip("€")

        link_juego= juego.find("a",class_="cover")['href']
        req=Request(link_juego,headers=hdr)
        page_juego=urlopen(req)
        s = BeautifulSoup(page_juego,"lxml")
        
        tags = s.find("div",class_="tags").find_all("a")
        tags = [tag.text for tag in tags]

        try:
            description= s.find("div",class_ ="description").text
        except:
            description="Este juego no dispone de descripción"

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
        
        j = Juego.objects.create(titulo=title,cover_path=cover,description=description,release=release,precio=price)
        juegos.append((title,cover,description,release,price,tags))
        
        for g in lista_generos_obj:
            j.generos.add(g)
        num_juegos = num_juegos + 1

        
    return ((num_juegos,num_generos,juegos))

#carga los datos desde la web en BD
def carga(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:
            schem = Schema(titulo=TEXT(stored=True),caratula=TEXT(stored=True),descripcion=TEXT(stored=True),
            release=DATETIME(stored=True),precio=NUMERIC(stored=True),generos=KEYWORD(stored=True,scorable=True,commas=True))

            #si existe indice, eliminamos
            if(os.path.exists("Index")):
                shutil.rmtree("Index")
            os.mkdir("Index")

            ix = create_in("Index",schema=schem)

            writer = ix.writer()
            i=0
            num_juegos, num_generos,juegos = populateDB()
            
            for juego in juegos:
                print(juego[5])
                writer.add_document(titulo=str(juego[0]),caratula=juego[1],descripcion=juego[2],
                release=juego[3],precio=float(juego[4]),generos=str(",".join(juego[5])))
                i= i + 1
            writer.commit()

            print("Se han indexado "+ str(i) +" juegos en el índice de whoosh.")
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

#Busca un listado de juegos con el titulo introducido usando whoosh
def buscar_juegoportitulo(request):
    formulario = BusquedaPorTituloForm()
    juegos=None
    if request.method == 'POST':
        formulario = BusquedaPorTituloForm(request.POST)
        if formulario.is_valid():
            ix = open_dir("Index")
            with ix.searcher() as searcher:
                query = QueryParser("titulo",ix.schema).parse(formulario.cleaned_data['titulo'])
                result = searcher.search(query)
                juegos=[]
                for r in result:
                    aux={"titulo": r["titulo"],"caratula":r["caratula"],"descripcion":r["descripcion"]
                    ,"release":r["release"],"precio":r["precio"],"generos":r["generos"]}
                    juegos.append(aux)
    
    return render(request, 'juegobusquedaportitulo.html', {'formulario':formulario, 'juegos':juegos})

#Busca juegos por genero usando whoosh
def buscar_juegosporgenero(request):
    formulario = BusquedaPorGeneroForm()
    juego=[]
    
    if request.method=='POST':
        formulario = BusquedaPorGeneroForm(request.POST)      
        if formulario.is_valid():
            ix = open_dir("Index")
            with ix.searcher() as searcher:

                query_gen="'"
                cont = len(formulario.cleaned_data['genero'])
                for id_gen in formulario.cleaned_data['genero']:
                    genero=Genero.objects.get(id=id_gen).nombre
                    if(cont==1):
                        query_gen += genero+"'"
                    else:
                        query_gen += genero + "' '"
                    cont = cont-1

                query = QueryParser("generos",ix.schema,plugins=[SingleQuotePlugin]).parse(query_gen)
                result = searcher.search(query)
                for r in result:
                    aux={"titulo": r["titulo"],"caratula":r["caratula"],"descripcion":r["descripcion"]
                    ,"release":r["release"],"precio":r["precio"],"generos":r["generos"]}
                    juego.append(aux)
            
    return render(request, 'juegosbusquedaporgenero.html', {'formulario':formulario, 'juegos':juego})

#Busqueda juegos por fecha usando whoosh
def buscar_juegosporfecha(request):
    formulario = BusquedaPorFechaForm()
    juegos=[]
    if request.method == 'POST':
        formulario = BusquedaPorFechaForm(request.POST)
        if formulario.is_valid():
            fecha_inicio = formulario.cleaned_data['fecha_inicio']
            fecha_fin = formulario.cleaned_data['fecha_fin']
            myquery ='{'+ str(fecha_inicio) + 'TO'+ str(fecha_fin) + ']' 
            ix = open_dir("Index")
            with ix.searcher() as searcher:
                query = QueryParser("release",ix.schema).parse(myquery)
                result = searcher.search(query,limit=200)
                juegos=[]
                for r in result:
                    aux={"titulo": r["titulo"],"caratula":r["caratula"],"descripcion":r["descripcion"]
                    ,"release":r["release"],"precio":r["precio"],"generos":r["generos"]}
                    juegos.append(aux)
    
    return render(request, 'juegosbusquedaporfecha.html', {'formulario':formulario, 'juegos':juegos})

