from __future__ import annotations

import sys
import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from project.rag.index import build_index


def main() -> None:
    knowledge_base_dir = ROOT / "data" / "knowledge_base"
    index_dir = ROOT / "artifacts" / "index"
    summary = build_index(knowledge_base_dir=knowledge_base_dir, index_dir=index_dir)
    timestamp = datetime.now(UTC).isoformat()
    (index_dir / "build_info.json").write_text(json.dumps({
        "last_built": timestamp,
        "documents": summary["documents"],
        "chunks": summary["chunks"],
    }, indent=2), encoding="utf-8")
    print(
        f"Built index from {summary['documents']} documents into {summary['chunks']} chunks at {index_dir}"
    )


if __name__ == "__main__":
    main()
