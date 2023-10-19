import psycopg2


connection = psycopg2.connect(
    database="scooters",
    user="admin",
    password="admin",
    host="localhost",
    port="5432"
)

cursor = connection.cursor()

cursor.execute(
    """
    CREATE TABLE scooter (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        battery_level DECIMAL NOT NULL
    );
    """
)

connection.commit()
connection.close()

print("Database setup complete.")
