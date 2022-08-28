class JustWrong(Exception):
    """Raise it if you need some help"""
    def __init__(self, message):
        self.message = message
        
        super().__init__()