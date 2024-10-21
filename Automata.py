import networkx as nx
import itertools as it
import matplotlib.pyplot as plt

class AutomataFinitoDeterminista:
    def __init__(self):
        self.grafo = nx.MultiDiGraph()  # Usamos MultiDiGraph para múltiples aristas

    def agregar_estado(self, estado, tipo=None, color='skyblue'):
        ''' Agrega un nodo al grafo. '''
        self.grafo.add_node(estado)
        if tipo == 'final':
            nx.set_node_attributes(self.grafo, {estado: 'red'}, 'color')
        elif tipo == 'inicial':
            nx.set_node_attributes(self.grafo, {estado: 'green'}, 'color')
        else:
            nx.set_node_attributes(self.grafo, {estado: color}, 'color')

    def agregar_transicion(self, estado_origen, estado_destino, simbolo):
        ''' Agrega una arista entre dos nodos. '''
        self.grafo.add_edge(estado_origen, estado_destino, label=simbolo)

    def mostrar_automata(self):
        '''Dibuja el automata finito determinista utilizando NetworkX y Matplotlib.'''

        # Posición de los nodos
        pos_nodos = nx.spring_layout(self.grafo, seed=5)
        # Colores de los nodos
        colores = [nx.get_node_attributes(self.grafo, 'color').get(n) for n in self.grafo.nodes()]
        # Etiquetas de los nodos
        labels = nx.get_edge_attributes(self.grafo, 'label')
        # Estilo de las aristas
        connectionstyle = [f"arc3,rad={r}" for r in it.accumulate([0.15] * 4)]

        # Dibujar el grafo con arcos separados para múltiples transiciones
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

        # nx.draw_networkx_edges(
        #     self.grafo, pos, edge_color="black", connectionstyle=connectionstyle
        # )

        # Dibujar las etiquetas de las aristas
        nx.draw_networkx_edge_labels(
            self.grafo,
            pos_nodos,
            labels,
            connectionstyle=connectionstyle,
            label_pos=0.3,
            font_color="black",
            bbox={"alpha": 0},
        )
        plt.show()

# Ejemplo de uso
# afd = AutomataFinitoDeterminista()
# afd.agregar_estado("q0", tipo="inicial")
# afd.agregar_estado("q1")
# afd.agregar_estado("q2")
# afd.agregar_estado("q3", tipo="final")
# afd.agregar_transicion("q0", "q1", "a")
# afd.agregar_transicion("q1", "q0", "c")
# afd.agregar_transicion("q1", "q1", "d")
# afd.agregar_transicion("q0", "q2", "b")
# afd.agregar_transicion("q1", "q3", "d")
# afd.agregar_transicion("q2", "q3", "b")
# afd.agregar_transicion("q3", "q3", "a")
# afd.mostrar_automata()

def ksa(llave):
    S = list(range(256))
    key_length = len(llave)
    j = 0
    for i in range(256):
        j = (j + ord(llave[i % key_length]) + S[i]) % 256
        S[i], S[j] = S[j], S[i]

    return S


def prga(S):
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


if __name__ == "__main__":
    afd = AutomataFinitoDeterminista()

    afd.agregar_estado("q0", tipo="inicial")

    llave = "Llave a utilizar"
    texto_plano = "Mensaje a cifrar"

    afd.agregar_estado("q1")
    afd.agregar_transicion("q0", "q1", f"{texto_plano}\n{llave}")

    texto_cifrado = rc4(llave, texto_plano, afd)

    afd.agregar_estado("q3", tipo="final")
    afd.agregar_transicion("q2", "q3", f"{texto_cifrado}")
    afd.mostrar_automata()