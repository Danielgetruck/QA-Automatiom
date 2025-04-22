# app.py - Flask Dashboard for Playwright Automation Tests
from flask import Flask, render_template, request, jsonify
import subprocess
import os
import time
import threading
import queue
import datetime
import re

app = Flask(__name__, static_folder='static', template_folder='templates')

# Dictionary to store test results
test_running = False
process_queue = queue.Queue()
output_queue = queue.Queue()

# Create directories for test results and logs
os.makedirs("debug/screenshots", exist_ok=True)
os.makedirs("debug/traces", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Company-specific test definitions
COMPANIES = {
    "company1": {
        "name": "Jafora",
        "email": "jafora@getruck.co",
        "password": "Jafor2024",
        "branch": "Branch 70",
        "tests": {
            "login_test": {
                "name": "Login Test",
                "description": "Tests login functionality for Jafora",
                "script": "login_test.py",
                "script_args": "--company jafora --custom-login true",
                "last_run": None,
                "status": None,
                "output": []
            },
            "sync_test": {
                "name": "Sync Test",
                "description": "Tests synchronization functionality for Jafora's products",
                "script": "sync_Test.py",
                "script_args": "--company jafora --products all",
                "last_run": None,
                "status": None,
                "output": []
            },
            "branch_selection": {
                "name": "Branch Selection",
                "description": "Tests Jafora's branch selection workflow",
                "script": "Branch_Selection.py",
                "script_args": "--company jafora --branch 70",
                "last_run": None,
                "status": None,
                "output": []
            },
            "route_test": {
                "name": "Route Test",
                "description": "Tests route management for Jafora's distribution network",
                "script": "Route_Test.py",
                "script_args": "--company jafora --routes central",
                "last_run": None,
                "status": None,
                "output": []
            },
            "full_workflow": {
                "name": "Full Workflow",
                "description": "Tests the entire Jafora workflow from login to route management",
                "script": "login_automation.py",
                "script_args": "--company jafora --full-test true",
                "last_run": None,
                "status": None,
                "output": []
            },
            "delete_last_plan": {
                "name": "Delete Last Plan",
                "description": "Deletes the last plan for Jafora",
                "script": "Delete_last_plan.py",
                "script_args": "--company jafora",
                "last_run": None,
                "status": None,
                "output": []
            }
        }
    },
    "company2": {
        "name": "Hollandia",
        "email": "hollandia@getruck.co",
        "password": "Hollandia2024",
        "branch": "Branch 50",
        "tests": {
            "login_test": {
                "name": "Login Test",
                "description": "Tests login functionality for Hollandia",
                "script": "login_test.py",
                "script_args": "--company hollandia --custom-login true",
                "last_run": None,
                "status": None,
                "output": []
            },
            "sync_test": {
                "name": "Sync Test",
                "description": "Tests synchronization functionality for Hollandia's dairy products",
                "script": "sync_Test.py",
                "script_args": "--company hollandia --products dairy",
                "last_run": None,
                "status": None,
                "output": []
            },
            "branch_selection": {
                "name": "Branch Selection",
                "description": "Tests Hollandia's special branch selection process",
                "script": "Branch_Selection.py",
                "script_args": "--company hollandia --branch 50",
                "last_run": None,
                "status": None,
                "output": []
            }
        }
    },
    "company3": {
        "name": "Plassim",
        "email": "plassim@getruck.co",
        "password": "Plassim2024",
        "branch": "Branch 30",
        "tests": {
            "login_test": {
                "name": "Login Test",
                "description": "Tests login functionality for Plassim",
                "script": "login_test.py",
                "script_args": "--company plassim --custom-login true",
                "last_run": None,
                "status": None,
                "output": []
            },
            "sync_test": {
                "name": "Sync Test",
                "description": "Tests synchronization for Plassim plastic products",
                "script": "sync_Test.py",
                "script_args": "--company plassim --products plastics",
                "last_run": None,
                "status": None,
                "output": []
            },
            "branch_selection": {
                "name": "Branch Selection",
                "description": "Tests Plassim branch selection with regional filters",
                "script": "Branch_Selection.py",
                "script_args": "--company plassim --branch 30 --region north",
                "last_run": None,
                "status": None,
                "output": []
            },
            "route_test": {
                "name": "Route Test",
                "description": "Tests Plassim route management with plastic products",
                "script": "Route_Test.py",
                "script_args": "--company plassim --routes north --product-type plastics",
                "last_run": None,
                "status": None,
                "output": []
            }
        }
    },
    "company4": {
        "name": "Asofta",
        "email": "asofta@getruck.co",
        "password": "Asofta2024",
        "branch": "Branch 25",
        "tests": {
            "login_test": {
                "name": "Login Test",
                "description": "Tests login functionality for Asofta",
                "script": "login_test.py", 
                "script_args": "--company asofta --custom-login true",
                "last_run": None,
                "status": None,
                "output": []
            },
            "route_test": {
                "name": "Route Test",
                "description": "Tests Asofta's specialized route management system",
                "script": "Route_Test.py",
                "script_args": "--company asofta --routes national --priority-delivery true",
                "last_run": None,
                "status": None,
                "output": []
            },
            "full_workflow": {
                "name": "Full Workflow",
                "description": "Tests the complete Asofta distribution workflow",
                "script": "login_automation.py",
                "script_args": "--company asofta --full-test true --priority-accounts true",
                "last_run": None,
                "status": None,
                "output": []
            }
        }
    },
    "company5": {
        "name": "Infiniya",
        "email": "infiniya@getruck.co",
        "password": "Infiniya2024",
        "branch": "Branch 40",
        "tests": {
            "login_test": {
                "name": "Login Test",
                "description": "Tests login functionality for Infiniya",
                "script": "login_test.py",
                "script_args": "--company infiniya --custom-login true",
                "last_run": None,
                "status": None,
                "output": []
            },
            "sync_test": {
                "name": "Sync Test",
                "description": "Tests Infiniya's specialized product synchronization",
                "script": "sync_Test.py",
                "script_args": "--company infiniya --products tech",
                "last_run": None,
                "status": None,
                "output": []
            }
        }
    },
    "company6": {
        "name": "Vetmarket",
        "email": "vetmarket@getruck.co",
        "password": "Vetmarket2024",
        "branch": "Branch 60",
        "tests": {
            "login_test": {
                "name": "Login Test",
                "description": "Tests login functionality for Vetmarket",
                "script": "login_test.py",
                "script_args": "--company vetmarket --custom-login true",
                "last_run": None,
                "status": None,
                "output": []
            },
            "branch_selection": {
                "name": "Branch Selection",
                "description": "Tests Vetmarket's specialized branch selection for medical supplies",
                "script": "Branch_Selection.py",
                "script_args": "--company vetmarket --branch 60 --medical-supplies true",
                "last_run": None,
                "status": None,
                "output": []
            },
            "route_test": {
                "name": "Route Test",
                "description": "Tests Vetmarket's temperature-controlled route management",
                "script": "Route_Test.py",
                "script_args": "--company vetmarket --routes central --temperature-control true",
                "last_run": None,
                "status": None,
                "output": []
            }
        }
    },
    "company7": {
        "name": "Tempo",
        "email": "tempo@getruck.co",
        "password": "Tempo2024",
        "branch": "Branch 45",
        "tests": {
            "login_test": {
                "name": "Login Test",
                "description": "Tests login functionality for Tempo",
                "script": "login_test.py",
                "script_args": "--company tempo --custom-login true",
                "last_run": None,
                "status": None,
                "output": []
            },
            "sync_test": {
                "name": "Sync Test",
                "description": "Tests synchronization functionality for Tempo's beverage inventory",
                "script": "sync_Test.py",
                "script_args": "--company tempo --products beverages",
                "last_run": None,
                "status": None,
                "output": []
            },
            "branch_selection": {
                "name": "Branch Selection",
                "description": "Tests Tempo's branch selection with beverage specialization",
                "script": "Branch_Selection.py",
                "script_args": "--company tempo --branch 45 --beverage-type all",
                "last_run": None,
                "status": None,
                "output": []
            },
            "route_test": {
                "name": "Route Test",
                "description": "Tests Tempo's route management for beverage distribution",
                "script": "Route_Test.py",
                "script_args": "--company tempo --routes national --beverage-delivery true",
                "last_run": None,
                "status": None,
                "output": []
            }
        }
    }
}

# Worker thread to run tests
def worker():
    global test_running
    while True:
        try:
            # Get the next item from the queue
            item = process_queue.get()
            if item is None:
                break
            
            # Unpack the company_id and test_id
            company_id, test_id = item
            
            test_running = True
            
            # Get company and test info
            company = COMPANIES[company_id]
            test_data = company["tests"][test_id]
            
            # Update test status
            test_data["status"] = "running"
            test_data["output"] = []
            test_data["last_run"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Output initial line to indicate test start
            output_queue.put((company_id, test_id, f"Starting test for {company['name']}..."))
            output_queue.put((company_id, test_id, f"Using credentials: {company['email']}"))
            output_queue.put((company_id, test_id, f"Default branch: {company['branch']}"))
            
            # Create command to run the test script with company-specific args
            command = ["python", test_data["script"]]
            
            # Add the script_args if defined
            if "script_args" in test_data and test_data["script_args"]:
                command.extend(test_data["script_args"].split())
            
            # Add company credentials explicitly
            command.extend([
                "--email", company["email"],
                "--password", company["password"],
                "--branch", company["branch"].replace("Branch ", "")
            ])
                
            try:
                # Run the test process
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Stream the output with immediate flushing
                for line in iter(process.stdout.readline, ''):
                    line = line.strip()
                    if line:
                        test_data["output"].append(line)
                        output_queue.put((company_id, test_id, line))
                        # Ensure the queue doesn't grow too large
                        while output_queue.qsize() > 100:
                            try:
                                output_queue.get_nowait()
                            except queue.Empty:
                                break
                
                # Wait for process to complete and get return code
                return_code = process.wait()
                
                if return_code == 0:
                    test_data["status"] = "success"
                    output_queue.put((company_id, test_id, "Test completed successfully"))
                else:
                    test_data["status"] = "failed"
                    output_queue.put((company_id, test_id, f"Test failed with return code {return_code}"))
                    
            except Exception as e:
                test_data["status"] = "error"
                error_msg = f"Error running test: {str(e)}"
                test_data["output"].append(error_msg)
                output_queue.put((company_id, test_id, error_msg))
                
            test_running = False
            process_queue.task_done()
            
        except Exception as e:
            print(f"Worker thread error: {str(e)}")
            test_running = False

# Start worker thread
worker_thread = threading.Thread(target=worker)
worker_thread.daemon = True
worker_thread.start()

@app.route('/')
def index():
    return render_template('index.html', companies=COMPANIES)

@app.route('/company_tests/<company_id>')
def company_tests(company_id):
    """Returns the tests available for a specific company"""
    if company_id not in COMPANIES:
        return jsonify({"status": "error", "message": "Invalid company ID"})
    
    company = COMPANIES[company_id]
    
    return jsonify({
        "status": "success",
        "company": company["name"],
        "tests": company["tests"]
    })

@app.route('/run_test', methods=['POST'])
def run_test():
    test_id = request.form.get('test_id')
    company_id = request.form.get('company')
    
    if company_id not in COMPANIES:
        return jsonify({"status": "error", "message": "Invalid company ID"})
    
    company = COMPANIES[company_id]
    
    if test_id not in company["tests"]:
        return jsonify({"status": "error", "message": "Invalid test ID for this company"})
    
    if test_running:
        return jsonify({"status": "error", "message": "Another test is already running"})
    
    # Queue the test to run with company-specific details
    test_data = company["tests"][test_id]
    test_data["status"] = "running"
    
    # Queue the test with company and test IDs
    process_queue.put((company_id, test_id))
    
    return jsonify({
        "status": "success", 
        "message": f"Running test: {test_data['name']} for {company['name']}"
    })

@app.route('/test_status/<company_id>/<test_id>')
def test_status(company_id, test_id):
    """Get status for a specific company's test"""
    if company_id not in COMPANIES:
        return jsonify({"status": "error", "message": "Invalid company ID"})
    
    company = COMPANIES[company_id]
    
    if test_id not in company["tests"]:
        return jsonify({"status": "error", "message": "Invalid test ID for this company"})
    
    test_data = company["tests"][test_id]
    
    return jsonify({
        "status": test_data["status"],
        "last_run": test_data["last_run"],
        "output": test_data["output"]
    })

@app.route('/stream')
def stream():
    def generate():
        while True:
            try:
                data = output_queue.get(block=False)
                
                if len(data) == 2:
                    # Just company_id and test_id, no message
                    company_id, test_id = data
                    yield f"data: {company_id}:{test_id}:\n\n"
                else:
                    company_id, test_id, line = data
                    yield f"data: {company_id}:{test_id}:{line}\n\n"
                    
                # Flush the output immediately
                yield f": heartbeat\n\n"  # Empty comment to force flush
            except queue.Empty:
                # Send a heartbeat comment to keep connection alive
                yield f": heartbeat\n\n"
            
            time.sleep(0.1)
    
    response = app.response_class(
        generate(),
        mimetype='text/event-stream'
    )
    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response

if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Prevent caching
    app.run(debug=True, threaded=True, host='0.0.0.0')