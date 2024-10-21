from Automata import AutomataFinitoDeterminista


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
