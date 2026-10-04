"""
Commande de seed : indexe le corpus d'exemple s'il n'est pas déjà en base.

Pourquoi : sur une installation neuve, la base vectorielle est vide et la
première question du chat plante (erreur 500). Cette commande évite ça.

Lancement, depuis la racine du projet :
    python -m app.seed
Dans Docker :
    docker compose exec api python -m app.seed
"""
from pathlib import Path

from app.database import SessionLocal

# À VÉRIFIER : remplace ces imports par les chemins réels de TON projet.
# (les noms de fonctions viennent de ta route d'upload)
from app.models.document import Document
from app.services.document_processor import (extract_text_from_pdf,split_into_chunks,generate_embedding,)
from app.vector_db import collection

# PDF d'exemple versionné dans le dépôt (choisis un texte dont la licence
# autorise la redistribution, puisque le dépôt est public).
CORPUS_PATH = Path("data/oncologie.pdf")
CORPUS_NAME = CORPUS_PATH.name


def seed():
    db = SessionLocal()
    try:
        # ÉTAPE 1 : le corpus est-il déjà indexé ?
        # On cherche dans la table documents une ligne dont le name
        # est CORPUS_NAME. first() renvoie le document trouvé, ou None.
        existing = db.query(Document).filter(Document.name == CORPUS_NAME).first()

        if existing is not None:
            # Déjà indexé : on ne fait rien (c'est ce qui rend le seed
            # "idempotent" : le lancer 1 ou 10 fois donne le même résultat,
            # et ça évite des appels inutiles à Gemini).
            print(f"Corpus '{CORPUS_NAME}' déjà indexé, rien à faire.")
            return

        # ÉTAPE 2 : pas encore indexé -> on lit le PDF et on le découpe
        # en chunks (petits morceaux de texte).
        texte = extract_text_from_pdf(str(CORPUS_PATH))
        chunks = split_into_chunks(texte)

        # ÉTAPE 3 : enregistrer le Document dans PostgreSQL.
        # refresh() recharge l'objet pour récupérer son id généré par la base.
        new_document = Document(name=CORPUS_NAME, nombre_chunks=len(chunks))
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        # ÉTAPE 4 : indexer chaque chunk dans ChromaDB.
        # Si ça échoue en cours de route, on annule tout (Document + chunks
        # déjà écrits) pour garder PostgreSQL et ChromaDB cohérents.
        try:
            for i, chunk in enumerate(chunks):
                embedding = generate_embedding(chunk)
                collection.add(
                    ids=[f"{new_document.id}_{i}"],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"document_id": new_document.id}],
                )
        except Exception as e:
            db.delete(new_document)
            db.commit()
            collection.delete(where={"document_id": new_document.id})
            raise RuntimeError(f"Échec de l'indexation du corpus : {e}")

        print(f"Corpus '{CORPUS_NAME}' indexé : {len(chunks)} chunks.")
    finally:
        # On ferme toujours la session, même en cas d'erreur.
        db.close()


if __name__ == "__main__":
    seed()