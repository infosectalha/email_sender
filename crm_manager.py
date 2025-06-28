import sqlite3
import os
from datetime import datetime

DATABASE_NAME = 'clients.db'

class CRMManager:
    def __init__(self, db_name=DATABASE_NAME):
        self.db_name = db_name
        self._conn = None
        self._cursor = None
        self._connect()
        self._create_table()

    def _connect(self):
        """Establishes a connection to the SQLite database."""
        self._conn = sqlite3.connect(self.db_name)
        self._conn.row_factory = sqlite3.Row # Access columns by name
        self._cursor = self._conn.cursor()

    def _close(self):
        """Closes the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._cursor = None

    def __enter__(self):
        # self._connect() # Already connected in init, or reconnect if needed
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()

    def _execute_query(self, query, params=None, commit=False, fetch_one=False, fetch_all=False):
        """Helper function to execute queries."""
        if self._conn is None or self._cursor is None: # Ensure connection is active
            self._connect()

        try:
            self._cursor.execute(query, params or ())
            if commit:
                self._conn.commit()

            result = None
            if fetch_one:
                result = self._cursor.fetchone()
            elif fetch_all:
                result = self._cursor.fetchall()

            # For INSERT, UPDATE, DELETE, lastrowid or rowcount might be useful
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                 return self._cursor.rowcount # or self._cursor.lastrowid for INSERT

            return result
        except sqlite3.Error as e:
            print(f"SQLite error: {e} \nQuery: {query} \nParams: {params}")
            # Optionally re-raise or handle more gracefully
            return None # Or False, or raise custom exception

    def _create_table(self):
        """Creates the clients table if it doesn't exist."""
        query = """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            status TEXT DEFAULT 'Prospect',
            tags TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_interaction_date TEXT
        );
        """
        # Also, an interactions table might be better for logging multiple contacts
        # For now, last_interaction_date is on the client.
        query_interactions = """
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            interaction_type TEXT NOT NULL, -- e.g., 'Email Sent', 'Reply Received', 'Call'
            template_used TEXT, -- If email
            subject TEXT, -- If email
            interaction_date TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
        );
        """
        self._execute_query(query, commit=True)
        self._execute_query(query_interactions, commit=True)


    def add_or_update_client(self, email, name=None, status=None, tags=None, notes=None, interaction_log=None):
        """
        Adds a new client or updates an existing one based on email.
        If status is provided, it's updated. Tags and notes are appended or overwritten if provided.
        `interaction_log` is a dict for logging an interaction if the client is added/updated.
        """
        client = self.get_client_by_email(email)
        now_iso = datetime.now().isoformat()

        current_tags = []
        if client and client['tags']:
            current_tags = client['tags'].split(',')

        new_tags_list = []
        if isinstance(tags, str):
            new_tags_list = [t.strip() for t in tags.split(',') if t.strip()]
        elif isinstance(tags, list):
            new_tags_list = [str(t).strip() for t in tags if str(t).strip()]

        updated_tags_set = set(current_tags + new_tags_list)
        final_tags_str = ",".join(sorted(list(updated_tags_set))) if updated_tags_set else None

        if client: # Update existing client
            client_id = client['id']
            update_fields = {}
            if name is not None and name != client['name']:
                update_fields['name'] = name
            if status is not None and status != client['status']:
                update_fields['status'] = status
            if final_tags_str is not None and final_tags_str != client['tags']: # Check if actually changed
                 update_fields['tags'] = final_tags_str
            if notes is not None: # Append notes or overwrite? For now, let's assume overwrite if provided
                update_fields['notes'] = notes # Or: client['notes'] + "\n" + notes if appending

            if update_fields:
                set_clause = ", ".join([f"{key} = ?" for key in update_fields.keys()])
                params = list(update_fields.values()) + [client_id]
                query = f"UPDATE clients SET {set_clause} WHERE id = ?"
                self._execute_query(query, params, commit=True)

        else: # Add new client
            query = """
            INSERT INTO clients (email, name, status, tags, notes, last_interaction_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            # Use provided status or default to 'Prospect'
            effective_status = status if status is not None else 'Prospect'
            params = (email, name, effective_status, final_tags_str, notes, now_iso, now_iso)
            self._execute_query(query, params, commit=True)
            client_id = self._cursor.lastrowid # Get ID of the newly inserted client

        if interaction_log and client_id:
            self.log_interaction(
                client_id=client_id,
                interaction_type=interaction_log.get('type', 'Email Sent'), # Default type
                template_used=interaction_log.get('template'),
                subject=interaction_log.get('subject'),
                notes=interaction_log.get('notes') # e.g. "Sent cold_outreach"
            )
        elif interaction_log and not client_id : # Should not happen if client exists or is added
             print(f"Warning: Could not log interaction for {email}, client_id not found.")


        return client_id # Return the ID of the client

    def get_client_by_email(self, email):
        """Retrieves a client by their email address."""
        query = "SELECT * FROM clients WHERE email = ?"
        return self._execute_query(query, (email,), fetch_one=True)

    def get_client_by_id(self, client_id):
        """Retrieves a client by their ID."""
        query = "SELECT * FROM clients WHERE id = ?"
        return self._execute_query(query, (client_id,), fetch_one=True)

    def get_all_clients(self, status_filter=None, tag_filter=None):
        """Retrieves all clients, optionally filtered by status or tag."""
        base_query = "SELECT * FROM clients"
        conditions = []
        params = []

        if status_filter:
            conditions.append("status = ?")
            params.append(status_filter)
        if tag_filter:
            conditions.append("tags LIKE ?")
            params.append(f"%{tag_filter}%") # Simple LIKE search for tag

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY created_at DESC"
        return self._execute_query(base_query, params, fetch_all=True)

    def update_client_status(self, client_id_or_email, new_status):
        """Updates the status of a client."""
        client = self.get_client_by_id(client_id_or_email) if isinstance(client_id_or_email, int) else self.get_client_by_email(client_id_or_email)
        if client:
            query = "UPDATE clients SET status = ?, last_interaction_date = ? WHERE id = ?"
            self._execute_query(query, (new_status, datetime.now().isoformat(), client['id']), commit=True)
            return True
        return False

    def log_interaction(self, client_id, interaction_type, template_used=None, subject=None, notes=None):
        """Logs an interaction for a client."""
        query = """
        INSERT INTO interactions (client_id, interaction_type, template_used, subject, interaction_date, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        interaction_date = datetime.now().isoformat()
        params = (client_id, interaction_type, template_used, subject, interaction_date, notes)
        self._execute_query(query, params, commit=True)

        # Also update client's last_interaction_date
        update_client_query = "UPDATE clients SET last_interaction_date = ? WHERE id = ?"
        self._execute_query(update_client_query, (interaction_date, client_id), commit=True)
        return self._cursor.lastrowid

    def get_client_interactions(self, client_id_or_email):
        """Retrieves all interactions for a specific client."""
        client = self.get_client_by_id(client_id_or_email) if isinstance(client_id_or_email, int) else self.get_client_by_email(client_id_or_email)
        if client:
            query = "SELECT * FROM interactions WHERE client_id = ? ORDER BY interaction_date DESC"
            return self._execute_query(query, (client['id'],), fetch_all=True)
        return []

    def search_clients(self, search_term):
        """Searches clients by email, name, or tags."""
        query = """
        SELECT * FROM clients
        WHERE email LIKE ? OR name LIKE ? OR tags LIKE ?
        ORDER BY last_interaction_date DESC
        """
        term = f"%{search_term}%"
        return self._execute_query(query, (term, term, term), fetch_all=True)


if __name__ == '__main__':
    # Example Usage (and test)
    # Clean up old DB for fresh test run if needed
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
        print(f"Removed old {DATABASE_NAME} for fresh test.")

    with CRMManager() as crm:
        print(f"Database '{crm.db_name}' initialized.")

        # Add clients
        client1_id = crm.add_or_update_client(
            email="test1@example.com",
            name="Test User One",
            status="Prospect",
            tags="linkedin,tech",
            interaction_log={'type': 'Manual Add', 'notes': 'Initial prospect from list.'}
        )
        print(f"Added/Updated client 1, ID: {client1_id}")

        client2_id = crm.add_or_update_client(
            email="test2@example.com",
            name="Test User Two",
            status="Contacted",
            tags="referral",
            notes="Met at conference.",
            interaction_log={'type': 'Email Sent', 'template': 'cold_outreach.html', 'subject': 'Intro'}
        )
        print(f"Added/Updated client 2, ID: {client2_id}")

        crm.add_or_update_client(email="test1@example.com", name="Test User Uno (Updated)", status="Replied", tags="active_convo")
        print("Updated client 1 (test1@example.com)")

        # Get clients
        print("\n--- Client test1@example.com ---")
        client1_data = crm.get_client_by_email("test1@example.com")
        if client1_data:
            for key, value in client1_data.items():
                print(f"{key}: {value}")

        print("\n--- All Clients ---")
        all_clients = crm.get_all_clients()
        if all_clients:
            for client in all_clients:
                print(f"ID: {client['id']}, Email: {client['email']}, Name: {client['name']}, Status: {client['status']}, Tags: {client['tags']}, LastInteracted: {client['last_interaction_date']}")
        else:
            print("No clients found.")

        # Log another interaction for client 2
        if client2_id:
            crm.log_interaction(client2_id, "Reply Received", notes="Positive reply, asked for quote.")
            crm.update_client_status(client2_id, "Needs Quote")
            print(f"\nLogged reply for client ID {client2_id} and updated status.")

            print("\n--- Interactions for Client 2 ---")
            interactions_c2 = crm.get_client_interactions(client2_id)
            if interactions_c2:
                for interaction in interactions_c2:
                    print(f"  - Type: {interaction['interaction_type']}, Date: {interaction['interaction_date']}, Template: {interaction['template_used']}, Notes: {interaction['notes']}")
            else:
                print("  No interactions found for client 2.")

        print("\n--- Searching for 'tech' tag ---")
        tech_clients = crm.get_all_clients(tag_filter="tech")
        if tech_clients:
            for client in tech_clients:
                print(f"Found tech client: {client['email']}")
        else:
            print("No clients with 'tech' tag found.")

        print("\n--- Searching for 'User T' (name search) ---")
        search_results_name = crm.search_clients("User T")
        if search_results_name:
            for client in search_results_name:
                 print(f"Search found (name): {client['email']} - {client['name']}")
        else:
            print("No clients found for 'User T'.")

        print("\n--- Searching for 'example.com' (email search) ---")
        search_results_email = crm.search_clients("example.com")
        if search_results_email:
            for client in search_results_email:
                 print(f"Search found (email): {client['email']}")
        else:
            print("No clients found for 'example.com'.")


    print(f"\nCRM operations complete. Database '{DATABASE_NAME}' should contain the data.")
    # The connection is automatically closed by __exit__ when 'with' block ends.
