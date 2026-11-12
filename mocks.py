from contract import Subscription, Platform, TransportType

_subscriptions: list[Subscription] = []

def add_subscription(user_id: str, platform: Platform, route: int, transport: TransportType) -> bool:
    for s in _subscriptions:
        if s.user_id == user_id and s.platform == platform and s.route == route:
            return False
    _subscriptions.append(Subscription(user_id, platform, route, transport))
    return True

def remove_subscription(user_id: str, platform: Platform, route: int) -> bool:
    global _subscriptions
    before = len(_subscriptions)
    _subscriptions = [s for s in _subscriptions if not (s.user_id == user_id and s.platform == platform and s.route == route)]
    return len(_subscriptions) < before

def list_subscriptions(user_id: str, platform: Platform) -> list[Subscription]:
    return [s for s in _subscriptions if s.user_id == user_id and s.platform == platform]