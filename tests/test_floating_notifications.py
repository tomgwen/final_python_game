from floating_notifications import FloatingNotificationManager


def test_notifications_keep_four_and_expire():
    manager = FloatingNotificationManager()
    for index in range(5):
        manager.add(f"message {index}", now_ms=0)
    assert [item.text for item in manager.notifications] == [
        "message 1",
        "message 2",
        "message 3",
        "message 4",
    ]
    manager.update(3500)
    assert manager.notifications == []


def test_log_sync_only_adds_new_rolling_message():
    manager = FloatingNotificationManager()
    manager.sync_from_logs(["a", "b", "c"], now_ms=0)
    manager.sync_from_logs(["b", "c", "d"], now_ms=10)
    assert [item.text for item in manager.notifications] == ["a", "b", "c", "d"]
