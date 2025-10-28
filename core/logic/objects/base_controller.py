class BaseEntityController:
    """Basecontroller"""
    def __init__(self, main_controller):
        self.main_controller = main_controller

    def add(self, entity):
        raise NotImplementedError

    def edit(self, entity):
        raise NotImplementedError

    def remove(self, entity):
        raise NotImplementedError
