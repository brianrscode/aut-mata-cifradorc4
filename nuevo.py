import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
import itertools as it
import re


#######################################################
##################### AUTÓMATA FD #####################
#######################################################
class AutomataFinitoDeterminista:
    def __init__(self):

        self.grafo = nx.MultiDiGraph()  # Grafo con múltiples aristas

    def agregar_estado(self, estado, tipo=None, color='skyblue'):
        '''Agrega un estado (nodo) al autómata.'''
        if tipo == 'final':
            color = 'green'
        elif tipo == 'inicial':
            color = 'yellow'
        elif tipo == 'noAceptado':
            color = 'red'
        if not color:
            color = 'skyblue'

        self.grafo.add_node(estado)
        nx.set_node_attributes(self.grafo, {estado: color}, 'color')

    def agregar_transicion(self, estado_origen, estado_destino, simbolo):
        '''Agrega una transición (arista) entre estados.'''
        self.grafo.add_edge(estado_origen, estado_destino, label=simbolo)

    def mostrar_automata(self):
        '''Dibuja el autómata usando NetworkX y Matplotlib.'''
        # Posición de los nodos
        pos_nodos = nx.spring_layout(self.grafo, seed=5, k=1)
        # Colores de los nodos
        colores = [nx.get_node_attributes(self.grafo, 'color').get(n) for n in self.grafo.nodes()]
        # Etiquetas de los nodos
        labels = nx.get_edge_attributes(self.grafo, 'label')

        # Dibujar nodos y aristas
        nx.draw(
            self.grafo,
            pos_nodos,
            with_labels=True,
            connectionstyle='arc3,rad=0.2',
            node_size=2000,
            node_color=colores,
            font_size=10,
            font_weight='bold',
            edge_color='black'
        )
        # Dibujar etiquetas de las aristas
        nx.draw_networkx_edge_labels(
            self.grafo,
            pos_nodos,
            labels,
            connectionstyle=[f"arc3,rad={r}" for r in it.accumulate([0.15] * 4)],
            label_pos=0.5,
            font_color="black",
            # bbox={"alpha": 0},  # Elimina el fondo del label
        )
        plt.show()

    def q0(self, llave):
        pat = r'[a-z]{5}'
        self.agregar_estado("q0", tipo="inicial")
        if not re.match(pat, llave):
            self.agregar_estado("q8", tipo="noAceptado")
            self.agregar_transicion("q0", "q8", f"{llave}")
            return False
        return True

    def q1(self, texto_plano, llave):
        self.agregar_estado("q1")
        self.agregar_transicion("q0", "q1", f"{llave}")
        if not re.match(r'[a-zA-Z0-9]{5,10}', texto_plano):
            self.agregar_estado("q9", tipo="noAceptado")
            self.agregar_transicion("q1", "q9", f"{llave}")
            return False
        return True

    def q2(self, llave, texto_plano ):
        llave_ascii = [ord(c) for c in llave]
        self.agregar_estado("q2")
        self.agregar_transicion("q1", "q2", f"{texto_plano}")
        return llave_ascii

    def q3(self, llave_ascii):
        '''Algoritmo de KSA.'''
        S = list(range(256))  # Tabla S
        key_length = len(llave_ascii)
        j = 0
        for i in range(256):
            j = (j + llave_ascii[i % key_length] + S[i]) % 256
            S[i], S[j] = S[j], S[i]
        self.agregar_estado("q3")
        self.agregar_transicion("q2", "q3", f"{llave_ascii}")
        return S

    def q4(self, S, texto_plano):
        i = 0
        j = 0
        k = 0
        llaves = []
        self.agregar_estado("q4")
        self.agregar_transicion("q3", "q4", "KSA")
        while k < len(texto_plano):
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            llaves.append(S[(S[i] + S[j]) % 256])
            k += 1

        return llaves

    def q5(self, llaves, texto_plano):
        self.agregar_estado("q5")
        self.agregar_estado("q6")
        self.agregar_transicion("q4", "q5", "PRGA")

        texto_cifrado = ""
        for idx, char in enumerate(texto_plano):
            texto_cifrado += "%02X" % (ord(char) ^ llaves[idx])

        self.agregar_transicion("q5", "q6", "XOR")

        return texto_cifrado

    def q6(self, texto_cifrado):
        self.agregar_estado("q7", tipo="final")
        self.agregar_transicion("q6", "q7", f"{texto_cifrado}")

#######################################################
##################### CIFRADO RC4 #####################
#######################################################
def ksa(llave):
    '''Algoritmo de KSA.'''
    S = list(range(256))  # Tabla S
    key_length = len(llave)
    llave_ascii = [ord(c) for c in llave]
    j = 0
    for i in range(256):
        j = (j + llave_ascii[i % key_length] + S[i]) % 256
        S[i], S[j] = S[j], S[i]
    return S

def prga(S):
    '''Algoritmo de PRGA.'''
    i = 0
    j = 0
    while True:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        yield S[(S[i] + S[j]) % 256]

def rc4(llave, texto_plano, afd):
    afd.agregar_estado("q2")
    S = ksa(llave)
    llaves = prga(S)
    afd.agregar_transicion("q1", "q2", "ksa y prga")

    texto_cifrado = ""
    for char in texto_plano:
        texto_cifrado += "%02X" % (ord(char) ^ next(llaves))

# Función que se ejecuta al presionar el botón
def generar_automata():
    '''Genera un autómata y muestra el resultado'''

    # Obtener la llave
    llave = entry_llave.get()
    # Obtener el texto plano
    texto_plano = entry_texto.get()

    if not llave or not texto_plano:
        messagebox.showerror("Error", "Por favor ingrese tanto la llave como el texto plano.")
        return


    afd = AutomataFinitoDeterminista()
    if afd.q0(llave):
        if afd.q1(texto_plano, llave):
            llave_ascii = afd.q2(llave, texto_plano)
            S = afd.q3(llave_ascii)
            llaves = afd.q4(S, texto_plano)
            texto_cifrado = afd.q5(llaves, texto_plano)
            afd.q6(texto_cifrado)


    afd.mostrar_automata()


# Interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Generador de Autómata y RC4")
root.geometry("300x200")

# Etiquetas y entradas de texto
label_llave = tk.Label(root, text="Llave de 5 caracteres (a-z):")
label_llave.pack()

entry_llave = tk.Entry(root)
entry_llave.pack()

label_texto = tk.Label(root, text="Texto plano de 5 a 10 carateres (a-zA-Z0-9):")
label_texto.pack()

entry_texto = tk.Entry(root)
entry_texto.pack()

# Botón para generar el autómata
btn_generar = tk.Button(root, text="Generar Autómata", command=generar_automata)
btn_generar.pack()

# Iniciar la ventana principal
root.mainloop()
