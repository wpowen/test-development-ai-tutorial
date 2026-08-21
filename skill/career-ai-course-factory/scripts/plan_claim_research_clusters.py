#!/usr/bin/env python3
"""Fail-closed, read-only planner for clustered claim research."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator
from build_claim_source_manifest import validate_freshness

ROUTE_BY_CLASS = {"LOCAL-DETERMINISTIC":"LOCAL-VERIFY","STABLE-DEFINITION":"EXTERNAL-RESEARCH","SHARED-MECHANISM":"EXTERNAL-RESEARCH","VENDOR-VERSION":"EXTERNAL-RESEARCH","NUMERIC-STATISTICAL":"EXTERNAL-RESEARCH","SECURITY-AUTHORITY":"EXTERNAL-RESEARCH","FAILURE-OPERATIONS":"EXTERNAL-RESEARCH","TEACHING-PROFESSIONAL":"TEACHING-VALIDATION","TARGET-EMPIRICAL":"TARGET-EVIDENCE"}
CLASSES = tuple(ROUTE_BY_CLASS)
ROUTES = tuple(dict.fromkeys(ROUTE_BY_CLASS.values())) + ("BLOCKED-UNCLASSIFIED",)
CANONICAL_IDENTITY_FIELDS = ("subject", "predicate", "object", "type", "scope", "version", "time-boundary", "vendor", "environment", "population", "region-language", "authority-risk", "required-dimensions", "execution-contract")
UNKNOWN_IDENTITY_VALUES = {"", "unknown", "unknown-explicit", "not-specified", "not-specified-explicit", "not_specified", "not-specified"}
CLUSTER_QUESTIONS = {"K01":"How are terms, system boundaries, and traditional baselines defined?","K02":"How do lifecycle roles, artifacts, decisions, and failure cost enter professional work?","K03":"What are model behavior and AI API protocol semantics and limits?","K04":"How do evaluation, Oracle, and statistical inference support trustworthy conclusions?","K05":"How do knowledge sources, retrieval, data quality, conflict, and permissions affect results?","K06":"How do agents, tools, state, retries, handoffs, and side effects behave?","K07":"How are security, privacy, governance, and human authorization controlled?","K08":"How do performance, capacity, cost, and reliability constrain a system?","K09":"Can a conclusion be traced to inputs, versions, traces, and accountable owners?","K10":"How do platform, integration, client, and environment differences affect testing?","K11":"What evidence supports career, organization, teaching, and transfer claims?","K12":"How do factory, research, evidence, and publication contracts flow reliably?"}
ALIASES = {"local":"LOCAL-DETERMINISTIC","local-implementation":"LOCAL-DETERMINISTIC","fixture":"LOCAL-DETERMINISTIC","fixture-behavior":"LOCAL-DETERMINISTIC","stable-definition":"STABLE-DEFINITION","external-technical":"STABLE-DEFINITION","external-technical-fact":"STABLE-DEFINITION","shared-mechanism":"SHARED-MECHANISM","empirical-generalization":"SHARED-MECHANISM","vendor-version":"VENDOR-VERSION","numeric-statistical":"NUMERIC-STATISTICAL","security-authority":"SECURITY-AUTHORITY","failure-operations":"FAILURE-OPERATIONS","teaching-professional":"TEACHING-PROFESSIONAL","course-teaching":"TEACHING-PROFESSIONAL","target-empirical":"TARGET-EMPIRICAL","target-system":"TARGET-EMPIRICAL"}

def norm(value: Any) -> str: return re.sub(r"\s+", " ", str(value if value is not None else "").strip().lower())
def digest(value: Any) -> str: return "sha256:" + hashlib.sha256(norm(value).encode()).hexdigest()
def file_digest(path: Path) -> str: return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
def _first(c: dict[str, Any], *keys: str) -> str:
    for k in keys:
        if c.get(k) is not None and str(c.get(k, "")).strip(): return str(c[k]).strip()
    return ""

def _explicit_class(c: dict[str, Any]) -> tuple[str | None, str]:
    values = []
    for key in ("evidence_class","evidence_route","route"):
        if c.get(key) is None or not norm(c[key]): continue
        value=norm(c[key]); normalized=ALIASES.get(value,value.upper())
        if normalized in ROUTE_BY_CLASS.values():
            if c.get("evidence_class") and ROUTE_BY_CLASS.get(ALIASES.get(norm(c["evidence_class"]),norm(c["evidence_class"]).upper())) != normalized: return None, "conflicting explicit route"
            continue
        values.append(normalized)
    if not values: return None, ""
    if len(set(values)) != 1 or values[0] not in CLASSES: return None, "conflicting or unknown explicit evidence class"
    return values[0], "explicit normalized evidence class"

def classify_claim(c: dict[str, Any]) -> tuple[str, str]:
    explicit, reason = _explicit_class(c)
    if reason: return explicit or "UNCLASSIFIED", reason
    text = norm(" ".join(str(c.get(k, "")) for k in ("statement","scope","claim_type","subject","predicate","object")))
    if re.search(r"(?:not|no|without|never|cannot|未|无|不是|不含)\s+(?:production|target|live|真实|生产|目标)|(?:production|target|live|真实|生产|目标)\s+(?:not|no|without|never|cannot|未|无|不是|不含|unavailable|unknown|unproven)", text): return "UNCLASSIFIED", "negated target wording requires explicit class"
    if re.search(r"target[- ]system|production|live provider|真实模型|企业|生产|当前系统|目标系统", text): return "TARGET-EMPIRICAL", "target indicator"
    if re.search(r"security|privacy|acl|authorization|permission|tenant|compliance|prompt injection|越权|隐私|权限|安全|合规|授权", text): return "SECURITY-AUTHORITY", "security/authority indicator"
    if _first(c,"vendor","tool","provider","version","version_scope","vendor_version") or re.search(r"\b(api|sdk|provider|model|vendor|deprecated|deprecation)\b|版本|弃用|限额", text): return "VENDOR-VERSION", "vendor/version indicator"
    if re.search(r"(?:\d+(?:\.\d+)?\s*%|\b(?:n|p|r|ci|slo|p\d{2})\s*[=<>≤≥]|threshold|latency|throughput|cost|比例|阈值|样本|显著|性能|成本|延迟)", text): return "NUMERIC-STATISTICAL", "number/threshold indicator"
    if re.search(r"fixture|synthetic|故障注入|fixture-tested|样例|演示数据", text): return "LOCAL-DETERMINISTIC", "fixture is local evidence"
    if re.search(r"course|teaching|lesson|learner|教学|课程|学习者|练习|默认值|design parameter", text): return "TEACHING-PROFESSIONAL", "teaching indicator"
    if re.search(r"repository|\bgit\b|schema|validator|runner|projection|hash|本仓库|代码|实现|验证器|阻断|blocked", text): return "LOCAL-DETERMINISTIC", "local artifact indicator"
    if re.search(r"usually|typically|most|industry|improves|effective|普遍|通常|大多数|行业|提升|效果", text): return "SHARED-MECHANISM", "empirical generalization requires external research"
    if norm(_first(c,"claim_type","claim_type_family","type")) in {"definition","mechanism","protocol","standard","terminology","concept"}: return "STABLE-DEFINITION", "stable technical claim type"
    return "UNCLASSIFIED", "no deterministic rule matched"

def canonical_fields(c: dict[str, Any], evidence_class: str) -> dict[str, str]:
    predicate=norm(_first(c,"predicate")) or "NOT-SPECIFIED"; subject=norm(_first(c,"subject")) or "NOT-SPECIFIED"; obj=norm(_first(c,"object")) or "NOT-SPECIFIED"; typ=norm(_first(c,"claim_type_family","claim_type","type")) or "NOT-SPECIFIED"
    # Canonical identity is semantic fields, not page/instructional wording.
    semantic_statement="|".join((predicate, subject, obj, typ))
    dimensions=c.get("required_dimensions")
    normalized_dimensions="|".join(sorted(norm(item) for item in dimensions)) if isinstance(dimensions,list) and dimensions else "NOT-SPECIFIED"
    return {"statement":semantic_statement,"predicate":predicate,"subject":subject,"object":obj,"scope":norm(_first(c,"scope","scope_digest")) or "NOT-SPECIFIED","type":typ,"version":norm(_first(c,"version_scope","version","vendor_version")) or "NOT-SPECIFIED","time-boundary":norm(_first(c,"time_boundary")) or "NOT-SPECIFIED","vendor":norm(_first(c,"vendor_or_tool","vendor","tool","provider")) or "NOT-SPECIFIED","environment":norm(_first(c,"environment_scope","environment")) or "NOT-SPECIFIED","population":norm(_first(c,"population_scope","population")) or "NOT-SPECIFIED","region-language":norm(_first(c,"region_language","region-language","locale")) or "NOT-SPECIFIED","authority-risk":norm(_first(c,"authority_risk","risk")) or "NOT-SPECIFIED","required-dimensions":normalized_dimensions,"execution-contract":norm(_first(c,"execution_contract","_inventory_execution_contract")) or "not-specified","evidence-class":evidence_class}

def canonical_identity_complete(fields: dict[str, str]) -> bool:
    """Return whether an external claim is safe to use for canonical deduplication."""
    for field in CANONICAL_IDENTITY_FIELDS:
        value = norm(fields.get(field, ""))
        if value in UNKNOWN_IDENTITY_VALUES:
            return False
    return True

def canonical_key(f: dict[str, str]) -> dict[str, Any]:
    # Missing cluster identity is an explicit unclassified state. Never
    # default it to a researchable cluster before independent review.
    f = {**{"cluster":"K00","route":ROUTE_BY_CLASS.get(f.get("evidence-class",""),"BLOCKED-UNCLASSIFIED"),"source-family-policy":"unknown"}, **f}
    names = ("statement","scope","version","time-boundary","vendor","environment","region-language","authority-risk","type","population","predicate","required-dimensions","execution-contract","cluster","evidence-class","route","source-family-policy")
    ordered = [f[k] for k in names]
    normalized = {"normalized_statement":f["statement"],"normalized_scope":f["scope"],"normalized_version":f["version"],"normalized_time_boundary":f["time-boundary"],"normalized_vendor":f["vendor"],"normalized_environment":f["environment"],"normalized_region":f["region-language"],"normalized_risk":f["authority-risk"],"normalized_claim_type":f["type"],"normalized_population":f["population"],"normalized_predicate":f["predicate"],"normalized_required_dimensions":f["required-dimensions"],"normalized_execution_contract":f["execution-contract"],"normalized_cluster":f["cluster"],"normalized_evidence_class":f["evidence-class"],"normalized_route":f["route"],"normalized_source_family_policy":f["source-family-policy"]}
    normalized["component_digests"] = {"statement":digest(f["statement"]),"scope":digest(f["scope"]),"version":digest(f["version"]),"time_boundary":digest(f["time-boundary"]),"vendor":digest(f["vendor"]),"environment":digest(f["environment"]),"region":digest(f["region-language"]),"risk":digest(f["authority-risk"]),"claim_type":digest(f["type"]),"population":digest(f["population"]),"predicate":digest(f["predicate"]),"required_dimensions":digest(f["required-dimensions"]),"execution_contract":digest(f["execution-contract"]),"cluster":digest(f["cluster"]),"evidence_class":digest(f["evidence-class"]),"route":digest(f["route"]),"source_family_policy":digest(f["source-family-policy"])}
    normalized["key_digest"] = "sha256:" + hashlib.sha256("\0".join(ordered).encode()).hexdigest()
    return normalized

def _cluster(c: dict[str, Any], ec: str) -> str:
    if re.match(r"^K(?:0[1-9]|1[0-2])$", str(c.get("primary_cluster_id",""))): return str(c["primary_cluster_id"])
    # K00 is an explicit unassigned sentinel. It is intentionally rejected by
    # the current cluster-map schema until the schema permits blocked claims to
    # carry an unassigned cluster without masking the missing registry mapping.
    return "K00"

def load_source(path: Path) -> list[dict[str, Any]]:
    data=json.loads(path.read_text(encoding="utf-8")); rows=data.get("claims") if isinstance(data,dict) else data
    if rows is None and isinstance(data,dict): rows=data.get("items") or data.get("authors")
    if not isinstance(rows,list): raise ValueError(f"source {path} must contain a claims/items/authors array")
    out=[]
    for i,row in enumerate(rows):
        if not isinstance(row,dict): raise ValueError(f"source {path} row {i} must be an object")
        if not str(row.get("claim_id") or row.get("id") or "").strip(): raise ValueError(f"source {path} row {i} missing claim_id/id")
        if not str(row.get("statement") or row.get("claim") or "").strip(): raise ValueError(f"source {path} row {i} missing statement")
        item=dict(row)
        if isinstance(data, dict):
            item["_inventory_page_id"] = data.get("page_id") or data.get("topic_id") or data.get("id")
            item["_inventory_execution_contract"] = data.get("execution_contract")
        out.append(item)
    return out

def _inside(root: Path, path: Path) -> bool:
    try: path.relative_to(root); return path != root
    except ValueError: return False

def plan(package_root: Path, sources: list[Path], output: Path | None = None, source_root: Path | None = None, classification_overlay: Path | None = None) -> dict[str, Any]:
    root=package_root.resolve(strict=True)
    if not root.is_dir(): raise ValueError("package root must be a directory")
    source_base=(source_root or package_root).resolve(strict=True)
    if not source_base.is_dir(): raise ValueError("source root must be a directory")
    paths=[]
    for original in sources:
        path=(source_base/original if not original.is_absolute() else original).resolve(strict=True)
        if not _inside(source_base,path): raise ValueError(f"source escapes source root: {original}")
        if not path.is_file(): raise ValueError(f"source must be a regular file: {path}")
        paths.append(path)
    out=None
    if output is not None:
        out=(root/output if not output.is_absolute() else output).resolve()
        if not _inside(root,out): raise ValueError("output escapes package root")
        if out in paths: raise ValueError("output must not overwrite an input source")
    raw=[]; seen=set()
    for path in paths:
        for index,c in enumerate(load_source(path)):
            cid=str(c.get("claim_id") or c.get("id"))
            if cid in seen: raise ValueError(f"duplicate claim id: {cid}")
            seen.add(cid); raw.append((c,path,index))
    # Classification is an independently reviewed artifact. Absence is a
    # blocker, never implicit approval from heuristic classification.
    overlay_pending=True; overlay_digest=None
    if classification_overlay is not None:
        op=(source_base/classification_overlay if not classification_overlay.is_absolute() else classification_overlay).resolve(strict=True)
        if not _inside(source_base,op): raise ValueError("classification overlay escapes source root")
        if out is not None and out == op: raise ValueError("output must not overwrite classification overlay")
        overlay=json.loads(op.read_text(encoding="utf-8")); overlay_digest=file_digest(op)
        bound_manifest_path = overlay.get("claim_source_manifest_path")
        bound_manifest_digest = overlay.get("claim_source_manifest_digest")
        if bound_manifest_path or bound_manifest_digest:
            if not bound_manifest_path or not bound_manifest_digest:
                raise ValueError("classification overlay source-manifest binding is incomplete")
            manifest_path = (source_base / str(bound_manifest_path)).resolve(strict=True)
            if not _inside(source_base, manifest_path) or file_digest(manifest_path) != bound_manifest_digest:
                raise ValueError("classification overlay claim-source-manifest digest is stale")
            manifest_document = json.loads(manifest_path.read_text(encoding="utf-8"))
            freshness_errors = validate_freshness(manifest_document, source_base)
            if freshness_errors:
                raise ValueError("classification overlay source-manifest freshness failed: " + "; ".join(freshness_errors[:5]))
        schema_path=Path(__file__).resolve().parents[1]/"assets/schemas/classification-overlay.v1.schema.json"; schema=json.loads(schema_path.read_text(encoding="utf-8")); schema_errors=list(Draft202012Validator(schema).iter_errors(overlay))
        if schema_errors: raise ValueError("classification overlay schema invalid: "+schema_errors[0].message)
        if overlay.get("generated_by")==overlay.get("reviewed_by"): raise ValueError("classification overlay requires distinct generated_by/reviewed_by")
        proposed=overlay.get("claims") if isinstance(overlay,dict) else None
        if not isinstance(proposed,list): raise ValueError("classification overlay must contain claims array")
        if overlay.get("claim_count") != len(proposed): raise ValueError("classification overlay claim_count mismatch")
        if sorted(overlay.get("source_inventory_digests",[])) != sorted(file_digest(p) for p in paths): raise ValueError("classification overlay source inventory digests do not match inputs")
        ids=[str(x.get("claim_id")) for x in proposed if isinstance(x,dict)]; source_ids={str(c.get("claim_id") or c.get("id")) for c,_,_ in raw}
        if len(ids)!=len(set(ids)) or set(ids)!=source_ids: raise ValueError("classification overlay must cover claim IDs exactly once")
        by_id={str(x["claim_id"]):x for x in proposed}
        if overlay.get("review_status")=="approved":
            digest_fields=("subject","predicate","object","claim_type_family","scope","version","time_boundary","vendor_or_tool","environment","population","region_language","authority_risk","required_dimensions","execution_contract","local_validation_locators","target_evidence_required")
            for item in proposed:
                fdig=item.get("field_digests", {})
                for field in digest_fields:
                    value=item.get(field); material=json.dumps(value, sort_keys=True, separators=(",",":"), ensure_ascii=False) if isinstance(value,(list,dict,bool)) else str(value)
                    if fdig.get(field) != digest(material): raise ValueError(f"classification overlay field digest mismatch: {item['claim_id']}:{field}")
        for i,(c,p,n) in enumerate(raw):
            c=dict(c); c.update({k:v for k,v in by_id[str(c.get("claim_id") or c.get("id"))].items() if k in {"evidence_class","route","risk","primary_cluster_id","related_cluster_ids","source_family_policy","subject","predicate","object","claim_type_family","scope","version","time_boundary","vendor_or_tool","environment","population","region_language","authority_risk","required_dimensions","execution_contract","local_validation_locators","target_evidence_required","classification_reason"}}); raw[i]=(c,p,n)
        overlay_pending=not (overlay.get("review_status")=="approved" and overlay.get("independent_review") is True and overlay.get("approved_at") and not any(x.get("evidence_class")=="UNCLASSIFIED" or x.get("risk")=="unknown" for x in proposed))
    rows=[]; identity_blocked_units=0
    for c,path,index in raw:
        ec,reason=classify_claim(c); cluster=_cluster(c,ec)
        if not re.match(r"^K(?:0[1-9]|1[0-2])$", str(c.get("primary_cluster_id",""))): ec,reason="UNCLASSIFIED","missing explicit primary cluster registry assignment"
        if c.get("target_evidence_required") is True and ec != "UNCLASSIFIED":
            ec,reason="TARGET-EMPIRICAL","claim explicitly requires target evidence"
        route=ROUTE_BY_CLASS.get(ec,"BLOCKED-UNCLASSIFIED"); fields=canonical_fields(c,ec); fields.update({"cluster":cluster,"route":route,"source-family-policy":norm(c.get("source_family_policy")) or "unknown"})
        # Never collapse externally researched claims when semantic identity is
        # incomplete. A short or similar sentence is not evidence that two
        # claims share scope, version, population, or authority conditions.
        if route == "EXTERNAL-RESEARCH" and not canonical_identity_complete(fields):
            identity_blocked_units += 1
            ec, route, reason = "UNCLASSIFIED", "BLOCKED-UNCLASSIFIED", "canonical identity fields are incomplete; independent audit required before deduplication"
            fields = canonical_fields(c, ec)
            fields.update({"cluster": cluster, "route": route, "source-family-policy": norm(c.get("source_family_policy")) or "unknown"})
        key=canonical_key(fields); cid=str(c.get("claim_id") or c.get("id")); fd=file_digest(path)
        risk=norm(c.get("risk")); valid_risk=risk in {"low","medium","high","critical"}; if_risk=risk if valid_risk else "unknown"
        if not valid_risk: ec,route,reason="UNCLASSIFIED","BLOCKED-UNCLASSIFIED","missing or invalid risk"; fields["evidence-class"]=ec; fields["route"]=route; fields["source-family-policy"]="unknown:"+fd+":"+str(index); key=canonical_key(fields)
        if route=="BLOCKED-UNCLASSIFIED" and fields["source-family-policy"]=="unknown": fields["source-family-policy"]="unknown:"+fd+":"+str(index); key=canonical_key(fields)
        status="MAPPED" if route!="BLOCKED-UNCLASSIFIED" else "BLOCKED"
        row={"claim_id":cid,"statement":str(c.get("statement") or c.get("claim")),"claim_type":_first(c,"claim_type","claim_type_family","type") or "unspecified","risk":if_risk,"primary_cluster_id":cluster,"evidence_class":ec,"route":route,"status":status,"execution_contract":fields["execution-contract"],"required_dimensions":sorted(str(x) for x in c.get("required_dimensions",[]) if str(x).strip()),"time_boundary":fields["time-boundary"],"vendor_or_tool":fields["vendor"],"identity_fingerprint":digest(cid+"\0"+str(c.get("statement") or c.get("claim"))+"\0"+_first(c,"scope")),"request_fingerprint":digest(json.dumps(key,sort_keys=True)),"canonical_claim_key":key,"digests":{"scope_digest":digest(fields["scope"]),"version_digest":digest(fields["version"]),"environment_digest":digest(fields["environment"]),"region_digest":digest(fields["region-language"]),"risk_digest":digest(fields["authority-risk"])},"source_locators":[{"locator_id":f"source-{index}","kind":"local","uri_or_path":str(path),"digest":fd}],"origin":{"origin_kind":"claim-inventory","origin_id":path.stem,"origin_path":str(path),"origin_digest":fd},"cannot_prove":["This dry-run does not prove provider research, target behavior, saturation, or reuse."],"invalidation":{"status":"current","triggers":["statement-change","scope-change","version-change","environment-change","region-change","risk-change","source-retraction","counterevidence-change","contract-change","artifact-change","target-state-change"],"invalidates_node_ids":[f"N1-{cid}",f"N2-{cid}",f"N4-{cid}"]},"_fields":fields,"_reason":reason,"_tokens":set(re.findall(r"[\w-]+"," ".join(fields.values())))}
        if route=="TARGET-EVIDENCE": row["target_evidence"]={"required":True,"status":"UNKNOWN","evidence_refs":[],"cannot_substitute_with":["external-web","fixture","local-static-check","shared-bundle"]}
        rows.append(row)
    buckets={}
    for i,row in enumerate(rows):
        f=row["_fields"]; bucket=(row["route"],f["version"],f["environment"])
        for token in sorted(row["_tokens"]): buckets.setdefault((*bucket,token),[]).append(i)
    candidates=[]; no_reuse=[]
    for i,left in enumerate(rows):
        if left["route"]=="BLOCKED-UNCLASSIFIED": continue
        f=left["_fields"]
        token_buckets=[]
        for token in left["_tokens"]:
            bucket=buckets.get((left["route"],f["version"],f["environment"],token),[])
            if bucket:
                token_buckets.append((len(bucket), token, bucket))
        candidate_set=set()
        # Prefer rare shared tokens; this avoids expanding common template
        # words across the entire 40k-claim draft corpus.
        for _,_,bucket in sorted(token_buckets, key=lambda item: (item[0], item[1]))[:8]:
            for j in bucket:
                if j>i:
                    candidate_set.add(j)
                    if len(candidate_set)>=60:
                        break
            if len(candidate_set)>=60:
                break
        indices=sorted(candidate_set)[:60]
        # Full-corpus drafts can contain tens of thousands of repeated
        # template sentences.  Use a cheap token-overlap shortlist before
        # invoking SequenceMatcher; exact canonical keys always remain
        # eligible and are never filtered by this optimization.
        shortlist=[]
        left_tokens=left["_tokens"]
        for j in indices:
            right=rows[j]; exact=left["canonical_claim_key"]["key_digest"]==right["canonical_claim_key"]["key_digest"]
            if exact:
                shortlist.append((1.0,j,True)); continue
            right_tokens=right["_tokens"]
            union=left_tokens | right_tokens
            overlap=(len(left_tokens & right_tokens) / len(union)) if union else 0.0
            if overlap >= 0.45:
                shortlist.append((overlap,j,False))
        for _,j,exact in sorted(shortlist, key=lambda item: (-item[0], item[1]))[:20]:
            right=rows[j]
            sim=1.0 if exact else SequenceMatcher(None,left["statement"],right["statement"]).ratio()
            if exact or sim>=.86:
                dimensions=("scope","version","time-boundary","environment","region-language","authority-risk","population","predicate","vendor","type","subject","object","required-dimensions","execution-contract","evidence-class","route","cluster","source-family-policy")
                mismatches=[d for d in dimensions if left["_fields"].get(d,"NOT-SPECIFIED")=="NOT-SPECIFIED" or right["_fields"].get(d,"NOT-SPECIFIED")=="NOT-SPECIFIED" or left["_fields"].get(d)!=right["_fields"].get(d)]
                item={"claim_ids":[left["claim_id"],right["claim_id"]],"kind":"EXACT" if exact else "NEAR","similarity":round(sim,6),"identity_status":"canonical-semantic-equal" if exact else "unknown"}
                if mismatches:
                    item.update({"reuse_decision":"NO-REUSE","reason":"unknown or incompatible transfer dimensions: "+", ".join(mismatches)}); no_reuse.append(item)
                else:
                    item["reuse_decision"]="UNDECIDED"; candidates.append(item)
    # The versioned map schema intentionally has no UNCLASSIFIED enum. Keep every
    # raw claim in the planner result/manifest, while the schema-bound map carries
    # only routable claims; BLOCKED status and counts preserve the missing rows.
    units={}
    for row in rows: units.setdefault(row["canonical_claim_key"]["key_digest"], []).append(row)
    for unit_digest, members in units.items():
        unit_id="CU-"+unit_digest.split(":",1)[1][:16]
        for position, row in enumerate(members):
            row["canonical_unit_id"]=unit_id; row["canonical_unit_role"]="anchor" if position==0 else "member"
    public=[{k:v for k,v in r.items() if not k.startswith("_") and v is not None} for r in rows]
    map_public=public
    inventory_digest="sha256:"+hashlib.sha256("\n".join(file_digest(p) for p in paths).encode()).hexdigest()
    inventory_page_ids={str(c.get("_inventory_page_id") or c.get("page_id") or c.get("source_page") or c.get("topic_id") or path) for c,path,_ in raw}; page_ids=set(inventory_page_ids)
    catalog_digest=None; coverage_source="inventory-derived"
    if source_root is not None:
        manifest_candidate=source_base/"research/catalog-manifest.json"
        if manifest_candidate.exists():
            manifest_path=manifest_candidate.resolve(strict=True)
            if not _inside(source_base, manifest_path): raise ValueError("catalog manifest escapes source root")
            catalog=json.loads(manifest_path.read_text(encoding="utf-8")); scope=catalog.get("release_scope") if isinstance(catalog.get("release_scope"),dict) else {}; declared=scope.get("promised_page_ids") or catalog.get("promised_page_ids") or catalog.get("page_ids") or catalog.get("pages")
            if isinstance(declared,list) and declared:
                page_ids={str(x) for x in declared}; catalog_digest=file_digest(manifest_path); coverage_source="catalog-manifest"
    expected_pages=sorted(page_ids); covered_pages=sorted(page_ids & inventory_page_ids); missing_pages=sorted(page_ids-inventory_page_ids); unexpected_pages=sorted(inventory_page_ids-page_ids)
    page_set_digest="sha256:"+hashlib.sha256(json.dumps({"expected":expected_pages,"covered":covered_pages,"missing":missing_pages,"unexpected":unexpected_pages},sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    page_coverage={"coverage_source":coverage_source,"catalog_manifest_digest":catalog_digest,"page_set_digest":page_set_digest,"expected_page_ids":expected_pages,"covered_page_ids":covered_pages,"missing_page_ids":missing_pages,"unexpected_page_ids":unexpected_pages}
    overlay_binding=overlay_digest or "none"; coverage_binding=catalog_digest or page_set_digest
    map_doc={"schema_version":"claim-cluster-map.v1","map_id":"map-"+hashlib.sha256((inventory_digest+overlay_binding+coverage_binding).encode()).hexdigest()[:16],"generated_at":"dry-run","inventory_digest":inventory_digest,"cluster_registry_version":"clusters.v1","page_coverage":page_coverage,"clusters":[{"cluster_id":k,"canonical_question":v,"cluster_digest":digest(k+"\0"+v)} for k,v in CLUSTER_QUESTIONS.items()],"claims":map_public}
    if overlay_digest: map_doc["classification_overlay_digest"]=overlay_digest
    map_digest="sha256:"+hashlib.sha256(json.dumps(map_doc,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    pages_expected=len(expected_pages); pages_with_claim_inventory=len(covered_pages)
    ext=[r for r in rows if r["route"]=="EXTERNAL-RESEARCH"]; blocked=sum(r["route"]=="BLOCKED-UNCLASSIFIED" for r in rows); counts={"pages_expected":pages_expected,"pages_with_claim_inventory":pages_with_claim_inventory,"missing_page_count":len(missing_pages),"unexpected_page_count":len(unexpected_pages),"pages_total":pages_expected,"claims_total":len(rows),"eligible_external_units_before":len(ext),"canonical_external_units_after":len({r["canonical_claim_key"]["key_digest"] for r in ext}),"local_units":sum(r["route"]=="LOCAL-VERIFY" for r in rows),"target_units":sum(r["route"]=="TARGET-EVIDENCE" for r in rows),"teaching_units":sum(r["route"]=="TEACHING-VALIDATION" for r in rows),"blocked_units":blocked,"identity_blocked_units":identity_blocked_units}
    route_counts={r:sum(x["route"]==r for x in rows) for r in ROUTES}
    ready=blocked==0 and not overlay_pending and not missing_pages and not unexpected_pages and coverage_source=="catalog-manifest"
    manifest={"schema_version":"research-route-dry-run-manifest.v1","dry_run_id":"dry-"+hashlib.sha256((inventory_digest+page_set_digest).encode()).hexdigest()[:16],"generated_at":"dry-run","input_inventory_digests":[file_digest(p) for p in paths],"map_digest":map_digest,"page_coverage":page_coverage,**({"classification_overlay_digest":overlay_digest} if overlay_digest else {}),"status":"READY" if ready else "BLOCKED","counts":counts,"routes":route_counts,"reuse":{"DIRECT-REUSE":0,"SOURCE-REUSE-DELTA":0,"NO-REUSE":0,"undecided_candidate_count":len(candidates),"no_reuse_candidate_count":len(no_reuse),"audited_decision_count":0},"invalidation":{"current":len(rows),"superseded":0,"invalid":0,"invalidation_count":len(rows)},"unclassified_count":blocked}
    result={"schema_version":"research-route-dry-run-manifest.v1","dry_run":True,"claim_map":map_doc,"manifest":manifest,"claims":public,"candidate_map":candidates,"no_reuse_candidates":no_reuse,"missing_pages":missing_pages,"unexpected_pages":unexpected_pages,"classification_overlay":{"digest":overlay_digest,"audit_pending":overlay_pending,"reviewed_by":overlay.get("reviewed_by") if classification_overlay is not None else None} if classification_overlay is not None else None,"counts":{**counts,**route_counts,"canonical_units":len({r["canonical_claim_key"]["key_digest"] for r in rows}),"candidate_groups":len(candidates),"reuse_decisions":0,"reuse_undecided":len(candidates),"no_reuse_candidate_count":len(no_reuse),"UNCLASSIFIED":blocked}}
    # `--output` names a route manifest, so persist the schema-bound manifest
    # itself. The richer wrapper remains the in-memory return value for callers
    # and stdout-free programmatic use; writing it under the manifest schema
    # would make the artifact impossible to validate independently.
    if out is not None: out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result

def parse_args():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--package-root",required=True,type=Path); p.add_argument("--source-root",type=Path,help="read-only root for catalog/page manifests"); p.add_argument("--classification-overlay",type=Path); p.add_argument("--source",action="append",required=True,type=Path); p.add_argument("--output",type=Path); return p.parse_args()
def main():
    a=parse_args()
    try: result=plan(a.package_root,a.source,a.output,a.source_root,a.classification_overlay)
    except (OSError,ValueError,json.JSONDecodeError) as exc: print(f"BLOCKED-CLAIM-PLAN: {exc}",file=sys.stderr); return 2
    if a.output is None: print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))
    return 0 if result["manifest"]["status"] == "READY" else 2
if __name__=="__main__": raise SystemExit(main())
