import json
import re

def build_searchable_profile(stream):
    """Combines all text from a stream into a single, searchable lowercase string."""
    blob = []
    
    # Add stream name and description
    blob.append(stream['stream_name'].lower())
    blob.append(stream['description'].lower())

    for subject in stream['core_subjects']:
        blob.append(subject['subject'].lower())
        blob.extend([topic.lower() for topic in subject.get('topics', [])])
        
    for career in stream['career_options']:
        blob.append(career['career'].lower())
        blob.extend([spec.lower() for spec in career.get('specializations', [])])
        
    for study in stream['higher_studies']:
        blob.append(study['path'].lower())
        blob.extend([deg.lower() for deg in study['degrees']])
        
    # Join all text into one string
    return " ".join(set(blob))

def recommend_streams(streams_data, interested, not_interested):

    interested_kw = [k.lower() for k in interested]
    not_interested_kw = [k.lower() for k in not_interested]
    
    stream_scores = {}

    # building a profile for every stream
    stream_profiles = {}
    for stream in streams_data['streams']:
        stream_profiles[stream['stream_name']] = build_searchable_profile(stream)

    # Now, score each stream
    for stream_name, profile in stream_profiles.items():
        score = 0
        
        for kw in interested_kw:
            if re.search(re.escape(kw), profile):
                score += 1
                
        for kw in not_interested_kw:
            if re.search(re.escape(kw), profile):
                score -= 1
        
        stream_scores[stream_name] = score

    # 3. Filter and Format Results
    recommendations = []
    sorted_streams = sorted(stream_scores.items(), key=lambda item: item[1], reverse=True)
    
    for stream_name, score in sorted_streams:
        # Only show streams that have a final positive score
        if score > 0:
            recommendations.append({
                "stream": stream_name,
                "score": score
            })

    return recommendations

# --- Main part of the script that runs ---

try:
    with open('streams.json', 'r') as f:
        data = json.load(f)

    # --- 1. Get runtime inputs from the user ---
    print("Enter your interests (e.g., data scientist, mathematics, engineering)")
    print("Separate multiple items with a comma (',')\n")
    interested_input = input("Interested in: ")
    not_interested_input = input("Not interested in: ")

    # --- 2. Process the inputs into clean lists ---
    user_interested = [k.strip().lower() for k in interested_input.split(',') if k.strip()]
    user_not_interested = [k.strip().lower() for k in not_interested_input.split(',') if k.strip()]

    print("\n--- Calculating Recommendations... ---")

    # --- 3. Run the recommendation function ---
    results = recommend_streams(data, user_interested, user_not_interested)

    # --- 4. Print the results ---
    if not results:
        print("\nNo suitable streams found based on your preferences.")
    else:
        print("\nHere are your top recommendations, ranked by priority:\n")
        
        for rank, rec in enumerate(results, start=1):
            print(f"Rank {rank}: {rec['stream']} (Score: {rec['score']})")

except FileNotFoundError:
    print("Error: The file 'streams.json' was not found. Make sure it's in the same directory.")
except Exception as e:
    print(f"An error occurred: {e}")