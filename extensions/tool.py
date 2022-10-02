class Tool:
    """Handle some easy but useful functions."""
    def is_int(object) -> bool:
        try:
            int(object)
        except:
            return False
        return True

    def is_exist(object, index: int) -> bool:
        try:
            object[index]
        except:
            return False
        return True