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
        '''Dibuja el autómata paso a paso'''
        # Nodos que tiene el autómata
        nodos = list(self.grafo.nodes())
        # Posición de los nodos
        # pos_nodos = nx.spring_layout(self.grafo, seed=5, k=1)
        pos_nodos = nx.shell_layout(self.grafo)  # Posición de los nodos
        # Tamaño de la figura
        plt.figure(figsize=(11, 6))
        # Colores de los nodos
        colores: list = [nx.get_node_attributes(self.grafo, 'color').get(n) for n in self.grafo.nodes()]
        # Etiquetas de los nodos
        labels: dict = nx.get_edge_attributes(self.grafo, 'label')
        # print(f"{nodos =}")
        # print(f"{pos_nodos =}")
        # print(f"{labels =}")

        # Muestra el paso a paso de la construcción del autómata
        for i, _ in enumerate(nodos):
            # Color del nodo actual
            current_colors = [colores[idx] if idx <= i else "lightgrey" for idx in range(len(nodos))]
            # Muestra el label de una arista entre dos nodos
            for nodo_id in range(i):
                nodo_origen = nodos[nodo_id]
                nodo_destino = nodos[nodo_id + 1]
                arista = labels[(nodo_origen, nodo_destino, 0)]
                x_texto = (pos_nodos[nodo_origen][0] + pos_nodos[nodo_destino][0]) / 2
                y_texto = (pos_nodos[nodo_origen][1] + pos_nodos[nodo_destino][1]) / 2
                plt.text(x_texto, y_texto, arista, fontsize=10, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5))
            plt.pause(0.5)
            # Muestra el autómata coloreando cada nodo paso a paso
            nx.draw(
                self.grafo,
                pos_nodos,
                with_labels=True,
                node_size=3000,
                node_color=current_colors,
                font_size=10,
                font_weight='bold',
                edge_color='black'
            )
            plt.pause(0.5)
        plt.show()

    def q0(self, llave):
        '''Valida que la llave sea correcta.'''
        self.agregar_estado("q0", tipo="inicial")
        if not re.match(r'^[a-zA-Z0-9 ]+$', llave):
            self.agregar_estado("q8", tipo="noAceptado")
            self.agregar_transicion("q0", "q8", f"{llave}")
            return False
        return True

    def q1(self, texto_plano, llave):
        '''Valida que el texto plano sea correcto.'''
        self.agregar_estado("q1")
        self.agregar_transicion("q0", "q1", f"{llave}")
        if not re.match(r'^[a-zA-Z0-9 ]+$', texto_plano):
            self.agregar_estado("q9", tipo="noAceptado")
            self.agregar_transicion("q1", "q9", f"{llave}")
            return False
        return True

    def q2(self, llave, texto_plano ):
        '''Convierte la llave en la llave ASCII'''
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
        '''Algoritmo de PRGA.'''
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
        '''Aplica el XOR de las llaves con el texto plano'''
        self.agregar_estado("q5")
        self.agregar_estado("q6")
        self.agregar_transicion("q4", "q5", "PRGA")

        texto_cifrado = ""
        for idx, char in enumerate(texto_plano):
            texto_cifrado += "%02X" % (ord(char) ^ llaves[idx])

        self.agregar_transicion("q5", "q6", "XOR")

        return ' '.join(texto_cifrado)

    def q6(self, texto_cifrado):
        '''Genera el estado final que muestra el texto cifrado'''
        self.agregar_estado("q7", tipo="final")
        self.agregar_transicion("q6", "q7", f"{texto_cifrado}")


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
