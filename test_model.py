import spacy
import re
from patterns import add_custom_patterns
from spacy.tokens import Span
import json

def analyze_text(text):
    nlp = spacy.load("software_install_ner_model200_01")
    
    
    
    matcher, phrase_matcher = add_custom_patterns(nlp)
    doc = nlp(text)
    
    result = {
        "type": [],
        "tasks": [],
        "software": [],
        "versions": [],
        "packages": [],
        "targets": [],
        "justifications": [],
        "licenses": [],
        "Task_Complete": 0,
        "Task_Count": 0
    }
    
    matched_tasks = []
    package_flag = False  
    matches = matcher(doc)
    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        span_text = doc[start:end].text.strip()
        if label == "INSTALL_TASK":
            matched_tasks.append(span_text)
        elif label == "REQUIRE_TASK":
            result.setdefault("require_flags", []).append(span_text)
        elif label == "REQUEST_TASK":
            result.setdefault("request_flags", []).append(span_text)
        elif label == "ACCESS_TASK":
            result.setdefault("access_flags", []).append(span_text)
        elif label == "TYPE_NOT_GETTING_INSTALLED":
            result["type"].append("Not getting installed")
        elif label == "TYPE_NOT_ABLE":
            result["type"].append("Not able to")
        elif label == "TYPE_ENABLE":
            result["type"].append("Enable")
        elif label == "TYPE_HOW_TO":
            result["type"].append("How to")
        elif label == "TYPE_ACT":
            result["type"].append("Act")
        elif label == "TYPE_CONNECT":
            result["type"].append("Connect")
        elif label == "SOFTWARE_WITH_VERSION":
            m = re.match(r"^(?P<sw>[A-Za-z\.]+)(?P<ver>\d+(?:\.\d+)*)$", span_text)
            arch_markers = {"aarch", "arm", "x86", "x64"}
            if m and len(m.group("sw")) >= 3 and m.group("sw").lower() not in arch_markers:
                result["software"].append(m.group("sw"))
                result["versions"].append(m.group("ver"))

        elif label in ["SOFTWARE_COMPOUND", "SOFTWARE_NAMES"]:
            result["software"].append(span_text)
        elif label == "VERSION_NUMBERS":
            result["versions"].append(span_text)
        elif label == "PACKAGE_NAMES":
            result["packages"].append(span_text)
        elif label == "PACKAGE_WITH_VERSION":
            m = re.match(r"^(?P<pkg>[A-Za-z0-9]+Setup)-(?:[A-Za-z0-9\-]+-)?(?P<ver>[A-Za-z0-9\-\.]+)$", span_text)
            if m:
                result["packages"].append(m.group("pkg"))
                result["versions"].append(m.group("ver"))
                package_flag = True
        elif label == "TARGETS":
            result["targets"].append(span_text)
        elif label == "JUSTIFICATIONS":
            result["justifications"].append(span_text)
        elif label == "LICENSES":
            result["licenses"].append(span_text)
    
    phrase_matches = phrase_matcher(doc)
    for match_id, start, end in phrase_matches:
        label = nlp.vocab.strings[match_id]
        span_text = doc[start:end].text.strip()
        if label == "SOFTWARE_NAMES":
            result["software"].append(span_text)
    
    def remove_duplicates_and_substrings(lst):
        filtered = []
        seen = set()
        for item in lst:
            token = item.strip()
            if token.lower() == "the":
                continue
            if token.lower() not in seen:
                seen.add(token.lower())
                filtered.append(token)
        final = []
        for item in filtered:
            lower_item = item.lower()
            if any(lower_item != other.lower() and lower_item in other.lower() for other in filtered):
                continue
            final.append(item)
        return final
    
    for key in ["software", "versions", "packages", "targets", "justifications", "licenses"]:
        result[key] = remove_duplicates_and_substrings(result[key])
    
    # Normalize software tokens
    normalized_software = []
    for token in result["software"]:
        m = re.match(r"^([A-Za-z\.]+)(\d+(?:\.\d+)+)$", token, re.I)
        if m:
            normalized_software.append(m.group(1))
            if m.group(2) not in result["versions"]:
                result["versions"].append(m.group(2))
        else:
            lower = token.lower()
            if lower == "opebjdk":
                normalized_software.append("openjdk")
            elif lower == "ctirix":
                normalized_software.append("citrix")
            elif lower == "enterproce arichtecure":
                normalized_software.append("Enterprice Architecure")
            else:
                normalized_software.append(token)
    result["software"] = remove_duplicates_and_substrings(normalized_software)
    
    new_software = []
    for token in result["software"]:
        m = re.match(r"^(\.netcore)(\d+)$", token, re.I)
        if m:
            new_software.append(m.group(1))
            if m.group(2) not in result["versions"]:
                result["versions"].append(m.group(2))
        else:
            new_software.append(token)
    result["software"] = remove_duplicates_and_substrings(new_software)
    
        # Post-process versions to extract only numeric version if needed.
    new_versions = []
    for ver in result["versions"]:
        # If the version string starts with alphabetic characters followed by a version,
        # extract only the numeric part.
        m = re.match(r"^[A-Za-z\.]+(\d+(?:\.\d+)+)$", ver, re.I)
        if m:
            new_versions.append(m.group(1))
        else:
            new_versions.append(ver)
    result["versions"] = remove_duplicates_and_substrings(new_versions)

    
    if "local" in [t.lower() for t in result["targets"]] and "system" in [t.lower() for t in result["targets"]]:
        result["targets"] = [t for t in result["targets"] if t.lower() not in ["local", "system"]]
        result["targets"].append("local system")
    
    if not result["licenses"]:
        lower_text = text.lower()
        if "enterprise" in lower_text:
            result["licenses"].append("Enterprise")
        elif "standard" in lower_text:
            result["licenses"].append("Standard")
        elif "evaluation" in lower_text:
            result["licenses"].append("Evaluation")
        elif "open source" in lower_text:
            result["licenses"].append("Open Source")
        elif "enterprice" in lower_text:
            result["licenses"].append("Enterprise")
    
    if not result["justifications"]:
        justification_phrases = [
            (r"for\s+(\w+(?:\s+\w+){0,3})\s+purposes", "\\1 purposes"),
            (r"to\s+(learn|complete|practice|develop|use|work\s+on)\s+(\w+(?:\s+\w+){0,3})", "\\1 \\2"),
            (r"for\s+(project|learning|development|work|testing|production|business)", "\\1"),
        ]
        for pattern, replacement in justification_phrases:
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches:
                justification = re.sub(pattern, replacement, matches.group(0), flags=re.IGNORECASE)
                result["justifications"].append(justification.strip())
                break
        # Post-process targets: if multiple targets are found, try to extract a single target from the phrase "on my <target>"
    if isinstance(result["targets"], list) and len(result["targets"]) > 1:
        m = re.search(r"on\s+(?:my\s+)?(\w+)", text, re.IGNORECASE)
        if m:
            extracted_target = m.group(1).strip()
            # If the extracted target exists in the current targets list, use it exclusively
            if extracted_target.lower() in [t.lower() for t in result["targets"]]:
                result["targets"] = extracted_target  # storing as a string
        # Post-process targets: if any target token contains "host", override the targets with a single string "host"
    if isinstance(result["targets"], list) and result["targets"]:
        for t in result["targets"]:
            if "host" in t.lower():
                result["targets"] = "host"
                break

 
    lower_text = text.lower()
    if re.search(r"\bhow to install\b", lower_text):
        final_task = "install"
    elif re.search(r"\bdownload\b", lower_text):
        final_task = "download"
    elif re.search(r"\baccess\b", lower_text):
        final_task = "access"
    elif package_flag:
        final_task = "install"
    elif re.search(r"\brequest\b", lower_text):
        final_task = "request"
    elif re.search(r"\b(require)\b", lower_text):
        final_task = "require"
    elif re.search(r"\b(enable)\b", lower_text):
        final_task = "enable"
    else:
        if matched_tasks:
            final_task = sorted(matched_tasks, key=lambda x: len(x), reverse=True)[0]
        else:
            final_task = ''
    
    
    result["tasks"] = [final_task]
    result["Task_Count"] = len(result["software"]) + len(result["packages"])
    if result["Task_Count"] == 0 and len(result["tasks"]) > 0:
        result["Task_Count"] = 1
    result["Task_Complete"] = 0
    
    return result

def transform_result(result):
    """
    Transform the flat result into a list of task entries.
    We decide what to use as the primary key:
      - If 'software' is non-empty, we create one task per software.
      - Else, if 'packages' is non-empty, one task per package.
      - Otherwise, we create a single task with the available info.
    """
    tasks = []
    
    # Determine primary list: software takes precedence over packages.
    if result["software"]:
        primary_items = result["software"]
        primary_field = "software"
    elif result["packages"]:
        primary_items = result["packages"]
        primary_field = "packages"
    else:
        primary_items = [None]
        primary_field = None
    
    for i, item in enumerate(primary_items):
        task_entry = {
            "task_id": i + 1,
            "type": result["type"],
            "Tasks": result["tasks"],
            "software": item if primary_field == "software" else [],
            "packages": item if primary_field == "packages" else result["packages"],
            "versions": result["versions"],
            "targets": result["targets"],
            "justifications": result["justifications"],
            "licenses": result["licenses"],
        }
        tasks.append(task_entry)
    
    transformed = {
        "tasks": tasks,
        "Task_Complete": result["Task_Complete"],
        "Task_Count": len(tasks)
    }
    return transformed

def test_analyzer(json_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)
        subset = data[0:500]
    test_cases = [entry["inc_short_description"] for entry in subset if "inc_short_description" in entry]
    # test_cases=["Can you please provide the link to download the Postman app for Comcast project?"]
    
    print("Testing text analyzer with transformed output:\n")
    for text in test_cases:
        print(f"Input text: {text}")
        result = analyze_text(text)
        transformed = transform_result(result)
        # Pretty-print the transformed output
        for task in transformed["tasks"]:
            print(f"task_id: {task['task_id']}, {task}")
        print(f"Task_Complete: {transformed['Task_Complete']}")
        print(f"Task_Count: {transformed['Task_Count']}\n")

if __name__ == "__main__":
    json_file_path = "Genral Data.json"  
    test_analyzer(json_file_path)
