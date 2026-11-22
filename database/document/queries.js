// D1. Documento completo de una versión.
db.versions.findOne({_id: "VER-001"});
// D2. Versiones del mismo documento.
db.versions.find({documentId: "DOC-001"}, {_id: 1, kind: 1, revision: 1, "content.summary": 1});
// D3. Runbooks con instrucciones anidadas.
db.versions.find({kind: "RUNBOOK", "content.steps.0": {$exists: true}});
// D4. Contratos que describen un método GET.
db.versions.find({kind: "API", "content.endpoints.method": "GET"});
