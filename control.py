import os
import sqlite3
import subprocess
import sys

def extract_student_id():
    """
    Extract the student's GitHub repository name or directory from the command-line argument.
    """
    if len(sys.argv) > 1:
        # Assuming the repo name is passed as an argument
        user_repo = sys.argv[1]
        print(f"Repository or Directory Name: {user_repo}")
        return user_repo
    else:
        print("Error: No repository name provided.")
        sys.exit(1)


def fetch_data_from_directories(student_code_dir, autograder_output_file, readme_file):
    """Fetch data from the specified directories with encoding handling."""
    student_code_data = ""
    for filename in os.listdir(student_code_dir):
        file_path = os.path.join(student_code_dir, filename)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    student_code_data += f"File: {filename}\n{file.read()}\n\n"
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='ISO-8859-1') as file:
                        student_code_data += f"File: {filename}\n{file.read()}\n\n"
                except UnicodeDecodeError:
                    print(f"Warning: Could not read file {filename} due to encoding issues.")

    try:
        with open(autograder_output_file, 'r', encoding='utf-8') as file:
            autograder_output = file.read()
    except UnicodeDecodeError:
        with open(autograder_output_file, 'r', encoding='ISO-8859-1') as file:
            autograder_output = file.read()

    try:
        with open(readme_file, 'r', encoding='utf-8') as file:
            professor_instructions = file.read()
    except UnicodeDecodeError:
        with open(readme_file, 'r', encoding='ISO-8859-1') as file:
            professor_instructions = file.read()

    return student_code_data, autograder_output, professor_instructions


def send_data_to_ollama(student_code_data, autograder_output, professor_instructions):
    """Send combined data to the Ollama model."""
    prompt = (
        f"DO NOT CORRECT THE CODE!!! ONLY PROVIDE Question-based guided FEEDBACK BASED ON THIS:\n"
        f"**Student Code:**\n{student_code_data}\n\n"
        f"**Autograder Output:**\n{autograder_output}\n\n"
        f"**Professor Instructions:**\n{professor_instructions}\n\n"
    )

    try:
        result = subprocess.run(
            ['ollama', 'run', 'ux1'],
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"Error running Ollama: {result.stderr}")
            return {"error": result.stderr}
        return {"response": result.stdout}
    except Exception as e:
        print(f"Failed to run Ollama model: {e}")
        return {"error": str(e)}
def write_feedback_to_file(student_id, assignment_id, feedback):
    """Write feedback into a Markdown file."""
    feedback_file_path = f"/home/{os.getenv('USER')}/feedback.md"
    try:
        with open(feedback_file_path, 'w', encoding='utf-8') as file:
            file.write(f"# Feedback for {student_id}\n\n")
            file.write(feedback)
        print(f"Feedback saved to {feedback_file_path}")
        return feedback_file_path
    except Exception as e:
        print(f"Failed to write to Feedback.md: {e}")
        return None
        if conn:
            conn.close()

def insert_into_database(student_id, assignment_id, test_id, feedback, feedback_file_path, student_code_dir, autograder_output_file):
    """Insert all data into SQLite database."""
    db_path = os.path.join(os.getenv("HOME"), "agllmdatabase.db")  # Updated database path
    conn = None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert student code into submissions table
        for filename in os.listdir(student_code_dir):
            file_path = os.path.join(student_code_dir, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    code_content = file.read()
                cursor.execute(
                    '''
                    INSERT INTO submissions (student_repo, assignment_id, code, submitted_at)
                    VALUES (?, ?, ?, datetime('now', 'utc'))
                    ''',
                    (student_id, assignment_id, code_content)
                )

        # Retrieve the last inserted submission ID for linking feedback and autograder outputs
        submission_id = cursor.lastrowid

        # Insert autograder output into autograder_outputs table
        with open(autograder_output_file, 'r', encoding='utf-8') as file:
            autograder_output = file.read()
        cursor.execute(
            '''
            INSERT INTO autograder_outputs (submission_id, output, generated_at)
            VALUES (?, ?, datetime('now', 'utc'))
            ''',
            (submission_id, autograder_output)
        )

        # Insert feedback into feedback table
        cursor.execute(
            '''
            INSERT INTO feedback (submission_id, feedback_text, generated_at)
            VALUES (?, ?, datetime('now', 'utc'))
            ''',
            (submission_id, feedback)
        )

        conn.commit()
        print("Data successfully inserted into the database.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        if conn:
            conn.close()

def main():
    student_code_dir = os.path.expanduser('/home/CN1030173/logs/studentcode')
    autograder_output_file = os.path.expanduser('/home/CN1030173/logs/autograder_output.txt')
    readme_file = os.path.expanduser('/home/CN1030173/logs/README.md')

    student_id = extract_student_id()

    assignment_id = 101
    test_id = 1001

    student_code_data, autograder_output, professor_instructions = fetch_data_from_directories(
        student_code_dir, autograder_output_file, readme_file
    )

    model_response = send_data_to_ollama(student_code_data, autograder_output, professor_instructions)

    if "error" not in model_response:
        feedback = model_response.get("response", "No feedback generated.")
        feedback_file_path = write_feedback_to_file(student_id, assignment_id, feedback)
        if feedback_file_path:
            insert_into_database(student_id, assignment_id, test_id, feedback, feedback_file_path, student_code_dir, autograder_output_file)
    else:
        print("Error in generating feedback:", model_response["error"])


if __name__ == "__main__":
    main()
