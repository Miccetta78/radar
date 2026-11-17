"""Applica al sito le righe del Google Sheet "Radar - sorgente sito".

Colonne: tipo | id | parte | contenuto
  issue        -> id numero, contenuto = JSON del numero (spezzabile in parti)
  delete-issue -> id del numero da togliere
  file         -> id = percorso relativo nel repo, contenuto = testo del file
Le righe con stesso tipo e id vengono unite in ordine di "parte".
Errori su una riga non bloccano le altre e vengono stampati nel log.
"""
import csv
import json
import os
import sys

csv.field_size_limit(sys.maxsize)

ROOT = os.path.abspath(os.getcwd())
ISSUES = os.path.join(ROOT, "data", "issues.json")
BLOCKED = (".github/", ".git/", "CNAME")


def load_rows(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    groups = {}
    for n, r in enumerate(rows):
        r = (r + ["", "", "", ""])[:4]
        tipo, rid, parte, contenuto = (c.strip() if i < 3 else c for i, c in enumerate(r))
        if n == 0 and tipo.lower() == "tipo":
            continue
        if not tipo or not rid:
            continue
        try:
            p = int(float(parte or 1))
        except ValueError:
            p = 1
        groups.setdefault((tipo, rid), []).append((p, n, contenuto))
    out = []
    for (tipo, rid), parts in groups.items():
        parts.sort()
        out.append((tipo, rid, "".join(c for _, _, c in parts)))
    return out


def main(csv_path):
    rows = load_rows(csv_path)
    with open(ISSUES, encoding="utf-8") as f:
        issues = json.load(f)
    before = json.dumps(issues, ensure_ascii=False)
    errors = []

    for tipo, rid, contenuto in rows:
        if tipo == "issue":
            try:
                obj = json.loads(contenuto)
                if obj.get("id") != rid:
                    raise ValueError(f"id nel JSON ({obj.get('id')}) diverso da id riga")
            except Exception as e:  # noqa: BLE001
                errors.append(f"issue {rid}: {e}")
                continue
            issues = [i for i in issues if i.get("id") != rid] + [obj]
        elif tipo == "delete-issue":
            issues = [i for i in issues if i.get("id") != rid]
        elif tipo == "file":
            rel = rid.lstrip("/")
            dest = os.path.abspath(os.path.join(ROOT, rel))
            if not dest.startswith(ROOT + os.sep) or rel.startswith(BLOCKED) or rel == "data/issues.json":
                errors.append(f"file {rid}: percorso non ammesso")
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8", newline="") as f:
                f.write(contenuto)
        else:
            errors.append(f"tipo sconosciuto: {tipo} ({rid})")

    issues.sort(key=lambda i: (i.get("date", ""), i.get("number", 0)), reverse=True)
    if json.dumps(issues, ensure_ascii=False) != before:
        with open(ISSUES, "w", encoding="utf-8") as f:
            json.dump(issues, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("issues.json aggiornato:", [i.get("id") for i in issues])

    for e in errors:
        print("ERRORE:", e)
    # Gli errori vengono segnalati ma non bloccano la pubblicazione del resto.
    if errors:
        open(os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "sync_errors"), "w").write("\n".join(errors))


if __name__ == "__main__":
    main(sys.argv[1])
