import pytest
from app.adapters.voice import VoiceAdapter
from app.core.gateway import OutgoingMessage, ChannelType


@pytest.mark.asyncio
async def test_voice_parse_incoming():
    adapter = VoiceAdapter()
    payload = {
        "call_id": "call123",
        "from_number": "+123456789",
        "transcript": "Hello there"
    }

    msg = await adapter.parse_incoming(payload)

    assert msg.user_id == "+123456789"
    assert msg.message == "Hello there"
    assert msg.session_id == "voice_call123"


@pytest.mark.asyncio
async def test_voice_send_message_no_token():
    adapter = VoiceAdapter()
    outgoing = OutgoingMessage(
        channel=ChannelType.VOICE,
        user_id="+123",
        message="Hi",
        metadata={"call_id": "call123"}
    )
    result = await adapter.send_message(outgoing)
    assert result is False
