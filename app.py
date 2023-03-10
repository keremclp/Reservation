from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import json

app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'busiwapp42'
app.config['MYSQL_DATABASE_HOST'] = '<database_host>'
app.config['MYSQL_DATABASE_DB'] = '<database_name>'
mysql = MySQL(app)


# Establish a global database connection and cursor
conn = None
cursor = None

@app.before_first_request
def create_connection():
    global conn, cursor
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        create_table_query = """
            CREATE TABLE IF NOT EXISTS reservations (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                name VARCHAR(255), 
                date DATE
            );
        """
        cursor.execute(create_table_query)
        conn.commit()
    except Exception as e:
        print("Error connecting to the database: ", e)

@app.teardown_appcontext
def close_connection(error):
    global conn, cursor
    if cursor:
        cursor.close()
    if conn:
        conn.close()

# Route to retrieve all reservations from the database
@app.route('/reservations', methods=['GET'])
def get_all_reservations():
    global cursor
    try:
        # Retrieve all reservations from the database using the global cursor
        query = "SELECT * FROM reservations"
        cursor.execute(query)
        reservations = cursor.fetchall()

        if not reservations:
            return jsonify({'error': 'No reservations found'}), 404

        # Return the reservations as a JSON object
        return jsonify(reservations), 200
    except Exception as e:
        print("Error retrieving reservations from the database: ", e)
        return jsonify({'error': 'Error retrieving reservations from the database'}), 500


@app.route('/reservations/<int:reservation_id>', methods=['GET'])
def get_reservation(reservation_id):
    try:
        # Check if reservation_id is an integer
        if not isinstance(reservation_id, int):
            return jsonify({'error': 'Reservation ID must be an integer.'}), 400

        # Retrieve the specified reservation from the database
        query = "SELECT * FROM reservations WHERE id = %s"
        cursor.execute(query, (reservation_id,))
        reservation = cursor.fetchone()

        # If the reservation is not found, return a 404 error
        if not reservation:
            return jsonify({"error": "Reservation not found"}), 404

        # Return the reservation as a JSON object
        return jsonify(reservation)
    except Exception as e:
        print("Error retrieving reservation from the database: ", e)
        return jsonify({'error': 'Error retrieving reservation from the database'}), 500


@app.route('/reservations', methods=['POST'])
def create_reservation():
    try:
        # Get the name and date of the reservation from the request body
        data = request.get_json()
        name = data.get('name')
        date = data.get('date')

        # Validate the name and date
        if not name or not date:
            return jsonify({'error': 'Name and date are required fields.'}), 400
        
        # Insert the new reservation into the database
        query = "INSERT INTO reservations (name, date) VALUES (?, ?)"
        cursor.execute(query, (name, date))
        conn.commit()

        # Get the ID of the new reservation
        reservation_id = cursor.lastrowid

        # Return a success message with the ID of the newly created reservation
        return jsonify({'message': f'Reservation created with ID {reservation_id}.'}), 201

    except json.JSONDecodeError:
        # Handle invalid request data errors
        return jsonify({'error': 'Invalid JSON request data.'}), 400

    except TypeError:
        # Handle invalid request data errors
        return jsonify({'error': 'Invalid request data.'}), 400

    except Exception as e:
        # Handle all other errors
        return jsonify({'error': f'Error creating reservation with ID {reservation_id}: {e}.'}), 500


@app.route('/reservations/<int:reservation_id>', methods=['PUT'])
def update_reservation(reservation_id):
    try:
        # Check if reservation_id is an integer and positive
        if not isinstance(reservation_id, int) or reservation_id <= 0:
            return jsonify({'error': 'Reservation ID must be a positive integer.'}), 400

        # Get the updated name and date of the reservation from the request body
        data = request.get_json()
        name = data.get('name')
        date = data.get('date')

        # Validate the name and date
        if not name or not date:
            return jsonify({'error': 'Name and date are required fields.'}), 400
        
        # Retrieve the specified reservation from the database
        query = "SELECT * FROM reservations WHERE id = ?"
        cursor.execute(query, (reservation_id,))
        reservation = cursor.fetchone()

        if not reservation:
            return jsonify({'error': 'Reservation not found.'}), 404

        # Update the specified reservation in the database
        query = "UPDATE reservations SET name=?, date=? WHERE id=?"
        cursor.execute(query, (name, date, reservation_id))
        conn.commit()
        
        # Return a success message with a 200 status code
        return jsonify({'message': 'Reservation updated.'}), 200

    except json.JSONDecodeError:
        # Handle invalid request data errors
        return jsonify({'error': 'Invalid JSON request data.'}), 400

    except TypeError:
        # Handle invalid request data errors
        return jsonify({'error': 'Invalid request data.'}), 400

    except Exception as e:
        # Handle all other errors
        return jsonify({'error': f'Error updating reservation with ID {reservation_id}: {e}.'}), 500

@app.route('/reservations/<int:reservation_id>', methods=['DELETE'])
def delete_reservation(reservation_id):
    # Check if reservation_id is positive
    if not isinstance(reservation_id,int) or reservation_id <= 0 :
        return jsonify({'error': 'Reservation ID must be a positive integer.'}), 400
        
    try:
        
        # Retrieve the specified reservation from the database

        query = "SELECT * FROM reservations WHERE id = ?"
        cursor.execute(query, (reservation_id,))
        reservation = cursor.fetchone()
        
        if not reservation:
            return jsonify({'error': 'Reservation not found.'}), 404
                
        # Delete the reservation from the database
        query = "DELETE FROM reservations WHERE id=?"
        cursor.execute(query, (reservation_id,))
        conn.commit()      

        # Return a success message with a 204 status code
        return 'Reservation deleted', 204

    except json.JSONDecodeError:
        # Handle invalid request data errors
        return jsonify({'error': 'Invalid JSON request data.'}), 400
    
    except TypeError:
        # Handle invalid request data errors
        return jsonify({'error': 'Invalid request data.'}), 400

    except Exception as e:
        # Handle all other errors
        return jsonify({'error': f'Error deleting reservation with ID {reservation_id}: {e}.'}), 500


if __name__ == '__main__':
    app.run(debug=True)