class Oper:
    def __init__(self, fio, chat_id, que, pre_start="none", start="none", chat="none", date='none', ready = True,
                 username = 'none'):
        self.fio = fio                  # фио оп
        self.chat_id = chat_id          # его id в телеге
        self.que = que                  # когда встал в очередь
        self.pre_start = pre_start      # когда вышел в перед обедом
        self.start = start              # когда начал лп
        self.chat = chat                # когда вышел в чаты
        self.date = date                # дата этого лп
        self.username = username        # username в тг
        self.ready = ready              # готов ли для общения с ботом далее (выполнилось ли предыдуще действие)