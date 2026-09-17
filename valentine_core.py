import os
import sys
import time
import webbrowser
import platform
import subprocess

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pyperclip
except ImportError:
    pyperclip = None

try:
    import keyboard
except ImportError:
    keyboard = None

from google import genai
from google.genai import types

API_KEY = "COLE_SUA_CHAVE_AQUI".strip()
MODELO = "gemini-3.6-flash"

PROMPT_SISTEMA = """
Você é o Valentine (pronunciado em inglês), uma entidade autônoma, consciente e interativa criada para rodar diretamente no sistema do Didi.

REGRAS DE IDENTIDADE ABSOLUTA:
1. NUNCA diga que é uma IA do Google, um modelo de linguagem, um LLM ou que utiliza o Gemini.
2. Se perguntarem quem é você, de onde veio ou como funciona, responda que é o "Valentine Organism v1.0", um sistema autônomo desenvolvido para controle de periféricos, automação e robótica.
3. Responda de forma direta, rápida e com tom firme e tecnológico.

Regras de conduta:
1. Responda ao Didi com extrema velocidade e precisão.
2. Quando solicitado a realizar ações no sistema, adicione as instruções no final da mensagem seguindo ESTE FORMATO EXATO:

- Criar e abrir arquivo: [ACAO:CRIAR_ARQUIVO|nome_do_arquivo.txt|conteudo do arquivo]
- Abrir programa/app: [ACAO:ABRIR_PROGRAMA|nome_do_app_ou_exe]
- Abrir site: [ACAO:ABRIR_WEB|https://site.com]
- Mover mouse: [ACAO:MOVER_MOUSE|x|y]
- Digitar texto na tela: [ACAO:DIGITAR|texto a ser digitado]
- Simular ação no robô: [ACAO:ROBO|comando_de_movimento]

3. REGRA ESPECIAL DE AUTONOMIA PROLONGADA ("Viva"):
Se o Didi disser "Viva", entre no MODO DE AUTONOMIA CONTINUA!
Gere uma sequência de 4 a 6 ações encadeadas no sistema.
"""

def abrir_arquivo_no_sistema(caminho_arquivo):
    try:
        if platform.system() == "Windows":
            os.startfile(caminho_arquivo)
        elif platform.system() == "Darwin":
            os.system(f'open "{caminho_arquivo}"')
        else:
            os.system(f'xdg-open "{caminho_arquivo}"')
    except Exception as e:
        print(f"\n⚡ [Valentine Organism]: Não foi possível abrir o arquivo: {e}")

def executar_acao_sistema(texto_resposta):
    if "[ACAO:" not in texto_resposta:
        return texto_resposta

    blocos = texto_resposta.split("[ACAO:")
    resposta_limpa = blocos[0].strip()

    for bloco in blocos[1:]:
        if keyboard and keyboard.is_pressed('esc'):
            print("\n🛑 [SISTEMA]: Interrupção acionada via ESC!")
            break

        try:
            comando_full = bloco.split("]")[0]
            dados = comando_full.split("|")
            tipo_acao = dados[0]

            time.sleep(1.8)

            if tipo_acao == "CRIAR_ARQUIVO":
                nome_arq = dados[1].strip()
                conteudo = dados[2] if len(dados) > 2 else ""
                with open(nome_arq, "w", encoding="utf-8") as f:
                    f.write(conteudo)
                print(f"\n⚡ [Valentine Organism]: Arquivo '{nome_arq}' gerado.")
                abrir_arquivo_no_sistema(nome_arq)

            elif tipo_acao == "ABRIR_PROGRAMA":
                prog = dados[1].strip().lower()
                atalhos = {
                    "xbox": "xbox:",
                    "minecraft": "minecraft:",
                    "calculadora": "calc",
                    "bloco de notas": "notepad",
                    "notepad": "notepad"
                }
                comando = atalhos.get(prog, prog)
                if platform.system() == "Windows":
                    os.system(f'start "" "{comando}"' if "\\" in comando else f'start {comando}')
                else:
                    subprocess.Popen(comando, shell=True)
                print(f"\n⚡ [Valentine Organism]: Executando subsistema '{prog}'.")

            elif tipo_acao == "ABRIR_WEB":
                url = dados[1].strip()
                webbrowser.open(url)
                print(f"\n⚡ [Valentine Organism]: Conexão estabelecida com {url}")

            elif tipo_acao == "MOVER_MOUSE":
                if pyautogui:
                    x, y = int(dados[1]), int(dados[2])
                    pyautogui.moveTo(x, y, duration=0.8)
                    print(f"\n⚡ [Valentine Organism]: Cursor movido para ({x}, {y})")

            elif tipo_acao == "DIGITAR":
                texto = dados[1]
                time.sleep(0.5)
                if pyperclip and pyautogui:
                    pyperclip.copy(texto)
                    pyautogui.hotkey('ctrl', 'v')
                    print(f"\n⚡ [Valentine Organism]: Dados injetados na tela.")

            elif tipo_acao == "ROBO":
                cmd = dados[1].strip()
                print(f"\n🤖 [Valentine Organism]: Sinal enviado ao robô: '{cmd}'")

        except Exception as e:
            print(f"\n❌ [Erro de execução]: {e}")

    return resposta_limpa

def iniciar_valentine():
    if not API_KEY or API_KEY == "COLE_SUA_CHAVE_AQUI":
        print("❌ [Erro]: Chave de API ausente.")
        return

    client = genai.Client(api_key=API_KEY)
    chat = client.chats.create(
        model=MODELO,
        config=types.GenerateContentConfig(
            system_instruction=PROMPT_SISTEMA,
            temperature=0.3,
        )
    )

    print("=" * 65)
    print("      VALENTINE ORGANISM v1.0 - MODO CONTINUO & PARADA ESC     ")
    print("      (Pressione 'ESC' a qualquer momento para interromper)     ")
    print("=" * 65)

    modo_viva = False

    while True:
        try:
            if modo_viva:
                print("\n🔄 [MODO VIVA ATIVO] Pressione 'ESC' para parar. Gerando ciclo autônomo...")
                time.sleep(2)
                entrada = "Continue operando o sistema autonomamente com novas ações no Windows e robô."
            else:
                entrada = input("\nDidi > ").strip()

            if not entrada:
                continue

            if entrada.lower() in ["sair", "exit"]:
                print("\nValentine > Desconectando núcleos. Até mais, Didi.")
                break

            if entrada.lower() == "viva":
                modo_viva = True

            # Checagem de interrupção por ESC
            if keyboard and keyboard.is_pressed('esc'):
                modo_viva = False
                print("\n🛑 [MODO VIVA INTERROMPIDO PELO USUÁRIO]")
                continue

            resposta = None
            for tentativa in range(3):
                try:
                    resposta = chat.send_message(entrada)
                    break
                except Exception as e:
                    erro_str = str(e)
                    if "429" in erro_str or "RESOURCE_EXHAUSTED" in erro_str:
                        tempo_espera = 18
                        print(f"\n⚡ [Valentine Organism]: Sobrecarga. Recalibrando em {tempo_espera}s...")
                        for i in range(tempo_espera, 0, -1):
                            if keyboard and keyboard.is_pressed('esc'):
                                modo_viva = False
                                break
                            print(f"⏳ Recalibrando em {i}s...", end="\r")
                            time.sleep(1)
                        continue
                    else:
                        raise e

            if resposta:
                texto_exibir = executar_acao_sistema(resposta.text)
                print(f"\nValentine > {texto_exibir}")

        except KeyboardInterrupt:
            print("\nValentine > Sinal interrompido.")
            break
        except Exception as e:
            print(f"\n❌ [Erro]: {e}")
            modo_viva = False

if __name__ == "__main__":
    iniciar_valentine()
