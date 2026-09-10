# Offline evaluation fixtures.
# The actual OpenAI call is intentionally not performed by default.
# Run a live evaluation only after setting OPENAI_API_KEY.

ROUTER_CASES = [
    ("What is a Docker image?", "rag"),
    ("How does Kubernetes HPA work?", "rag"),
    ("Who is Batman?", "superhero"),
    ("What are Superman's abilities?", "superhero"),
    ("Compare Kubernetes self-healing with Wolverine's regeneration.", "both"),
    ("Compare Docker containers with Iron Man's armor.", "both"),
]


def test_evaluation_fixture_is_nonempty():
    assert len(ROUTER_CASES) >= 6
