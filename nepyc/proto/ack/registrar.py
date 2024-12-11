from nepyc.proto.ack import Ack


class AcknowledgementRegistrar:
    """
    The central singleton registrar for all ACK types.
    Handles registration and lookup of ACKs and their hierarchies.
    """

    _instance = None
    _ack_types = {}

    def __new__(cls, *args, **kwargs):
        """
        This method ensures that only one instance of the class is created.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register_ack(self, full_code: bytes, ack_type: Ack):
        """
        Register an ACK type with its full code.

        Parameters:
            full_code (bytes): The full code, such as 'REJ:DUP'.
            ack_type (Ack): The ACK class to register.
        """
        self._ack_types[full_code] = ack_type

    def get_ack(self, full_code: bytes) -> Ack:
        """
        Retrieve an ACK instance by its full code, including hierarchy.

        Parameters:
            full_code (bytes): The full code, such as 'REJ:DUP'.
        
        Returns:
            Ack: The corresponding ACK instance.
        """
        if ack_type := self._ack_types.get(full_code):
            return ack_type()
        print(f"Unknown ACK type: {full_code}")
        return Ack()  # Return a generic Ack if not found

    def register_child_ack(self, parent_code: bytes, child_code: bytes, child_ack: Ack):
        """
        Register a child ACK under a parent ACK.

        Parameters:
            parent_code (bytes): The full code of the parent ACK.
            child_code (bytes): The full code of the child ACK.
            child_ack (Ack): The child ACK class to register.
        """
        if parent_ack := self.get_ack(parent_code):
            parent_ack.register_child(child_code, child_ack)


def parse_full_code(full_code: bytes):
    """
    Parse the full code into parent and child components.

    Parameters:
        full_code (bytes): The full code, e.g., 'REJ:DUP'.

    Returns:
        tuple: (parent_code, child_code)
    """
    code_parts = full_code.decode('utf-8').split(':')
    parent_code = code_parts[0]
    child_code = code_parts[1] if len(code_parts) > 1 else ''
    return parent_code, child_code

REGISTRAR = AcknowledgementRegistrar()
