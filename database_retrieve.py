import sqlite3
import os
import argparse

def generate_markdown(student_repo):
    """Generate Markdown output for a specific student repository."""
    db_path = os.path.join(os.getenv("HOME"), "agllmdatabase.db")  # Path to the database
    output_file = os.path.expanduser(f"~/student_data_{student_repo}.md")  # Output file for markdown
    conn = None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the student_repo exists
        cursor.execute("SELECT 1 FROM submissions WHERE student_repo = ? LIMIT 1", (student_repo,))
        if not cursor.fetchone():
            print(f"No data found for student repository: {student_repo}")
            return

        with open(output_file, "w") as file:
            file.write(f"# Data for {student_repo}\n\n")

            # Submissions
            cursor.execute("""
                SELECT id, assignment_id, code, submitted_at
                FROM submissions
                WHERE student_repo = ?
            """, (student_repo,))
            submissions = cursor.fetchall()
            file.write("## Submissions\n\n")
            for submission in submissions:
                file.write(f"- **Submission ID**: {submission[0]}\n")
                file.write(f"  - **Assignment ID**: {submission[1]}\n")
                file.write(f"  - **Code**:\n```\n{submission[2]}\n```\n")
                file.write(f"  - **Submitted At**: {submission[3]}\n\n")

            # Feedback
            cursor.execute("""
                SELECT f.id, f.submission_id, f.feedback_text, f.generated_at
                FROM feedback f
                JOIN submissions s ON f.submission_id = s.id
                WHERE s.student_repo = ?
            """, (student_repo,))
            feedbacks = cursor.fetchall()
            file.write("## Feedback\n\n")
            for feedback in feedbacks:
                file.write(f"- **Feedback ID**: {feedback[0]}\n")
                file.write(f"  - **Submission ID**: {feedback[1]}\n")
                file.write(f"  - **Feedback**:\n{feedback[2]}\n")
                file.write(f"  - **Generated At**: {feedback[3]}\n\n")

            # Autograder Outputs
            cursor.execute("""
                SELECT a.id, a.submission_id, a.output, a.generated_at
                FROM autograder_outputs a
                JOIN submissions s ON a.submission_id = s.id
                WHERE s.student_repo = ?
            """, (student_repo,))
            autograder_outputs = cursor.fetchall()
            file.write("## Autograder Outputs\n\n")
            for output in autograder_outputs:
                file.write(f"- **Output ID**: {output[0]}\n")
                file.write(f"  - **Submission ID**: {output[1]}\n")
                file.write(f"  - **Output**:\n```\n{output[2]}\n```\n")
                file.write(f"  - **Generated At**: {output[3]}\n\n")

        print(f"Markdown file created: {output_file}")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Argument parser to accept the student_repo as a command-line argument
    parser = argparse.ArgumentParser(description="Retrieve data for a specific student and output it as Markdown.")
    parser.add_argument("student_repo", help="The student repository (e.g., hw3-LeonardAlmeida)")
    args = parser.parse_args()

    # Generate Markdown for the specified student repository
    generate_markdown(args.student_repo)
