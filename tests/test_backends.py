from unicef_notification.backends import EmailBackend


def test_init():
    backend = EmailBackend()
    assert hasattr(backend, "send_messages")
