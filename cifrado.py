def ksa(llave):
    S = list(range(256))
    key_length = len(llave)
    j = 0
    for i in range(256):
        j = (j + ord(llave[i % key_length]) + S[i]) % 256
        S[i], S[j] = S[j], S[i]

    return S


def prga(S, texto_plano):
    i = 0
    j = 0
    k = 0
    llaves = []
    while k < len(texto_plano):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]

        llaves.append(S[(S[i] + S[j]) % 256])
        k += 1
    return llaves


def rc4(llave, texto_plano):
    S = ksa(llave)
    llaves = prga(S, texto_plano)

    texto_cifrado = []
    for idx, char in enumerate(texto_plano):
        texto_cifrado.append("%02X" % (ord(char) ^ llaves[idx]))
    return ' '.join(texto_cifrado)

if __name__ == "__main__":
    llave = "llavellavellavellave"
    texto_plano = "textoPorCifrar"


    texto_cifrado = rc4(llave, texto_plano)
    print(texto_cifrado)
    # 86 E4 92 A1 9D 74 5C CO FC 7A 3C 53 6A DO
