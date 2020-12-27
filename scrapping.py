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
    
    all_link_juegos = s.find("div", class_= "search-wrapper").find("div",class_="search").findAll("div",class_="item")
    
    juegos = []
    
    for juego in all_link_juegos:
        
        titulo = juego.find("div",class_="name").text    

        cover = juego.find("img",class_="picture")['src']
        
        price = juego.find("div",class_="price").text
        price= price.strip("\n")

        link_juego= juego.find("a",class_="cover")['href']
        req=Request(link_juego,headers=hdr)
        page_juego=urlopen(req)
        s = BeautifulSoup(page_juego,"lxml")
        
        tags = s.find("div",class_="tags").find_all("a")
        tags = [tag.text for tag in tags]
        
        release = s.find("div",class_="release").find("span").text

        juegos.append((titulo,cover,tags,price,release))
        
    return juegos

if __name__ == "__main__":
    print(extraer_juegos())