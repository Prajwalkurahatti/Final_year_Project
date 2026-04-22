import json

# This script takes the hierarchical JSON data and creates a "reverse map".
# It turns the values (Careers, Topics, Degrees) into keys, and the Stream Name into the value.
# Useful for: "I want to be a Doctor, which stream should I pick?"

def reverse_map_streams(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please ensure the file exists.")
        return

    # We use a dictionary where Key = Term, Value = List of Streams
    # We use a list because some terms (like "Mathematics") appear in multiple streams.
    reverse_map = {}

    def add_to_map(term, stream_name, category, sub_category):
        # Clean the term (remove leading/trailing spaces)
        term = term.strip()
        
        if term not in reverse_map:
            reverse_map[term] = {
                "streams": [],
                "type": category,
                "category_context": sub_category
            }
        
        # Avoid duplicates if the stream is already listed for this term
        if stream_name not in reverse_map[term]["streams"]:
            reverse_map[term]["streams"].append(stream_name)

    for stream in data.get('streams', []):
        stream_name = stream.get('stream_name', 'Unknown Stream')

        # 1. Map Topics (from core_subjects)
        if 'core_subjects' in stream:
            for subject_entry in stream['core_subjects']:
                subject_name = subject_entry.get('subject', 'General')
                
                # Map the main Subject name itself (e.g., "Physics")
                add_to_map(subject_name, stream_name, "Subject", "Core Subject")

                # Map individual topics
                for topic in subject_entry.get('topics', []):
                    add_to_map(topic, stream_name, "Topic", subject_name)

        # 2. Map Careers (from career_options)
        if 'career_options' in stream:
            for career_entry in stream['career_options']:
                career_category = career_entry.get('career', 'General Career')
                
                # Map the Career Category itself
                add_to_map(career_category, stream_name, "Career Field", "General")

                # Map individual specializations
                for job in career_entry.get('specializations', []):
                    add_to_map(job, stream_name, "Career", career_category)

        # 3. Map Higher Studies (from higher_studies)
        if 'higher_studies' in stream:
            for study_entry in stream['higher_studies']:
                study_path = study_entry.get('path', 'General Path')
                
                # Map the Path name
                add_to_map(study_path, stream_name, "Education Path", "General")

                # Map individual degrees
                for degree in study_entry.get('degrees', []):
                    add_to_map(degree, stream_name, "Degree", study_path)

    # Write the reversed map to a new JSON file
    with open(output_file, 'w') as f:
        # sort_keys=True makes the output alphabetical and easier to read
        json.dump(reverse_map, f, indent=4, sort_keys=True)
    
    print(f"Success! Reversed data saved to: {output_file}")
    print(f"Total unique terms mapped: {len(reverse_map)}")

# --- Execution ---
if __name__ == "__main__":
    input_filename = 'streams.json'
    output_filename = 'reversed_streams.json'
    
    reverse_map_streams(input_filename, output_filename)