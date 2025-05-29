#!/usr/bin/env python3

import sys
import variables
from GA_functions import *


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(1)

    user_id = int(sys.argv[1])
    current_topic= int(sys.argv[2])
    score = float(sys.argv[3])
    

    # Fetch student profile
    student_profile, path = fetch_student_profile(user_id)
    if student_profile is None:
        sys.exit(1)
    variables.student_profile= student_profile

    # Fetch supporting data
    clusters = fetch_clusters()
    learning_objects, _ = fetch_learning_objects()
    variables.learning_objects= learning_objects
    


    # Fetch attempts count from quiz_attempts table
    attempts = fetch_attempts(user_id, current_topic)

    # Update score and path
    new_path = update_score(student_profile, score, attempts, path, clusters, variables.max_distance, learning_objects)

    # Save updated student profile
    update_student_profile(user_id, student_profile, new_path)

