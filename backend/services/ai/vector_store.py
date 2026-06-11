import os
from typing import List

import chromadb
from chromadb.config import Settings

from apps.accounts.models import Customer
from apps.compute.models import VirtualMachine
from apps.billing.models import Invoice
from apps.audit.models import AuditLog


class VectorIndexer:
    def __init__(self, persist_dir: str | None = None) -> None:
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "/data/chroma")
        self.client = chromadb.Client(Settings(persist_directory=self.persist_dir))
        self.collection = self.client.get_or_create_collection("pico_project")

    def _docs_from_models(self) -> List[dict]:
        docs = []
        for c in Customer.objects.all():
            docs.append({"id": f"customer:{c.id}", "text": f"Customer {c.company_name} {c.user.email}", "meta": {"type": "customer", "id": c.id}})
        for vm in VirtualMachine.objects.select_related("customer", "package").all():
            docs.append({"id": f"vm:{vm.id}", "text": f"VM {vm.name} status={vm.status} package={vm.package.name} ip={vm.ip_address}", "meta": {"type": "vm", "id": vm.id}})
        for inv in Invoice.objects.select_related("customer", "vm").all():
            docs.append({"id": f"invoice:{inv.id}", "text": f"Invoice {inv.invoice_number} amount={inv.amount} status={inv.status}", "meta": {"type": "invoice", "id": inv.id}})
        for a in AuditLog.objects.all():
            docs.append({"id": f"audit:{a.id}", "text": f"Audit {a.action} {a.description}", "meta": {"type": "audit", "id": a.id}})
        return docs

    def index_all(self) -> None:
        docs = self._docs_from_models()
        if not docs:
            return
        ids = [d["id"] for d in docs]
        documents = [d["text"] for d in docs]
        metadatas = [d["meta"] for d in docs]
        try:
            self.client.reset()
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection("pico_project")
        self.collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def query(self, text: str, n_results: int = 5):
        return self.collection.query(query_texts=[text], n_results=n_results)

    def query_similar(self, text: str, n_results: int = 5) -> List[dict]:
        result = self.collection.query(query_texts=[text], n_results=n_results, include=["documents", "metadatas"])
        docs = result.get("documents", [[]])[0] if result else []
        metas = result.get("metadatas", [[]])[0] if result else []
        items = []
        for document, metadata in zip(docs, metas):
            items.append({"document": document, "meta": metadata})
        return items
