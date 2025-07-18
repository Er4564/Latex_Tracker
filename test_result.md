#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Create an app to track .tex files in Overleaf with organized folders for each subject, supporting manual upload, git integration, copy-paste content, multi-level organization (term/semester → subject → files), file version history, last modified dates, file size and word count, compilation status, notes/tags, search functionality, file preview, and export options."

backend:
  - task: "Create comprehensive LaTeX file tracking API"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: unknown
        agent: "main"
        comment: "Implemented full backend with terms, subjects, files, version history, search, upload, and export endpoints"
      - working: true
        agent: "testing"
        comment: "Comprehensive testing completed successfully. All core API endpoints working: Terms CRUD ✅, Subjects CRUD ✅, Files CRUD ✅, File Upload ✅, Search ✅, Export (single & bulk) ✅, Dashboard Stats ✅, Error Handling ✅. Fixed two critical issues: 1) Bulk export race condition in temp file cleanup, 2) Subject update validation requiring separate SubjectUpdate model. Added LaTeX compilation feature with xelatex - auto-compilation on file creation, manual compilation endpoint, PDF download, proper error handling for compilation failures. System handles 14 files with various compilation statuses. All 7 core functionality areas tested and working."

frontend:
  - task: "Create LaTeX file tracker UI with dashboard, file management, and preview"
    implemented: true
    working: unknown
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: unknown
        agent: "main"
        comment: "Implemented complete frontend with dashboard, file upload, search, preview, and management interfaces"

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Create comprehensive LaTeX file tracking API"
    - "Create LaTeX file tracker UI with dashboard, file management, and preview"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "Built comprehensive LaTeX file tracking app with all requested features. Need to test backend API endpoints for terms, subjects, files, search, upload, and export functionality."
  - agent: "testing"
    message: "Backend testing completed successfully! All core API functionality working perfectly. Fixed 2 critical issues: bulk export race condition and subject update validation. Added LaTeX compilation feature with xelatex - files now auto-compile to PDF on creation, with manual compilation endpoint and PDF download. System handles compilation errors gracefully. All 7 core areas tested: API connectivity, Terms CRUD, Subjects CRUD, Files CRUD, Search, Export, and Stats. Ready for frontend integration or user acceptance testing."