import ollama
import math



class Database:
    def __init__(self, 
                 embedding_model: str = "all-minilm"):
        print("constructor here")
        self.embedding_model = embedding_model
        self.db = {}
        
    def print_db(self):
        print(self.db)
        
        
    def query_database(self, query, threshold):
        embedded_query = self.generate_embedding(query)
        best_matches = self.find_best_matches(embedded_query, threshold)
        # sorted_list = sorted(best_matches, key=lambda x: x[0], reverse=True)
        sorted_list = sorted(best_matches, key=lambda x: x[0], reverse=True)
        return sorted_list
      
        
    def find_best_matches(self, vector, threshold):
        results = []
        for entry in self.db.keys():
            distance = self.compute_distance(vector, self.db[entry], 'cossim')
            if distance >= threshold:
                results.append((distance, entry))
        return results
                
    def compute_distance(self, v1, v2, type):
        if type == 'cossim':
            return self.cosine_similarity(v1, v2)
        return None
    
    def cosine_similarity(self, vec1, vec2):
        """Calculates the cosine similarity between two vectors.

        Args:
            vec1: A list of numbers representing the first vector.
            vec2: A list of numbers representing the second vector.

        Returns:
            The cosine similarity between vec1 and vec2.
        """
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a**2 for a in vec1))
        magnitude2 = math.sqrt(sum(b**2 for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0  # Avoid division by zero
        else:
            return dot_product / (magnitude1 * magnitude2)
                

class DatabaseOllama(Database):
    def __init__(self, 
                 embedding_model: str = "all-minilm"):
        print("constructor here")
        self.embedding_model = embedding_model
        self.db = {}
        
    def add(self, text):
        if len(text) > 0:
            embedding = self.generate_embedding(text)
            self.db[text] = embedding
        
    def generate_embedding(self, text):
        embeddings = ollama.embeddings(
            model=self.embedding_model,
            prompt=text,
        )
        return(embeddings['embedding'])
    
    
    
# tbd - entscheiden ob LMStudio brauchbar ist.
    
class DatabaseLMStudio(Database): 
    def __init__(self, embedding_model: str = "all-minilm", embedding_dim: int = 384):
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        print("constructor here")
        self.embedding_model = embedding_model
        self.embeding_dim = embedding_dim
        self.db = {}
        
    def add(self, text):
        if len(text) > 0:
            text = text.replace("\n", " ")
            embedding = self.generate_embedding(text)
            self.db[text] = embedding
        
    def generate_embedding(self, text):      
        embedding = self.client.embeddings.create(input = [text], 
                        model=self.embedding_model).data[0].embedding
        return embedding
    

            