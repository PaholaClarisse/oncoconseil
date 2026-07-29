def test_scope_guard_question_hors_sujet():
    from app.services.chat_service import is_within_scope, search_relevant_chunks

    results = search_relevant_chunks("Quelle est la recette de la tarte aux pommes ?")
    assert is_within_scope(results["distances"]) == False