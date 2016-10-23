import unittest

import asyncio
from unittest.mock import Mock, patch

from flist.account import Character
from flist.chat import opcode
from flist.chat.protocol import FChatProtocol
from flist.chat.transport import FChatTransport, FChatPinger, TransportErrors
from flist.fchat import Connection


class MockTransport(FChatTransport):
    def connect(self):
        self.on_open()

    def send_message(self):
        pass


class MockAccount(object):
    def __init__(self):
        self.characters = {'Adamoraco': Character('Adamoraco', self)}
        self.account = 'account'
        self.bookmarks = []
        self.friends = []

    @property
    def ticket(self):
        return "MockTicket"


class TestFChatProtocol(unittest.TestCase):
    def setUp(self):
        # The test requires a mock transport for receiving messages.
        self.mocktransport = MockTransport()
        self.protocol = FChatProtocol(self.mocktransport)
        self.protocol.connect()

    def test_callbacks(self):
        result = None

        def callback(message):
            nonlocal result
            self.protocol.remove_op_callback(opcode.USER_CONNECTED, callback)
            result = message

        self.mocktransport.on_message("""NLN {}""")
        self.assertEqual(result, None, "Callback should have been ignored.")
        self.protocol.add_op_callback(opcode.USER_CONNECTED, callback)
        self.mocktransport.on_message("""NLN {"status":"online","gender":"Male","identity":"Adamoraco"}""")
        self.assertIsInstance(result, dict, "The object is a dict, parsed from JSON sent over the transport.")
        self.assertEqual(result['gender'], 'Male', "The dict contains a key 'gender' containing 'Male'.")

        result = None
        self.mocktransport.on_message("""NLN {}""")
        self.assertEqual(result, None, "Callback should have been removed.")

    def test_pings(self):
        result = None
        def callback(message):
            nonlocal result
            result = message

        self.mocktransport.send_message = callback
        self.mocktransport.on_message("PIN")
        self.assertEqual(result, 'PIN', "The protocol responds to pings.")


class TestFChatPinger(unittest.TestCase):
    class MockFChatPinger(FChatPinger):
        def connect(self):
            self.on_open()

    class PingFailureException(Exception):
        pass

    def setUp(self):
        # The test requires a mock transport for receiving messages.
        self.mocked_loop = Mock(spec=asyncio.get_event_loop())
        self.mocked_loop.time.return_value = 0.0
        self.mocktransport = self.MockFChatPinger("localhost", loop=self.mocked_loop)
        self.protocol = FChatProtocol(self.mocktransport)
        self.protocol.connect()

    def test_pings_connection_closed(self):
        self.assertTrue(self.mocked_loop.call_later.called, "Call later must have been called.")
        (seconds, function), kwargs = self.mocked_loop.call_later.call_args
        with patch.object(self.mocktransport, 'send_message') as send_message:
            send_message.side_effect = self.PingFailureException()
            with patch.object(self.mocktransport, 'on_close') as on_close:
                with self.assertRaises(self.PingFailureException):
                    function()
                on_close.assert_called_with(*TransportErrors.connection_exception)


class TestFChat(unittest.TestCase):
    identification_procedure = [
        """IDN {"character":"Adamoraco"}""",
        """VAR {"variable":"testvar","value":42}""",
        """HLO {"message":"This is a welcome message from the server."}""",
        """CON {"count":3}""",
        """FRL {"characters":["Moar", "Natsudra", "Kira"]}""",
        """IGN {"action":"init","characters":["Litigious douchebag"]}""",
        """ADL {"ops": ["Natsudra"]}""",
        """LIS {["Teal Deer","Male","busy"],["Natsudra","Female","looking"]}""",
        """LIS {["Adamoraco","Male","online"]}""",
        """NLN {"status":"online","gender":"Male","identity":"Adamoraco"}""",
    ]

    def setUp(self):
        account = MockAccount()
        character = account.characters['Adamoraco']

        # The test requires a mock transport for receiving messages.
        self.mocktransport = MockTransport()
        self.protocol = FChatProtocol(self.mocktransport)
        self.chat = Connection(self.protocol, character)

    def test_connect(self):
        def receiver(message):
            self.assertEqual(message[:3], "IDN", "First message should be chat identification.")
            for line in self.identification_procedure:
                self.mocktransport.on_message(line)

        self.mocktransport.send_message = receiver

        future = self.chat.connect()
        self.assertIsInstance(future.result(), Connection, "Future contains connection on successful identification.")
