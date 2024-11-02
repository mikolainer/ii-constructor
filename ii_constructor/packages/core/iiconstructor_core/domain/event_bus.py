class Event:
    """ Данные о событии """
    def __init__(self):
        pass

class EventHandler:
    """ Абстрактный обработчик события """
    @staticmethod
    def handle(ev: Event):
        """ Обрабатывает конкретное событие в `Subscriber` """
        raise NotImplementedError("Использование абстрактного класса")

class Subscriber:
    """ Интерфейс получателя событий """
    def __init__(self):
        pass

    def triggered(self, ev: Event):
        """ Раздаёт событие обработчикам `EventHandler` """
        raise NotImplementedError("Использование абстрактного класса")

class EventBus:
    """ Абстрактная шина событий """
    def __init__(self):
        pass

    def subscribe(self, sub: Subscriber):
        raise NotImplementedError("Использование абстрактного класса")

    def notify(self, ev: Event):
        raise NotImplementedError("Использование абстрактного класса")

class InmemoryEventBus(EventBus):
    __subscribers: list[Subscriber]

    def __init__(self):
        super().__init__()
        self.__subscribers = list[Subscriber]()

    def subscribe(self, sub: Subscriber):
        if issubclass(sub, Subscriber):
            self.__subscribers.append(sub)

    def notify(self, ev: Event):
        for sub in self.__subscribers:
            try:
                sub.triggered(ev)
            except Exception as e:
                print(e)

class Publisher:
    """ Интерфейс отправителя событий """
    __bus: EventBus

    def __init__(self):
        __bus = None

    def connect(self, bus: EventBus):
        """ Подключает шину для отправки событий """
        if issubclass(type(bus), EventBus):
            self.__bus = bus

    def send(self, ev: Event):
        """ Отправляет событие """
        if issubclass(type(self.__bus), EventBus):
            self.__bus.notify(ev)
