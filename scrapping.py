#encoding:utf-8

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import sqlite3

def extraer_juegos():
    url="https://www.instant-gaming.com/es/juegos/steam/"
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url,headers=hdr)
    page = urlopen(req)
    s = BeautifulSoup(page,"lxml")
    
    juegos = s.find("div", class_= "search-wrapper").find("div",class_="search").findAll("div",class_="item")
    titulos = []
    for juego in juegos:
        titulo = juego.find("a", class_="cover").find("img").get("title")
        titulos.append(titulo)
    return titulos

if __name__ == "__main__":
    print(extraer_juegos())