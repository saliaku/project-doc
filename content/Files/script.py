from GA_functions import *  
import variables  


def generate_learning_path(user_id):
    user_id=int(user_id)
    """Generates a learning path and stores it in Moodle."""
    print("here")
    # Fetch learning objects
    learning_objects, grouped_los = fetch_learning_objects()

    # Fetch learning objects
    variables.learning_objects= learning_objects
    print("learning objects",variables.learning_objects)


    # Fetch difficulty values dynamically
    difficulty_val = fetch_difficulty_values()
    print("difficulty_val",difficulty_val)


    # Fetch clusters
    clusters = fetch_clusters()
    print("clusters:", clusters)

    # Fetch student's cognitive profile from mdl_user
    conn = pymysql.connect(host=variables.HOST, user=variables.USER, password=variables.PASS, database="moodle")
    print("connected")
    print("userid", user_id)
    cursor = conn.cursor()
    print("going to execute")
    cursor.execute("SELECT wmv, wma, wmt, ipv, ipa, ipt, flesch FROM mdl_user WHERE id=%s;", (user_id,))
    print("executed")
    student_data = cursor.fetchone()
    print("student data:", student_data)
    conn.close()

    if not student_data:
        print("not found")
        return {"error": "Student profile not found"}

    print("student profile found") 

    student_profile = student(
        id=user_id,
        wmv=student_data[0], wma=student_data[1], wmt=student_data[2],
        ipv=student_data[3], ipa=student_data[4], ipt=student_data[5],
        read_metric=student_data[6],
        cluster_id=None,
        difficulty_val=difficulty_val, gene_space=grouped_los,
        completed=[], learning_costs={}, genes_explored={}
    )

    variables.student_profile= student_profile
    print(variables.student_profile)
    print(variables.max_distance, variables.num_gen)
    best_solution = get_path(student_profile, clusters, variables.max_distance, variables.num_gen)
    print("best_solution:",best_solution)
    print(clusters)
    
    # Store updated clusters
    store_clusters(clusters)

    # Convert learning path to JSON format for storage
    learning_path = [int(i) for i in best_solution]
    store_student_profile(user_id, student_profile, learning_path)
    store_attempt(user_id, learning_objects[learning_path[0]].topic, 1)
    

    return {"message": "Learning path generated", "path": learning_path}

if __name__ == "__main__":
    import sys
    import logging
    print("Script has started running")
    #logging.basicConfig(filename='/tmp/script_debug.log', level=logging.DEBUG)

    try:
        userid = sys.argv[1]
        #logging.debug(f"Script started for user: {userid}")
        print("hello world")
        print(userid)

        result = generate_learning_path(userid)
        print(result)

    except Exception as e:
        #logging.exception("An error occurred:")
        if len(sys.argv) < 2:
            print("Usage: script.py <userid>")
        sys.exit(0)


