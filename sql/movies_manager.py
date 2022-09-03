from sql.config import *
class Movies():

    def __init__(self, cursor):
        self.cursor = cursor

    def _execute_query(self,query):
        result = self.cursor.execute(query)
        return 

    def create_movies_table(self):
        query = """
            create table if not exists movies(
                id integer primary key auto_increment,
                name varchar(400) not null,
                description varchar(600) not null,
                premiere date,
                category_id integer not null,
                foreign key(category_id) references category(id)
            );
        """
        res = self._execute_query(query)
        return res

    def add_movie(self, data):
        query = f"""
            INSERT INTO movies(
                name, description, premiere, category_id)
            VALUES('{data.get("name")}', '{data.get("description")}',
                {data.get('premiere')}, {data.get('category_id')}
            );
        """
        self._execute_query(query)


    def get_all_movies(self):
        query = """
            select * from movies;    
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_movies_by_category(self,category_id):
        query = f"""
            select * from movies where category_id ={category_id};
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_movies_by_id(self,id):
        query = f"""
            select * from movies where id={id};
        """     
        self.cursor.execute(query)
        return self.cursor.fetchone()



    def search_movie(self,search_text):
        query = f"""
            select * from movie where name like '%{search_text}%';
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def _get_all_ids(self):
        query = f"""
            select id from movies;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

        