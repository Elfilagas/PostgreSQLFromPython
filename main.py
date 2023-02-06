import psycopg2


class Database:
    def __init__(self, dbname: str="clients_db", user: str="postgres", password: str="1906"):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password)
        self.cur = self.conn.cursor()

    def create_db(self):
        """Create tables 'clients' and 'phones'"""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS clients(
                id         SERIAL      PRIMARY KEY,
                first_name VARCHAR(50),
                last_name  VARCHAR(50),
                email      VARCHAR(100) UNIQUE
                );
            CREATE TABLE IF NOT EXISTS phones(
                phone_id     SERIAL  PRIMARY KEY,
                client_id    INTEGER REFERENCES clients(id),
                phone_number BIGINT UNIQUE
                );
            """)
        self.conn.commit()
        print("Tables created...")

    def add_client(self, first_name: str, last_name: str, email: str, phones: list[int, ...]=None) -> int:
        """Add client to clients table and his phones into phones table
        return client_id"""
        self.cur.execute("""
            INSERT INTO clients 
            VALUES (default, %s, %s, %s) 
            ON CONFLICT DO NOTHING 
            RETURNING id;
            """, (first_name, last_name, email))
        client_id = self.cur.fetchone()
        if phones is None:
            phones = []
        for phone in phones:
            self.cur.execute("""
                INSERT INTO phones
                VALUES (default, %s, %s) 
                ON CONFLICT DO NOTHING; 
                """, (client_id, phone))
        self.conn.commit()
        print(f"Client {first_name} {last_name} has added")
        return client_id

    def add_phone(self, client_id: int, phone: int):
        """Add phone number to existed client_id"""
        self.cur.execute("""
            INSERT INTO phones 
            VALUES (default, %s, %s) 
            ON CONFLICT DO NOTHING;
            """, (client_id, phone))
        self.conn.commit()
        print(f"Phone {phone} has added to client {client_id}")

    def change_client(self, client_id: int, first_name: str=None, last_name: str=None,
                      email: str=None, phones: list[int, ...]=None):
        """Change information about client"""
        if first_name:
            self.cur.execute("""
                UPDATE clients SET first_name=%s   
                WHERE id=%s;
                """, (first_name, client_id))
        if last_name:
            self.cur.execute("""
                UPDATE clients SET last_name=%s   
                WHERE id=%s;
                """, (last_name, client_id))
        if email:
            self.cur.execute("""
                UPDATE clients SET email=%s   
                WHERE id=%s;
                """, (email, client_id))
        if phones:
            self.cur.execute("""
                DELETE FROM phones   
                WHERE client_id=%s;
                """, (client_id,))
            for phone in phones:
                self.cur.execute("""
                    INSERT INTO phones
                    VALUES (default, %s, %s)
                    ON CONFLICT DO NOTHING; 
                    """, (client_id, phone))
        self.conn.commit()
        print("Data has changed")

    def delete_phone(self, client_id: int, phone: int):
        """Delete phone from phones table"""
        self.cur.execute("""
            DELETE FROM phones   
            WHERE client_id=%s and phone_number=%s;
            """, (client_id, phone))
        self.conn.commit()
        print(f"Phone number {phone} has deleted")

    def delete_client(self, client_id: int):
        """Delete client from clients table"""
        self.cur.execute("""
            DELETE FROM phones   
            WHERE client_id=%s;
            """, (client_id,))
        self.cur.execute("""
            DELETE FROM clients   
            WHERE id=%s;
            """, (client_id,))
        self.conn.commit()
        print(f"Client number {client_id} has deleted")

    def find_client(self, first_name: str=None, last_name: str=None, email: str=None, phone: int=None):
        """Find client by information and show client info"""
        if phone:
            self.cur.execute("""
                SELECT c.id, first_name, last_name, email 
                FROM phones p 
                JOIN clients c ON c.id = p.client_id 
                WHERE p.phone_number=%s;
                """, (phone,))
        elif email:
            self.cur.execute("""
                SELECT id, first_name, last_name, email  
                FROM clients 
                WHERE email=%s;
                """, (email,))
        elif last_name and first_name:
            self.cur.execute("""
                SELECT id, first_name, last_name, email  
                FROM clients 
                WHERE first_name=%s AND last_name=%s;
                """, (first_name, last_name))
        elif last_name:
            self.cur.execute("""
                SELECT id, first_name, last_name, email  
                FROM clients 
                WHERE last_name=%s;
                """, (last_name,))
        elif first_name:
            self.cur.execute("""
                SELECT id, first_name, last_name, email  
                FROM clients 
                WHERE first_name=%s;
                """, (first_name,))
        print(self.cur.fetchall())

    def close(self):
        """Close cursor and connection"""
        self.cur.close()
        self.conn.close()




def main():
    db = Database()
    db.create_db()
    db.add_client("Sergey", "Bobrov", "serbobr@mail.com", [698986565])
    db.add_client("Jack", "Bobrov", "jbobr@mail.com", [69898225, 666666])
    client_id = db.add_client("Jack", "Sparrow", "black.emerald@sea.com", [9586341, 653546778])
    db.add_phone(client_id, 99999999)
    db.change_client(client_id, "Zheka", "Vorobiev", "black.toss@sea.com", [11111, 222222222, 33333333])
    db.delete_phone(client_id, 11111)
    db.delete_client(client_id)
    db.find_client(phone=666666)
    db.find_client(email="serbobr@mail.com")
    db.find_client("Jack", "Sparrow")
    db.find_client(last_name="Bobrov")
    db.find_client("Jack")
    db.close()


if __name__ == "__main__":
    main()