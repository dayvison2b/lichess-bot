import time
import chess.engine
import requests
import json

# Configurações
lichess_token = 'your_token_here'
lichess_url = 'https://lichess.org'
stockfish_path = "./stockfish"

# Função para obter a lista de partidas em andamento

def obter_partidas_em_andamento():
    headers = {'Authorization': f"Bearer {lichess_token}"}
    response = requests.get(f"{lichess_url}/api/account/playing", headers=headers)
    return response.json()

def fazer_movimento_com_base_na_analise(fen_da_partida, tempo_analise=1.0):
    # Crie um tabuleiro a partir do FEN da partida
    board = chess.Board(fen_da_partida)

    # Analisando a posição com o Stockfish
    move_info = engine.analyse(board, chess.engine.Limit(time=tempo_analise))

    movimentos_da_cor_atual = []
    for move in move_info.get("pv", []):
        # Criando uma cópia temporária do tabuleiro
        temp_board = board.copy()

        if temp_board.is_legal(move):
            # O movimento é legal
            temp_board.push(move)
            movimentos_da_cor_atual.append(move.uci())
        else:
            # O movimento é ilegal
            continue

    if movimentos_da_cor_atual:
        # Escolha o melhor movimento da lista de movimentos possíveis
        melhor_movimento = movimentos_da_cor_atual[0]
        print(f"Melhor movimento: {melhor_movimento}")
        return melhor_movimento
    else:
        print("Não foi encontrado nenhum movimento legal.")
        return None

engine =  chess.engine.SimpleEngine.popen_uci("stockfish/stockfish.exe")
cor_atual = None  # Inicialize a cor atual como desconhecida

last_fen = ""

while True:
    # Obtém as partidas em andamento
    partidas_em_andamento = obter_partidas_em_andamento()
    
    if 'nowPlaying' in partidas_em_andamento and len(partidas_em_andamento["nowPlaying"]) > 0:
        if partidas_em_andamento["nowPlaying"][0]["isMyTurn"] and partidas_em_andamento["nowPlaying"][0]["fen"] != last_fen:
            fen_da_partida = partidas_em_andamento["nowPlaying"][0]["fen"]
            print(f"FEN da Partida em Andamento: {fen_da_partida}")
            last_fen = fen_da_partida

            # Verifique a cor atual apenas uma vez no início da partida
            cor_atual = partidas_em_andamento["nowPlaying"][0]["color"]

            # Faça o movimento com base na análise do Stockfish
            melhor_movimento = fazer_movimento_com_base_na_analise(fen_da_partida, tempo_analise=1)

            if melhor_movimento:
                # Faça o movimento no jogo no Lichess
                url = f"{lichess_url}/api/bot/game/{partidas_em_andamento['nowPlaying'][0]['gameId']}/move/{melhor_movimento}"
                headers = {"Authorization": f"Bearer {lichess_token}"}
                response = requests.post(url, headers=headers)

                if response.status_code == 200:
                    print(f"Feito o movimento: {melhor_movimento}")
                else:
                    print(f"Falha ao fazer o movimento: {response.status_code}")
        else:
            print("Aguardando a jogada do adversário")
    else:
        print("Aguardando partida...")
    time.sleep(0.5)
