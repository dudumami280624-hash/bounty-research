"""Offline target ranking: only explicitly authorized targets are eligible."""
def rank_targets(candidates):
    allowed = [x for x in candidates if x.get("official_scope_verified") is True
               and x.get("testing_authorized") is True]
    return sorted(allowed, key=lambda x: (
        bool(x.get("source_pinned")),
        bool(x.get("offline_reproducible")),
        bool(x.get("known_issue_checked"))
    ), reverse=True)
