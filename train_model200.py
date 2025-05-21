import spacy
from spacy.training import Example
import random
from training_data_200 import TRAINING_DATA

def align_entities(text, entities, nlp):
    """
    Align entity spans to token boundaries using contract/expand modes.
    Returns a list of aligned (start, end, label) tuples.
    """
    doc = nlp.make_doc(text)
    aligned_entities = []
    for start, end, label in entities:
        # Try aligning with 'contract' mode first
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            # If that fails, try 'expand' mode
            span = doc.char_span(start, end, label=label, alignment_mode="expand")
        if span is not None:
            aligned_entities.append((span.start_char, span.end_char, label))
        else:
            print(f"Warning: Could not align entity '{text[start:end]}' in text: {text}")
    return aligned_entities

def preprocess_training_data(training_data, nlp):
    """
    Preprocess training data to resolve entity alignment and remove overlaps.
    """
    processed_data = []
    for text, annotations in training_data:
        # First, align the entities
        aligned_entities = align_entities(text, annotations.get('entities', []), nlp)
        
        # Remove overlapping entities, keeping the first non-overlapping ones
        unique_entities = []
        for start, end, label in sorted(aligned_entities, key=lambda x: x[0]):
            if not any(start < prev_end and end > prev_start for prev_start, prev_end, _ in unique_entities):
                unique_entities.append((start, end, label))
        
        processed_annotations = {'entities': unique_entities}
        processed_data.append((text, processed_annotations))
    return processed_data

# Load the pre-existing English model (e.g., en_core_web_lg)
nlp = spacy.load("en_core_web_lg")

# Add (or get) the NER pipeline component
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner")
else:
    ner = nlp.get_pipe("ner")

# Add your updated entity labels
labels = ["TASK", "SOFTWARE", "TYPE", "VERSIONS", "PACKAGES", "TARGETS", "JUSTIFICATIONS", "LICENSES"]
for label in labels:
    ner.add_label(label)

# Preprocess the training data to align entities and remove overlaps
processed_training_data = preprocess_training_data(TRAINING_DATA, nlp)

# Convert processed training data to spaCy examples
training_examples = []
for text, annotations in processed_training_data:
    doc = nlp.make_doc(text)
    try:
        example = Example.from_dict(doc, annotations)
        training_examples.append(example)
    except ValueError as e:
        print(f"Skipping example due to error: {text}")
        print(f"Error: {e}")

# Initialize the optimizer
optimizer = nlp.initialize()

# Training loop: 50 epochs
for epoch in range(100):
    random.shuffle(training_examples)
    losses = {}
    for example in training_examples:
        nlp.update(
            [example],
            drop=0.3,
            losses=losses,
            sgd=optimizer
        )
    print(f"Epoch {epoch+1}, Loss: {losses.get('ner', 0):.2f}")

# Save the trained model to disk
nlp.to_disk("software_install_ner_model200_01")
print("Model saved successfully!")
