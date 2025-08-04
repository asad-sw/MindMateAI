# MindMate AI - Testing & Demo Guide

This guide provides instructions on how to run the MindMate AI application and test its core features.

---

### 1. Running the Application

**Prerequisites:**
- Python 3.x and Pip
- A web browser and a code editor (like VS Code with the "Live Server" extension)

**Backend Setup:**

1.  Open a terminal and navigate to the `/backend` directory.
2.  Create and activate a Python virtual environment.
3.  Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the server:
    ```bash
    flask run
    ```
    > The backend will be running at `http://127.0.0.1:5000`.

**Frontend Setup:**

1.  In your code editor, open the `/frontend` folder.
2.  Right-click on `index.html` and open it with Live Server.
3.  Right-click on `dashboard.html` and open it in a new tab with Live Server.

---

### 2. Demo Flow & Features to Test

This flow is designed to showcase the full power of MindMate AI for the hackathon judges.

**Step 1: Test the "High" Severity Case**

-   **Action:** On the main form (`index.html`), enter a name and age. For the symptoms, type something that indicates significant distress, like: **"I feel hopeless all the time, I can't sleep, and I have no energy to do anything."**
-   **What to Look For:**
    -   The AI should return a supportive and empathetic recommendation.
    -   The recommendation box should turn **red**, and the severity should be clearly marked as **"High"**.
    -   The submission should be saved to the `triage_log.csv` file in the `/backend` folder.

**Step 2: Test the "Medium" Severity Case**

-   **Action:** Click "New Submission." For the symptoms, type something concerning but less critical, like: **"I've been feeling very anxious and stressed out from work lately."**
-   **What to Look For:**
    -   The recommendation box should turn **orange**, and the severity should be marked as **"Medium"**.

**Step 3: View the Clinical Dashboard**

-   **Action:** Go to the `dashboard.html` tab you opened earlier and refresh the page.
-   **What to Look For:**
    -   You should see both of your new submissions at the top of the list.
    -   The severity badges should be color-coded (red for your first entry, orange for the second).
    -   **Test the filter:** Use the "Filter by Severity" dropdown and select "High." The list should update to show only the high-severity case. This demonstrates the core value proposition for clinic staff.
    -   **Test Pagination:** If you have more than 10 entries, test the "Previous" and "Next" buttons.

This testing flow demonstrates our complete, end-to-end solution and highlights our innovative use of agentic AI for real-world impact.
