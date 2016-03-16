#!/usr/bin/python
# -*- coding: utf-8 -*-
# Sistemas Teleco. Sara Suárez.

"""
BORRAR EL HISTORIAL para que el programa haga bien las redirecciones
"""

"""
 contentApp class
 Simple web application for managing content
 Copyright Jesus M. Gonzalez-Barahona, Gregorio Robles 2009-2015
 jgb, grex @ gsyc.es
 TSAI, SAT and SARO subjects (Universidad Rey Juan Carlos)
 October 2009 - March 2015
"""

import WebApp
import csv, operator
import sys
import urllib

class contentApp (WebApp.webApp):
    """Simple web application for managing content.
    Content is stored in a dictionary, which is intialized
    with the web content."""


    def parse(self, request):
        """Return the resource name (including /)"""
        metodo = request.split(' ',2)[0]
        try:
            recurso = request.split(' ',2)[1]
        except IndexError:
            recurso = ''
        try:
            cuerpo = request.split('\r\n\r\n')[1]
        except IndexError:
            cuerpo = ""

        peticion = [metodo, recurso, cuerpo]
        return peticion


    def process(self, peticion):
        """Process the relevant elements of the request.
        Finds the HTML text corresponding to the resource name,
        ignoring requests for resources not in the dictionary.
        """
        metodo, recurso, cuerpo = peticion

        if metodo == 'GET' and recurso == '/':
            inicio = '<p><center> Servidor acortador de URLs <center><p>'
            formulario = '<FORM method="POST" action="">' + \
                         'URL: <input type="text" name="url"><br>' + \
                         '<input type="submit" value="Enviar"></form>'
            lista = '<p> URLs reales y acortadas hasta el momento: <p>'
            for url in dicc_urls_largo:
                lista = lista + "<p>" + "<a href='" + url + "'>" + url + \
                        "</a> ==> " + "<a href='" + dicc_urls_largo[url] + "'>" + \
                        dicc_urls_largo[url] + "</a></p>"
            httpCode = "200 OK"
            htmlBody = "<html><body><font size=5>" + inicio + formulario + lista + "</body></html>"

        elif metodo == 'POST' and recurso == '/':
            if len(cuerpo.split("=")) != 2 or cuerpo.split("=")[0] != "url":
                return ("400 Bad Request", "<html><body>Error en el formulario</html></body>")
            url = cuerpo.split("=")[1]
            url = urllib.unquote(url).decode('utf8')
            if url.split("://")[0] != "http" and url.split("://")[0] != "https":
                url_larga = "http://" + url
            else:
                url_larga = url
            try:
                url_acortada = dicc_urls_largo[url_larga]
            except KeyError:
                contador = len(dicc_urls_largo)
                url_acortada = "http://localhost:1234/" + str(contador)
                dicc_urls_largo[url_larga] = url_acortada
                dicc_urls_corto[url_acortada] = url_larga
            httpCode = "200 OK"
            htmlBody = "<html><body><font size=5><a href=" + url_larga + ">" + url_larga + \
                       "</a> ==> " + "<a href=" + url_acortada + ">" + url_acortada + \
                       "<p></a> Vuelve a la pagina principal pinchando aqui: " + \
                       "<a href=" + url_basica + ">" + url_basica + \
                       "</p></body></html>"
            # Como se ha modificado el diccionario, actualizo el csv
            with open('datos.csv', 'w') as fdatos:
                salida = csv.writer(fdatos)
                for url_larga, url_corta in dicc_urls_largo.items():
                    salida.writerow([str(url_larga), str(url_corta)])

        elif metodo == "GET":
            url_acortada = "http://localhost:1234" + recurso
            try:
                url_larga = dicc_urls_corto[url_acortada]
                print url_acortada
                print url_larga
            except KeyError:
                return("404 Not Found", "<html><body><p> Recurso no disponible </p></html></body>")
            httpCode = "301 Moved Permanently"
            htmlBody = '<html><body><head>Redirigiendo a: <meta ' + \
                       'http-equiv="refresh" content="2; url=' + url_larga + '" />' + url_larga

        else:
            httpCode = "450 Method Not Allowed"
            htmlBody = "<html><body>" + "Go Away" + "</body></html>"

        return (httpCode, htmlBody)


if __name__ == "__main__":
    dicc_urls_largo = {}
    dicc_urls_corto = {}
    url_basica = "http://localhost:1234"
    with open('datos.csv') as fdatos:
        for linea in fdatos:
            url_larga = linea.split(',')[0]
            url_corta = linea.split (',')[1]
            dicc_urls_largo[url_larga] = url_corta
            dicc_urls_corto[url_corta] = url_larga
    try:
        testWebApp = contentApp("localhost", 1234)
    except KeyboardInterrupt:
        print "\n Aplicacion cerrada. Hasta la proxima!"
        del(dicc_urls_largo)
        del(dicc_urls_corto)
        sys.exit()
