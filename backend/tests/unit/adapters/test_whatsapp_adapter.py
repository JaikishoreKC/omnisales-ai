import pytest
from app.adapters.whatsapp import WhatsAppAdapter
from app.core.gateway import OutgoingMessage, ChannelType


@pytest.mark.asyncio
async def test_whatsapp_parse_incoming():
    adapter = WhatsAppAdapter()
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "1234567890",
                        "id": "msg1",
                        "text": {"body": "Hello"}
                    }]
                }
            }]
        }]
    }

    msg = await adapter.parse_incoming(payload)

    assert msg.user_id == "1234567890"
    assert msg.message == "Hello"
    assert msg.session_id == "wa_1234567890"


@pytest.mark.asyncio
async def test_whatsapp_send_message_no_token():
    adapter = WhatsAppAdapter()
    outgoing = OutgoingMessage(
        channel=ChannelType.WHATSAPP,
        user_id="1234567890",
        message="Hello"
    )
    result = await adapter.send_message(outgoing)
    assert result is False
