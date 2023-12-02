# Imports
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from numpy.random import randint
from difflib import SequenceMatcher
import hashlib
import numpy as np
import time as tm


def encode_message(bits, bases):
    message_cod = []
    for i in range(n):
        qc = QuantumCircuit(1, 1)
        if bases[i] == 0:  # Preparação na polarização de 0º
            if bits[i] == 0:
                qc.x(0)

        elif bases[i] == 1:  # Preparação na polarização de 45º
            if bits[i] == 0:
                qc.h(0)
            else:
                qc.x(0)
                qc.h(0)

        elif bases[i] == 2:  # Preparação na polarização de 90º
            if bits[i] == 0:
                qc.h(0)
            else:
                qc.x(0)
                qc.h(0)

        elif bases[i] == 3:  # Preparação na polarização de 135º ou -45º
            if bits[i] == 0:
                qc.h(0)
                qc.z(0)
            else:
                qc.x(0)
                qc.h(0)
                qc.sdg(0)

        qc.barrier()
        message_cod.append(qc)
    return message_cod


def medicao_mensagem(message_cod, bases, backend):
    measurements = []
    for q in range(n):
        if bases[q] == 0:  # Preparação na polarização de 0º
            message_cod[q].x(0)
            message_cod[q].measure(0, 0)

        elif bases[q] == 1:  # Preparação na polarização de 45º
            message_cod[q].x(0)
            message_cod[q].h(0)
            message_cod[q].measure(0, 0)

        elif bases[q] == 2:  # Preparação na polarização de 90º
            message_cod[q].x(0)
            message_cod[q].h(0)
            message_cod[q].measure(0, 0)

        elif bases[q] == 3:  # Preparação na polarização de 135º ou -45º
            message_cod[q].x(0)
            message_cod[q].h(0)
            message_cod[q].sdg(0)
            message_cod[q].measure(0, 0)

        result = backend.run(message_cod[q], shots=1024, memory=True).result()
        measured_bit = int(result.get_memory()[0])
        measurements.append(measured_bit)
    return measurements


def remover(a_bases, b_bases, bits):
    good_bits = []
    for q in range(n):
        if a_bases[q] == b_bases[q]:
            good_bits.append(bits[q])
    return good_bits


def comp_bits(bits, selection):
    amostra_bits = []
    for i in selection:
        i = np.remainder(i, len(bits))
        amostra_bits.append(bits.pop(i))
    return amostra_bits


def gera_arquivo_chave(circuito, nome_arquivo):
    with open(nome_arquivo, 'w') as file:
        for i, circuit in enumerate(circuito):
            circuit_str = circuit.qasm()
            file.write(f"// circuito N {i}:\n")
            file.write(circuit_str)
            file.write("\n\n")


def porcentagem_diferenca(chave_alice, chave_bob):
    similar = SequenceMatcher(None, chave_bob, chave_alice).ratio()
    porcentagem = similar * 100
    return porcentagem


# Geração aleatoria e o tamanho da geração seria o n = 145
n = 145

# Passo 1
alice_bits = randint(2, size=n)

# Passo 2
alice_bases = randint(4, size=n)
message_cod = encode_message(alice_bits, alice_bases)

# Passo 3
bob_bases = randint(4, size=n)
backend = AerSimulator()
print('Seu dispositivo é o: {}' .format(backend.name))
print('')
bob_results = medicao_mensagem(message_cod, bob_bases, backend)

# Passo 4
chave_alice = remover(alice_bases, bob_bases, alice_bits)
chave_bob = remover(alice_bases, bob_bases, bob_results)

# Passo 5
amostra_bits_tamanho = 10
selecao_bits = randint(n, size=amostra_bits_tamanho)
comp_bob = comp_bits(chave_bob, selecao_bits)
comp_alice = comp_bits(chave_alice, selecao_bits)

# Convertendo em string
conteudo_bob = "\n".join(map(str, chave_bob))

conteudo_alice = "\n".join(map(str, chave_alice))

# Gerando arquivos
with open("encode_message.pem", "wb") as arquivo:
    arquivo.write(str(message_cod).encode())

with open("chave_bob.pem", "w") as arquivo:
    arquivo.write(conteudo_bob)

with open("chave_alice.pem", "w") as arquivo:
    arquivo.write(conteudo_alice)

gera_arquivo_chave(message_cod, "encode_message.qasm")

# Colocando em Hash
chave_bob_hash = ''.join(str(numero) for numero in chave_bob)
chave_alice_hash = ''.join(str(numero) for numero in chave_alice)

hash_bob = hashlib.sha256()
hash_alice = hashlib.sha256()

hash_bob.update(chave_bob_hash.encode('utf-8'))
hash_alice.update(chave_alice_hash.encode('utf-8'))

hash_reultado_bob = hash_bob.hexdigest()
hash_reultado_alice = hash_alice.hexdigest()

# fazendo a verrificação do protocolo e similaridade
porcentagem = porcentagem_diferenca(chave_alice, chave_bob)
verdade = comp_bob == comp_alice


while True:
    # Solicitação do usuario
    escolher = input('''
Qual vai ser gerada?
1 - Chaves
2 - Hash
3 - Protocolo
4 - Similaridade
5 - Tudo
6 - Finalizar
''')
    if escolher.lower() in ['chaves', 'chave', 'c', '1']:
        tm.sleep(5)
        print()
        print("A chave de Alice: {}".format(chave_alice))
        print("A chave de Bob:   {}".format(chave_bob))

        verdade = comp_bob == comp_alice
        tm.sleep(5)
        print()
        print('O protocolo deu: ', verdade)

    elif escolher.lower() in ['hash', 'h', '2']:
        tm.sleep(5)
        print()
        print('Hash de Bob ', hash_reultado_bob)
        print('Hash de Alice ', hash_reultado_alice)

        verdade = comp_bob == comp_alice
        tm.sleep(5)
        print()
        print('O protocolo deu: ', verdade)

    elif escolher.lower() in ['protocolo', 'P', '3']:
        tm.sleep(5)
        verdade = comp_bob == comp_alice
        print()
        print('O protocolo deu: ', verdade)

    elif escolher.lower() in ['similaridade', 's', '4']:
        tm.sleep(5)
        porcentagem = porcentagem_diferenca(chave_alice, chave_bob)
        print()
        print(
            f'Com uma taxa de diferença entre as chaves de: {porcentagem:.2f}%')

        verdade = comp_bob == comp_alice
        tm.sleep(5)
        print()
        print('O protocolo deu: ', verdade)

    elif escolher.lower() in ['tudo', "t", "5"]:
        tm.sleep(5)
        print()
        print("A chave de Alice: {}".format(chave_alice))
        print("A chave de Bob:   {}".format(chave_bob))
        tm.sleep(5)
        print()
        print('Hash de Bob ', hash_reultado_bob)
        print('Hash de Alice ', hash_reultado_alice)
        print()
        tm.sleep(5)
        verdade = comp_bob == comp_alice
        print('O protocolo deu: ', verdade)
        tm.sleep(5)
        porcentagem = porcentagem_diferenca(chave_alice, chave_bob)
        print(
            f'Com uma taxa de similaridade entre as chaves de: {porcentagem:.2f}%')
    
    elif escolher.lower() in ['finalizar', 'f', '6']:
        print("Que pena que vai finalizar sem gerar um resultado 😕")
        

    else:
        print('Por favor, insira uma opção correta.')

    continuar = input("Deseja executar mais uma vez? (s/n): ")
    if continuar.lower() != 's':  # Se a expressão for diferente de s, o programa é encerrado
        print("Finalizando o programa. 🙃")
        tm.sleep(5)
        break
    