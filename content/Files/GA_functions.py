import pygad
import pymysql
import random
import json
import numpy as np
import copy
from collections import OrderedDict
from typing import OrderedDict
import variables
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pygad")



class LO:
    def __init__(self, id, topic, v, a, t, ip, read_metric):
        self.id = id
        self.topic = topic
        self.v = v  # Visual metric
        self.a = a  # Auditory metric
        self.t = t  # Reading/Writing metric
        self.ip = ip  # Information processing metric
        self.read_metric = read_metric # readability score of content (r)


    def __repr__(self):
        return f"{self.id}({self.topic})"
    
    
class student:
    def __init__(self, id, wma, wmv, wmt, ipa, ipv, ipt, read_metric, cluster_id, difficulty_val, gene_space, completed, learning_costs, genes_explored):
        self.id = id
        self.wmv = wmv
        self.wma = wma
        self.wmt = wmt
        self.ipv = ipv
        self.ipa = ipa
        self.ipt = ipt
        self.read_metric = read_metric #rd - readability score

        self.s = wma + wmv + wmt + ipa + ipv + ipt
        if (self.s==0):
            self.v = 0
            self.a = 0
            self.t = 0
        else:
            self.v = (wmv + ipv)/self.s
            self.a = (wma + ipa)/self.s
            self.t = (wmt + ipt)/self.s
        self.cluster_id= cluster_id
        self.difficulty= copy.deepcopy(difficulty_val)
        self.gene_space=copy.deepcopy(gene_space)
        self.completed=copy.deepcopy(completed)
        self.learning_costs=copy.deepcopy(learning_costs)
        self.explored_genes= copy.deepcopy(genes_explored)

    def __repr__(self):
        return f"{self.id}"
    
    
class Cluster:
    def __init__(self, centroid):
        self.centroid = centroid  # [v, a, t]
        self.gene_pool = set()   # Set of unique genes in the cluster

    def __repr__(self):
        return f"{self.centroid}\n{self.gene_pool}"
    


#Generating a random chromosome
def generate_random_chromosome(grouped_los):
    chromosome = [random.choice(grouped_los[topic]) for topic in grouped_los]
    random.shuffle(chromosome)
    return np.array(chromosome, dtype=int)


def generate_initial_population(pop_size, grouped_los):
    return np.array([generate_random_chromosome(grouped_los) for _ in range(pop_size)])


def add_learning_cost(topic, gene, cost, student_profile):

  explored_genes= student_profile.explored_genes
  # If topic does not exist, create an empty dictionary for it
  if topic not in explored_genes:
      explored_genes[topic] = {}

  # Add gene-cost pair only if gene is not already present
  if gene not in explored_genes[topic]:
      explored_genes[topic][gene] = cost
  explored_genes[topic] = OrderedDict(sorted(explored_genes[topic].items(), key=lambda x: x[1]))

def fitness_function(random_chromosome, student_profile, learning_objects):
    lc = 0
    lgs = []
    n = len(random_chromosome)

    # Ensure random_chromosome is treated as a list of integers
    random_chromosome = random_chromosome.astype(int)

    for i in random_chromosome:
        lg = learning_cost(i, student_profile, learning_objects)
        lgs.append(lg)

    lc = sum(lgs) / n
    '''local_learning_costs = [
        (lgs[i - 1] + lgs[i]) / 2 for i in range(1, n)
    ]

    variance = sum([(l - lc) ** 2 for l in local_learning_costs])
    fitness_value = lc + variance'''
    fitness_value= lc
    return -fitness_value

def learning_cost(i, student_profile, learning_objects):
    lo = learning_objects[i]  # Get the LO object from the dictionary
    learning_costs = student_profile.learning_costs
    topic = lo.topic

    if i in learning_costs and learning_costs[i] != -1:
        return learning_costs[i]
    else:
        wr = 0
        rd = student_profile.read_metric
        r = lo.read_metric
        d = student_profile.difficulty[topic]

        if rd >= r:
            wr = (rd - r) / 20

        s = student_profile.s
        v, a, t = student_profile.v, student_profile.a, student_profile.t
        tc, ac, vc = lo.t, lo.a, lo.v
        wip = 1 - (s / 33)
        ip = lo.ip

        lg = d + wr + t * (5 - tc) + a * (5 - ac) + v * (5 - vc) + wip * ip
        learning_costs[i] = lg
        add_learning_cost(topic, i, lg, student_profile)

    return lg

  
  
def pmx_crossover(parents, offspring_size, learning_objects):
    offspring = []
    parents = parents.tolist()  # Convert numpy array to list for processing
    for _ in range(offspring_size[0]):
        # Randomly select two parents
        parent1, parent2 = random.sample(parents,2)

        # Randomly choose crossover points
        size = len(parent1)
        point1, point2 = sorted(random.sample(range(size), 2))

        # Initialize offspring with placeholders
        child = [-1] * size

        # Copy segment from parent1 to the child
        child[point1:point2 + 1] = parent1[point1:point2 + 1]

        # Track topics already in the crossed section
        used_topics = {learning_objects[int(gene)].topic for gene in child[point1:point2 + 1] if gene != -1}

        # Add genes from parent2 that do not duplicate topics in the crossed section
        for idx in range(size):
            if idx < point1 or idx > point2:  # Consider only indices outside the crossed section
                candidate = parent2[idx]
                candidate_topic = learning_objects[int(candidate)].topic

                if candidate_topic not in used_topics:
                    child[idx] = candidate
                    used_topics.add(candidate_topic)

        # Fill any remaining empty slots (`-1`) with unused genes from parent2
        for idx in range(size):
            if child[idx] == -1:
                for candidate in parent2:
                    candidate_topic = learning_objects[int(candidate)].topic
                    if candidate_topic not in used_topics:
                        child[idx] = candidate
                        used_topics.add(candidate_topic)
                        break

        # Append the generated child to the offspring list
        offspring.append(child)
    # Convert offspring to a numpy array before returning
    return np.array(offspring)


def mutate_gene(solution, mutation_probability, student_profile, learning_objects):
    if np.random.rand() < mutation_probability:  # Apply mutation based on probability
        # Pick a random index in the solution
        idx = np.random.randint(0, len(solution))
        current_gene = solution[idx]
        current_topic = learning_objects[int(current_gene)].topic

        # Replace with a random LO of the same topic
        solution[idx] = random.choice(student_profile.gene_space[current_topic])

    return solution


def mutation(offspring, ga_instance, student_profile, learning_objects):

    mutation_probability = ga_instance.prob  # Example mutation probability
    for idx in range(offspring.shape[0]):  # Iterate over each chromosome
        # Apply custom mutation logic for the chromosome
        offspring[idx] = mutate_gene(
            solution=offspring[idx],
            mutation_probability=mutation_probability,
            student_profile= student_profile,
            learning_objects= learning_objects
        )

    return offspring


def repair(chromosome, dependency_graph, learning_objects, student_profile):

    # Convert chromosome to a list for processing
    chromosome = chromosome.tolist()

    # Extract topics from the chromosome
    topics = [learning_objects[int(gene)].topic for gene in chromosome]

    # Perform a topological sort on the dependency graph
    in_degree = {topic: 0 for topic in dependency_graph}
    for deps in dependency_graph.values():
        for dep in deps:
            in_degree[dep] += 1

    # Queue for topics with no dependencies
    queue = [topic for topic in in_degree if in_degree[topic] == 0]
    topo_sort = []

    while queue:
        # Sort the queue by difficulty from the student's perspective
        queue.sort(key=lambda topic: student_profile.difficulty.get(topic, float('inf')))

        # Pop the topic with the lowest difficulty
        topic = queue.pop(0)
        topo_sort.append(topic)

        for dependent in dependency_graph[topic]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    # Map topics to their position in the topological order
    topic_to_index = {topic: i for i, topic in enumerate(topo_sort)}

    # Reorder the chromosome to match the topological order
    repaired_chromosome = sorted(chromosome, key=lambda gene: topic_to_index[learning_objects[int(gene)].topic])

    # Convert back to NumPy array and return
    return np.array(repaired_chromosome)

def on_generation(ga_instance, learning_objects, student_profile):
    #Functions to be performed at the end of every generation
    # Access the population
    population = ga_instance.population
    # Dependency graph
    dependency_graph = {
        27: [28, 32],
        28: [29, 30],
        29: [31],
        30: [31],
        32: [33],
        33: [34],
        34: [35],
        31: [],
        35: []
        }

    # Repair each chromosome in the population
    for i in range(len(population)):
        population[i] = repair(population[i], dependency_graph, learning_objects, student_profile)

    # Update the population in the GA instance
    ga_instance.population = population

    best_solution, best_fitness, _ = ga_instance.best_solution()
    global max_fitness, sol, avg_fitness, c
    c=c+1
    avg_fitness=avg_fitness+best_fitness
    if(max_fitness< best_fitness):
      max_fitness= best_fitness
      sol= best_solution


def fitness_function_wrapper(ga_instance, solution, solution_idx):
    return fitness_function(solution, variables.student_profile, variables.learning_objects)

def pmx_crossover_wrapper(parents, offspring_size, ga_instance):
  return pmx_crossover(parents, offspring_size, variables.learning_objects)

def mutation_wrapper(offspring, ga_instance):
  return mutation(offspring, ga_instance, variables.student_profile, variables.learning_objects)

def on_generation_wrapper(ga_instance):
    on_generation(ga_instance, variables.learning_objects, variables.student_profile)

def cluster_assignment(student_profile, clusters, max_distance):
    # Assumes no cluster assigned previously to the student
    student_vat = np.array([student_profile.v, student_profile.a, student_profile.t])
    assigned = False
    # Find the closest cluster within max_distance
    for cluster_id, cluster in clusters.items():  # Iterate through dictionary
        # Manhattan distance
        distance = np.sum(np.abs(student_vat - cluster.centroid))
        print("distance:",distance)
        if distance <= max_distance:
            # Update 
            cluster.centroid = np.mean([cluster.centroid] + [student_vat], axis=0)
            student_profile.cluster_id = cluster_id  # Assign cluster ID to the student
            assigned = True
            num_gen=500
            break

    # If no suitable cluster, create a new one
    if not assigned:
        new_cluster_id = max(clusters.keys(), default=0) + 1  # Get new cluster ID
        clusters[new_cluster_id] = Cluster(centroid=student_vat)  # Initialize new cluster
        student_profile.cluster_id = new_cluster_id  # Assign new cluster ID
        num_gen=1000
    return num_gen

def get_initial_population(student_profile, clusters):
    # Gene space of student is assumed to contain at least one gene for each topic
    # Grouped_los and learning objects are universal ones

    cluster = clusters.get(int(student_profile.cluster_id))  # Retrieve cluster safely
    if cluster is None:
        return None  # Handle missing cluster case

    gene_pool = cluster.gene_pool
    gene_space = student_profile.gene_space
    grouped_genes = {}

    for topic, genes in gene_space.items():
        grouped_genes[topic] = [gene for gene in genes if int(gene) in gene_pool]
        if not grouped_genes[topic]:
            grouped_genes[topic] = genes  # Use all genes if no match in gene pool

    return generate_initial_population(16, grouped_genes)


def generate_path(student_profile, initial_pop, num_gen):
    global max_fitness, avg_fitness, c, sol
    max_fitness = float('-inf')
    avg_fitness = 0
    c = 0

    ga_instance = pygad.GA(
        initial_population=initial_pop,
        num_generations=num_gen,
        num_parents_mating=10,
        fitness_func=fitness_function_wrapper,
        sol_per_pop=16,
    
        parent_selection_type='rws',
        crossover_type=pmx_crossover_wrapper,
        mutation_type=mutation_wrapper,
        on_generation=on_generation_wrapper,  # Ensure this function repairs chromosomes
        keep_elitism=1
    )
    ga_instance.prob = 0.7
    ga_instance.run()

    # Best solution
    best_solution, best_fitness, _ = ga_instance.best_solution()
    avg_fitness += best_fitness
    c += 1
    avg_fitness /= c

    if best_fitness > max_fitness:
        max_fitness = best_fitness
        sol = best_solution

    '''print("Best solution:", sol)
    print("Best_fitness:", max_fitness)
    print('avg_fitness=', avg_fitness)

    for i in best_solution:
        topic = variables.learning_objects[int(i)].topic
        print(int(i), '-', variables.learning_objects[int(i)].v, variables.learning_objects[int(i)].a, variables.learning_objects[int(i)].t, '(', topic, ')', '-', student_profile.difficulty[topic])

    # Visualize the fitness evolution
    ga_instance.plot_fitness()'''
    return sol


def add_path(student_profile, path, clusters):
    cluster = clusters.get(int(student_profile.cluster_id))  # Retrieve cluster safely
    if cluster:
        cluster.gene_pool.update(path)  # Update gene pool


def get_path(student_profile, clusters, max_distance, num_gen):
    if student_profile.cluster_id is None:
        num_gen=cluster_assignment(student_profile, clusters, max_distance)

    # If assigned is false => then new cluster created
    initial_pop = get_initial_population(student_profile, clusters)
    '''print("Initial population:")
    print(initial_pop)'''
    path = generate_path(student_profile, initial_pop, num_gen)
    add_path(student_profile, path, clusters)
    return path


def update_gene(path, student_curr, topic):
    explored_genes = student_curr.explored_genes[topic]
    path[0] = next(iter(explored_genes))
    return path


def update_score(student_curr, score, true_attempts, path, clusters, max_distance, learning_objects):
  attempts= true_attempts%3
  topic = learning_objects[int(path[0])].topic
  topic_name=fetch_topic_name(topic)

  # Test passed
  if score >= 0.8:
    del student_curr.gene_space[topic]
    del student_curr.explored_genes[topic]
    student_curr.completed.append(topic)
    print(topic_name, "completed!")

    new_path = np.delete(path, 0)
    # End of course
    if len(new_path):
        store_attempt(student_curr.id, learning_objects[new_path[0]].topic, 1)
        #print("Course completed!")
    return new_path



  else:
    #remove the gene
    print("Oops! Retry", topic_name)
    student_curr.gene_space[topic].remove(int(path[0]))
    del student_curr.explored_genes[topic][int(path[0])]
    if not student_curr.gene_space[topic] or not student_curr.explored_genes[topic]:
        print("No more resources available on", topic_name, "!")
        del student_curr.gene_space[topic]
        del student_curr.explored_genes[topic]
        student_curr.completed.append(topic)
        new_path=np.delete(path, 0)
        if len(new_path):
            store_attempt(student_curr.id, learning_objects[new_path[0]].topic, 1)
        #print("Course completed!")
        return new_path
    else:
        if (attempts==1 or attempts==2):
            #print("updating gene")
            new_path= update_gene(path, student_curr, topic)
            store_attempt(student_curr.id, learning_objects[new_path[0]].topic, true_attempts+1)
            return new_path
        else:
            #print("regenerating path with increased difficulty for the topic")
            d=student_curr.difficulty[topic]
            #print("previous difficulty:", d)
            d=d+(1-score)
            if(d>5):
                d=5
            #print("updated difficulty:", d)
            student_curr.difficulty[topic]=d
            if(len(path)==1):
                new_path= update_gene(path, student_curr,topic) # only 1 gene needs to be updated not the whole path
                store_attempt(student_curr.id, learning_objects[new_path[0]].topic, true_attempts+1)
            else:
                '''fix here to deal with the the issue quiz_attempts
                fetch existing attempts and update either with 1 if new topic or 
                attempts+1 for same topic or 
                attempts'+1 for revisit'''
                new_path= get_path(student_curr,clusters, max_distance, variables.num_regen)
                new_topic=learning_objects[new_path[0]].topic
                if(topic==new_topic):
                    store_attempt(student_curr.id, new_topic, true_attempts+1)
                else: 
                    new_attempt= fetch_attempts(student_curr.id, new_topic)
                    store_attempt(student_curr.id, new_topic, new_attempt+1)
            return new_path

def fetch_learning_objects():
    import pymysql

    conn = pymysql.connect(host=variables.HOST, user=variables.USER, password=variables.PASS, database="fyp")
    cursor = conn.cursor()

    # Join `lo` and `topics` on the topic column, and fetch the IP from topics
    cursor.execute("""
        SELECT lo.id, lo.topic, lo.v, lo.a, lo.t, topics.ip, lo.read_metric
        FROM lo
        JOIN topics ON lo.topic = topics.id;
    """)
    rows = cursor.fetchall()
    conn.close()

    # Store learning objects in a dictionary
    learning_objects = {row[0]: LO(*row) for row in rows}

    # Group learning object IDs by topic
    grouped_los = {}
    for lo_id, lo in learning_objects.items():
        if lo.topic not in grouped_los:
            grouped_los[lo.topic] = []
        grouped_los[lo.topic].append(lo_id)

    return learning_objects, grouped_los


def fetch_clusters():
    #print("Fetching clusters...")

    try:
        conn = pymysql.connect(
            host=variables.HOST,
            user=variables.USER,
            password=variables.PASS,
            database="fyp"
        )
        #print("Connection established.")
    except Exception as conn_err:
        print("Database connection error:", conn_err)
        return {}

    try:
        cursor = conn.cursor()
        #print("Cursor created.")

        try:
            cursor.execute("SELECT id, centroid, gene_pool FROM clusters;")
            rows = cursor.fetchall()
            #print(f"Fetched {len(rows)} rows from clusters.")
        except Exception as query_err:
            print("Error executing SELECT query:", query_err)
            return {}
        finally:
            cursor.close()
            #print("Cursor closed.")

    except Exception as cursor_err:
        print("Cursor error:", cursor_err)
        return {}
    finally:
        conn.close()
        #print("Connection closed.")

    clusters = {}
    for row in rows:
        try:
            cluster_id = row[0]
            centroid = np.array(json.loads(row[1]))
            gene_pool = set(np.int64(x) for x in json.loads(row[2]))
            clusters[cluster_id] = Cluster(centroid)
            clusters[cluster_id].gene_pool=gene_pool
        except Exception as parse_err:
            print(f"Error parsing cluster row {row}: {parse_err}")

    return clusters


def store_clusters(clusters):
    """Stores or updates clusters in the database."""

    try:
        conn = pymysql.connect(
            host=variables.HOST,
            user=variables.USER,
            password=variables.PASS,
            database="fyp"
        )
        cursor = conn.cursor()

        for cluster_id, cluster_obj in clusters.items():
            centroid_json = json.dumps(convert_np(cluster_obj.centroid))
            gene_pool_json = json.dumps(convert_np(list(cluster_obj.gene_pool)))

            cursor.execute("""
                INSERT INTO clusters (id, centroid, gene_pool)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    centroid = VALUES(centroid),
                    gene_pool = VALUES(gene_pool);
            """, (cluster_id, centroid_json, gene_pool_json))

        conn.commit()

    except Exception as e:
        print("Error while storing clusters:", e)

    finally:
        conn.close()


def fetch_difficulty_values():
    conn = pymysql.connect(host=variables.HOST, user=variables.USER, password=variables.PASS, database="fyp")

    cursor = conn.cursor()
    
    cursor.execute("SELECT id, difficulty FROM topics;")
    
    rows = cursor.fetchall()
    conn.close()
    
    return {row[0]: row[1] for row in rows}

def fetch_topic_name(topic_id):
    conn = pymysql.connect(host=variables.HOST, user=variables.USER, password=variables.PASS, database="fyp")

    cursor = conn.cursor()
    
    cursor.execute("SELECT topic_name FROM topics where id=%s;", topic_id)
    
    rows = cursor.fetchone()
    conn.close()
    
    return rows[0]

def fetch_student_profile(user_id):
    """Fetch student profile from the database."""
    conn = pymysql.connect(host=variables.HOST, user=variables.USER, password=variables.PASS, database="moodle")
    cursor = conn.cursor()

    cursor.execute("SELECT wmv, wma, wmt, ipv, ipa, ipt, flesch FROM mdl_user WHERE id=%s", (user_id,))
    student_data = cursor.fetchone()
    conn.close()
    
    conn = pymysql.connect(host=variables.HOST, user=variables.USER, password=variables.PASS, database="fyp")
    cursor = conn.cursor()
    cursor.execute("SELECT path, difficulty, gene_space, explored_genes, completed, learning_costs, cluster_id FROM students WHERE user_id=%s", (user_id,))
    student_details = cursor.fetchone()
    conn.close()

    if not student_data or not student_details:
        print("Error: Student profile not found.")
        return None

    # Parse JSON fields
    path = json.loads(student_details[0])
    raw_difficulties = json.loads(student_details[1])
    difficulties= {int(k): v for k,v in raw_difficulties.items()}
    gene_space_raw = json.loads(student_details[2])
    gene_space = {int(k): v for k, v in gene_space_raw.items()}

    
    # Convert back from JSON list to Python objects
    explored_genes_raw = json.loads(student_details[3])
    explored_genes = {int(k): {int(sub_k): v for sub_k, v in sub_dict.items()} for k, sub_dict in explored_genes_raw.items()}

    completed_raw = student_details[4]
    completed = json.loads(completed_raw) if completed_raw else []

    learning_costs_raw = json.loads(student_details[5])
    learning_costs = {int(k): float(v) for k, v in learning_costs_raw.items()}

    cluster_id = int(student_details[6])
    student_profile= student(
        id=user_id,
        wmv=student_data[0], wma=student_data[1], wmt=student_data[2],
        ipv=student_data[3], ipa=student_data[4], ipt=student_data[5],
        read_metric=student_data[6],
        difficulty_val=difficulties, gene_space=gene_space,
        completed= completed,
        learning_costs= learning_costs,
        genes_explored=explored_genes,
        cluster_id=cluster_id
    )
    
    return student_profile, path


def store_student_profile(user_id, student_profile, path):
    """Update student profile in the database."""
    # Store in Moodle DB the path and cluster assigned
    conn = pymysql.connect(host=variables.HOST, user=variables.USER, password=variables.PASS, database="fyp")
    cursor = conn.cursor()
    path_json = json.dumps(path, default=convert_np)


    query = """
    INSERT INTO students (user_id, path, stored_path, cluster_id, difficulty, gene_space, explored_genes, learning_costs, completed) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
    ON DUPLICATE KEY UPDATE 
        path = VALUES(path),
        stored_path = VALUES(stored_path),
        cluster_id = VALUES(cluster_id),
        difficulty = VALUES(difficulty),
        gene_space = VALUES(gene_space),
        explored_genes = VALUES(explored_genes),
        learning_costs = VALUES(learning_costs),
        completed = VALUES(completed);
    """

    try:
    
        cursor.execute(query, (
            user_id, 
            path_json,
            path_json,
            convert_np(student_profile.cluster_id),  # Just in case it's also a numpy type
            json.dumps(student_profile.difficulty), 
            json.dumps(student_profile.gene_space), 
            json.dumps(convert_np(student_profile.explored_genes)), 
            json.dumps(convert_np(student_profile.learning_costs)),
            json.dumps(student_profile.completed)
        ))
        conn.commit()
        #print(f"[INFO] Successfully updated student profile for user_id={user_id}")
    except Exception as e:
        print(f"[ERROR] Failed to update student profile for user_id={user_id}: {e}")
    conn.close()
    
def update_student_profile(user_id, student_profile, path):
    """Update student profile in the database."""
    # Store in Moodle DB the path and cluster assigned
    conn = pymysql.connect(host=variables.HOST, user=variables.USER, password=variables.PASS, database="fyp")
    cursor = conn.cursor()
    path_json = json.dumps(path, default=convert_np)


    query = """
    INSERT INTO students (user_id, path, cluster_id, difficulty, gene_space, explored_genes, learning_costs, completed) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
    ON DUPLICATE KEY UPDATE 
        path = VALUES(path),
        cluster_id = VALUES(cluster_id),
        difficulty = VALUES(difficulty),
        gene_space = VALUES(gene_space),
        explored_genes = VALUES(explored_genes),
        learning_costs = VALUES(learning_costs),
        completed = VALUES(completed);
    """

    try:
    
        cursor.execute(query, (
            user_id, 
            path_json,
            convert_np(student_profile.cluster_id),  # Just in case it's also a numpy type
            json.dumps(student_profile.difficulty), 
            json.dumps(student_profile.gene_space), 
            json.dumps(convert_np(student_profile.explored_genes)), 
            json.dumps(convert_np(student_profile.learning_costs)),
            json.dumps(student_profile.completed)
        ))
        conn.commit()
        #print(f"[INFO] Successfully updated student profile for user_id={user_id}")
    except Exception as e:
        print(f"[ERROR] Failed to update student profile for user_id={user_id}: {e}")
    conn.close()
    

def fetch_attempts(user_id, topic_id):
    """Fetch the number of quiz attempts for a specific topic by a student."""
    conn = pymysql.connect(host=variables.HOST, user=variables.USER, password=variables.PASS, database="fyp")
    cursor = conn.cursor()

    cursor.execute("SELECT attempts FROM quiz_attempts WHERE student_id=%s AND topic_id=%s", (user_id, topic_id))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else 0  # Default to 0 if no attempts recorded


def store_attempt(user_id, topic_id, attempts):
    """Store or update the number of quiz attempts for a specific topic by a student."""
    try:
        conn = pymysql.connect(
            host=variables.HOST,
            user=variables.USER,
            password=variables.PASS,
            database="fyp"
        )
        cursor = conn.cursor()

        query = """
        INSERT INTO quiz_attempts (student_id, topic_id, attempts)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE attempts = VALUES(attempts);
        """

        cursor.execute(query, (user_id, topic_id, attempts))
        conn.commit()

    except Exception as e:
        print(f"Error storing attempts for user_id={user_id}, topic_id={topic_id}: {e}")
    finally:
        conn.close()

def convert_np(obj):
    if isinstance(obj, dict):
        return {convert_np(k): convert_np(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_np(i) for i in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

