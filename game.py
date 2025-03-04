import json
from queue import Queue
from threading import Thread

from tenacity import retry

from api import API
from chatter import Chatter
from enums import Game_Status
from lichess_game import Lichess_Game


class Game(Thread):
    def __init__(self, config: dict, api: API, game_id: str) -> None:
        Thread.__init__(self)
        self.config = config
        self.api = api
        self.game_id = game_id
        self.chatter = Chatter(api, config, game_id)
        self.ping_counter = 0
        self.game_queue = Queue()
        self.is_started = False
        self.abortion_counter = 0

    def start(self):
        Thread.start(self)

    def run(self) -> None:
        game_queue_thread = Thread(target=self._watch_game_stream, daemon=True)
        game_queue_thread.start()

        while True:
            event = self.game_queue.get()

            if event['type'] == 'gameFull':
                if not self.is_started:
                    print(f'Game "{self.game_id}" was started.')
                    self.lichess_game = Lichess_Game(self.api, event, self.config)
                    self.is_started = True
                else:
                    self.lichess_game.update(event['state'])

                if self.lichess_game.is_our_turn():
                    self._make_move()
                else:
                    self.lichess_game.start_pondering()
            elif event['type'] == 'gameState':
                self.ping_counter = 0
                updated = self.lichess_game.update(event)

                if self.lichess_game.status != Game_Status.STARTED:
                    print(self.lichess_game.get_result_message(event.get('winner')))
                    break

                if self.lichess_game.is_game_over():
                    continue

                if self.lichess_game.is_our_turn() and updated:
                    self._make_move()
            elif event['type'] == 'chatLine':
                self.chatter.handle_chat_message(event, self.lichess_game)
            elif event['type'] == 'opponentGone':
                continue
            elif event['type'] == 'ping':
                self.ping_counter += 1

                if self.ping_counter >= 10 and self.lichess_game.is_abortable():
                    print('Aborting game ...')
                    self.api.abort_game(self.game_id)
                    self.abortion_counter += 1

                    if self.abortion_counter >= 3:
                        break
            elif event['type'] == 'endOfStream':
                print('Game stream ended unexpectedly.')
                break
            else:
                print(event)

        self.lichess_game.end_game()

    def _make_move(self) -> None:
        uci_move, offer_draw, resign = self.lichess_game.make_move()
        if resign:
            self.api.resign_game(self.game_id)
        else:
            self.api.send_move(self.game_id, uci_move, offer_draw)
            self.chatter.print_eval(self.lichess_game)

    @retry
    def _watch_game_stream(self) -> None:
        game_stream = self.api.get_game_stream(self.game_id)
        for line in game_stream:
            if line:
                event = json.loads(line.decode('utf-8'))
            else:
                event = {'type': 'ping'}
            self.game_queue.put_nowait(event)

        self.game_queue.put_nowait({'type': 'endOfStream'})
