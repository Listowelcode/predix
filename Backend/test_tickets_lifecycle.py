from types import SimpleNamespace

from routes.tickets import ticket_matches_exhausted


finished = SimpleNamespace(match=SimpleNamespace(status="FINISHED"))
live = SimpleNamespace(match=SimpleNamespace(status="LIVE"))
missing_match = SimpleNamespace(match=None)

assert ticket_matches_exhausted([finished, finished]) is True
assert ticket_matches_exhausted([finished, live]) is False
assert ticket_matches_exhausted([finished, missing_match]) is False
assert ticket_matches_exhausted([]) is False

print("ticket lifecycle tests passed")
