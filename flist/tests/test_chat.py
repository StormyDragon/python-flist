import unittest
import asyncio
from flist.fchat import FChatProtocol, FChatTransport
from flist import opcode


class TestFChatProtocol(unittest.TestCase):
    class MockTransport(FChatTransport):
        def connect(self):
            pass

        def send_message(self):
            pass

    def setUp(self):
        # The test requires a mock transport for receiving messages.
        self.mocktransport = TestFChatProtocol.MockTransport()
        self.protocol = FChatProtocol(self.mocktransport)
        self.protocol.connect()

    def test_callbacks(self):
        result = None
        def callback(message):
            nonlocal result
            self.protocol.remove_op_callback(opcode.USER_CONNECTED, callback)
            result = message
        self.protocol.add_op_callback(opcode.USER_CONNECTED, callback)
        self.mocktransport.on_message("""NLN {"status":"online","gender":"Male","identity":"Adamoraco"}""")
        self.assertIsInstance(result, dict, "The object is a dict, parsed from JSON sent over the transport.")
        self.assertEqual(result['gender'], 'Male', "The dict contains a key 'gender' containing 'Male'.")

    def test_pings(self):
        result = None
        def callback(message):
            nonlocal result
            result = message

        self.mocktransport.send_message = callback
        self.mocktransport.on_message("PIN")
        self.assertEqual(result, 'PIN', "The protocol responds to pings.")