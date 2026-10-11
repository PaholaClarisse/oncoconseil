from unittest.mock import MagicMock


def test_scope_guard_question_hors_sujet(monkeypatch):
    from app.services import chat_service

    fake_collection = MagicMock()
    fake_collection.count.return_value = 1
    fake_collection.query.return_value = {
        "documents": [["chunk a", "chunk b", "chunk c"]],
        "distances": [[1.5, 1.6, 1.7]],
    }

    monkeypatch.setattr(chat_service, "collection", fake_collection)
    monkeypatch.setattr(chat_service, "generate_embedding", lambda question: [0.1, 0.2, 0.3])

    results = chat_service.search_relevant_chunks(
        "Quelle est la recette de la tarte aux pommes ?"
    )

    assert not chat_service.is_within_scope(results["distances"])

def test_scope_guard_question_hors_sujets(monkeypatch):
    from app.services import chat_service

    fake_collection = MagicMock()
    fake_collection.count.return_value = 1
    fake_collection.query.return_value = {
        "documents": [["chunk a", "chunk b", "chunk c"]],
        "distances": [[0.1,0.2,0.3]],
    }

    monkeypatch.setattr(chat_service, "collection", fake_collection)
    monkeypatch.setattr(chat_service, "generate_embedding", lambda question: [0.1, 0.2, 0.3])

    results = chat_service.search_relevant_chunks(
        "Quelle est la recette de la tarte aux pommes ?"
    )

    assert chat_service.is_within_scope(results["distances"])