import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
import itertools as it


#######################################################
##################### AUTÓMATA FD #####################
#######################################################
class AutomataFinitoDeterminista:
    def __init__(self):
        self.grafo = nx.MultiDiGraph()  # Grafo con múltiples aristas

    def agregar_estado(self, estado, tipo=None, color='skyblue'):
        '''Agrega un estado (nodo) al autómata.'''
        self.grafo.add_node(estado)
        if tipo == 'final':
            nx.set_node_attributes(self.grafo, {estado: 'red'}, 'color')
        elif tipo == 'inicial':
            nx.set_node_attributes(self.grafo, {estado: 'green'}, 'color')
        else:
            nx.set_node_attributes(self.grafo, {estado: color}, 'color')

    def agregar_transicion(self, estado_origen, estado_destino, simbolo):
        '''Agrega una transición (arista) entre estados.'''
        self.grafo.add_edge(estado_origen, estado_destino, label=simbolo)

    def mostrar_automata(self):
        '''Dibuja el autómata usando NetworkX y Matplotlib.'''
        # Posición de los nodos
        pos_nodos = nx.spring_layout(self.grafo, seed=5)
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
            label_pos=0.3,
            font_color="black",
            bbox={"alpha": 0},
        )
        plt.show()

#######################################################
##################### CIFRADO RC4 #####################
#######################################################
def ksa(llave):
    '''Algoritmo de KSA.'''
    S = list(range(256))  # Tabla S
    key_length = len(llave)
    j = 0
    for i in range(256):
        j = (j + ord(llave[i % key_length]) + S[i]) % 256
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
    return texto_cifrado

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
    afd.agregar_estado("q0", tipo="inicial")
    afd.agregar_estado("q1")
    afd.agregar_transicion("q0", "q1", f"{texto_plano}\n{llave}")

    texto_cifrado = rc4(llave, texto_plano, afd)

    afd.agregar_estado("q3", tipo="final")
    afd.agregar_transicion("q2", "q3", f"{texto_cifrado}")
    afd.mostrar_automata()

# Interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Generador de Autómata y RC4")
root.geometry("300x200")

# Etiquetas y entradas de texto
label_llave = tk.Label(root, text="Llave:")
label_llave.pack()

entry_llave = tk.Entry(root)
entry_llave.pack()

label_texto = tk.Label(root, text="Texto plano:")
label_texto.pack()

entry_texto = tk.Entry(root)
entry_texto.pack()

# Botón para generar el autómata
btn_generar = tk.Button(root, text="Generar Autómata", command=generar_automata)
btn_generar.pack()

# Iniciar la ventana principal
root.mainloop()
