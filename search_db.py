from rich.console import Console
from rich.panel import Panel
import sqlite3
import argparse
import shutil
import os

def fetch_data(student_repo):
    """Fetch data from the database for a specific student repository."""
    db_path = os.path.join(os.getenv("HOME"), "agllmdatabase.db")  # Path to the SQLite database
    conn = None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch submissions
        cursor.execute("""
            SELECT id, assignment_id, code, submitted_at
            FROM submissions
            WHERE student_repo = ?
        """, (student_repo,))
        submissions = cursor.fetchall()

        # Fetch feedback
        cursor.execute("""
            SELECT f.id, f.submission_id, f.feedback_text, f.generated_at
            FROM feedback f
            JOIN submissions s ON f.submission_id = s.id
            WHERE s.student_repo = ?
        """, (student_repo,))
        feedbacks = cursor.fetchall()

        # Fetch autograder outputs
        cursor.execute("""
            SELECT a.id, a.submission_id, a.output, a.generated_at
            FROM autograder_outputs a
            JOIN submissions s ON a.submission_id = s.id
            WHERE s.student_repo = ?
        """, (student_repo,))
        autograder_outputs = cursor.fetchall()

        return submissions, feedbacks, autograder_outputs

    except sqlite3.Error as e:
        raise Exception(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

def center_text(text, width):
    """Center text within a given width."""
    return text.center(width)
def display_data(student_repo, submissions, feedbacks, autograder_outputs):
    """Display data using rich-enhanced terminal output."""
    console = Console()
    terminal_width = shutil.get_terminal_size().columns

    # Centered Header
    header_text = f"Data for {student_repo}"
    console.print(
        Panel(
            center_text(header_text, terminal_width),
            expand=False,
            border_style="bright_cyan",
            title="[bold yellow]Student Repository[/bold yellow]",
            title_align="center",
        )
    )

    # Submissions Table
    console.print("\n[bold underline green]Submissions[/bold underline green]")
    if submissions:
        for submission in submissions:
            console.print(
                Panel(
                    f"[bold yellow]Submission ID[/bold yellow]: {submission[0]}\n"
                    f"[bold yellow]Assignment ID[/bold yellow]: {submission[1]}\n"
                    f"[bold yellow]Code[/bold yellow]:\n[dim cyan]{submission[2]}\n\n"
                    f"[bold yellow]Submitted At[/bold yellow]: {submission[3]}",
                    border_style="green",
                )
            )
    else:
        console.print("[red]No submissions found.[/red]")

    # Feedback Table
    console.print("\n[bold underline blue]Feedback[/bold underline blue]")
    if feedbacks:
        for feedback in feedbacks:
            console.print(
                Panel(
                    f"[bold yellow]Feedback ID[/bold yellow]: {feedback[0]}\n"
                    f"[bold yellow]Submission ID[/bold yellow]: {feedback[1]}\n"
                    f"[bold yellow]Feedback[/bold yellow]: {feedback[2]}\n\n"
                    f"[bold yellow]Generated At[/bold yellow]: {feedback[3]}",
                    border_style="blue",
                )
            )
    else:
        console.print("[red]No feedback found.[/red]")

    # Autograder Outputs Table
    console.print("\n[bold underline magenta]Autograder Outputs[/bold underline magenta]")
    if autograder_outputs:
        for output in autograder_outputs:
            console.print(
                Panel(
                    f"[bold yellow]Output ID[/bold yellow]: {output[0]}\n"
                    f"[bold yellow]Submission ID[/bold yellow]: {output[1]}\n"
                    f"[bold yellow]Output[/bold yellow]:\n[dim cyan]{output[2]}\n\n"
                    f"[bold yellow]Generated At[/bold yellow]: {output[3]}",
                    border_style="magenta",
                )
            )
    else:
        console.print("[red]No autograder outputs found.[/red]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Display student data from the database.")
    parser.add_argument("student_repo", help="The student repository (e.g., hw3-LeonardAlmeida)")
    args = parser.parse_args()

    try:
        # Fetch and display data for the given student repository
        submissions, feedbacks, autograder_outputs = fetch_data(args.student_repo)
        display_data(args.student_repo, submissions, feedbacks, autograder_outputs)
    except Exception as e:
        Console().print(f"[red]Error:[/red] {e}")
