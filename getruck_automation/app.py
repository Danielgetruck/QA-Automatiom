# app.py - Flask Dashboard for Playwright Automation Tests
from flask import Flask, render_template, request, jsonify
import subprocess
import os
import time
import threading
import queue
import datetime
import re

app = Flask(__name__)

# Dictionary to store test results
test_results = {}
test_running = False
process_queue = queue.Queue()
output_queue = queue.Queue()

# Create directories for test results and logs
os.makedirs("debug/screenshots", exist_ok=True)
os.makedirs("debug/traces", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Test definitions - you can customize these
TESTS = {
    "login_test": {
        "name": "Login Test",
        "description": "Tests login functionality",
        "script": "login_automation.py",
        "last_run": None,
        "status": None,
        "output": []
    },
    "sync_test": {
        "name": "Sync Test",
        "description": "Tests synchronization functionality",
        "script": "sync_automation.py",
        "last_run": None,
        "status": None,
        "output": []
    },
    "branch_selection": {
        "name": "Branch Selection",
        "description": "Tests branch selection functionality",
        "script": "branch_automation.py",
        "last_run": None,
        "status": None,
        "output": []
    },
    "route_test": {
        "name": "Route Test",
        "description": "Tests route management functionality",
        "script": "route_automation.py",
        "last_run": None,
        "status": None,
        "output": []
    },
    "full_workflow": {
        "name": "Full Workflow",
        "description": "Tests the entire workflow from login to route management",
        "script": "full_workflow.py",
        "last_run": None,
        "status": None,
        "output": []
    }
}

# Worker thread to run tests
def worker():
    global test_running
    while True:
        try:
            test_id = process_queue.get()
            if test_id is None:
                break
                
            test_running = True
            TESTS[test_id]["status"] = "running"
            TESTS[test_id]["output"] = []
            TESTS[test_id]["last_run"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Output initial line
            output_queue.put((test_id,))
            
            # Create command to run the test script
            command = ["python", TESTS[test_id]["script"]]
            
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
                        TESTS[test_id]["output"].append(line)
                        output_queue.put((test_id, line))
                        # Ensure the queue doesn't grow too large
                        while output_queue.qsize() > 100:
                            try:
                                output_queue.get_nowait()
                            except queue.Empty:
                                break
                
                # Wait for process to complete and get return code
                return_code = process.wait()
                
                if return_code == 0:
                    TESTS[test_id]["status"] = "success"
                    output_queue.put((test_id, "Test completed successfully"))
                else:
                    TESTS[test_id]["status"] = "failed"
                    output_queue.put((test_id, f"Test failed with return code {return_code}"))
                    
            except Exception as e:
                TESTS[test_id]["status"] = "error"
                error_msg = f"Error running test: {str(e)}"
                TESTS[test_id]["output"].append(error_msg)
                output_queue.put((test_id, error_msg))
                
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
    return render_template('index.html', tests=TESTS)

@app.route('/run_test', methods=['POST'])
def run_test():
    test_id = request.form.get('test_id')
    
    if test_id not in TESTS:
        return jsonify({"status": "error", "message": "Invalid test ID"})
    
    if test_running:
        return jsonify({"status": "error", "message": "Another test is already running"})
    
    # Queue the test to run
    process_queue.put(test_id)
    
    return jsonify({"status": "success", "message": f"Running test: {TESTS[test_id]['name']}"})

@app.route('/test_status/<test_id>')
def test_status(test_id):
    if test_id not in TESTS:
        return jsonify({"status": "error", "message": "Invalid test ID"})
    
    return jsonify({
        "status": TESTS[test_id]["status"],
        "last_run": TESTS[test_id]["last_run"],
        "output": TESTS[test_id]["output"]
    })

@app.route('/stream')
def stream():
    def generate():
        while True:
            try:
                test_id, line = output_queue.get(block=False)
                yield f"data: {test_id}:{line}\n\n"
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